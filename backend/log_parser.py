# backend/log_parser.py
from pymavlink import mavutil
import os

def parse_log(filename: str):
    filepath = os.path.join("uploaded_files", filename)
    
    try:
        mlog = mavutil.mavlink_connection(filepath, dialect="ardupilotmega")
    except Exception as e:
        return {"error": f"Failed to parse log: {str(e)}"}

    data = {
        "max_altitude": None,
        "flight_time_sec": 0,
        "gps_fix_lost_time": None,
        "failsafe_events": [],
        
        # Enhanced edge case detection
        "battery_voltage_drops": [],
        "gps_loss_events": [],
        "motor_failure_indicators": [],
        "sudden_altitude_changes": [],
        "communication_losses": [],
        "emergency_events": [],
        "pre_arm_failures": [],
        "ekf_failures": [],
        "compass_errors": [],
        "vibration_warnings": [],
        
        # Flight quality metrics
        "min_battery_voltage": None,
        "max_battery_voltage": None,
        "gps_fix_quality": {"good": 0, "poor": 0, "lost": 0},
        "flight_mode_changes": [],
        "critical_warnings": 0
    }

    max_alt = 0
    min_alt = float('inf')
    first_timestamp = None
    last_timestamp = None
    last_altitude = None
    last_battery_voltage = None
    gps_fix_count = {"3d": 0, "2d": 0, "none": 0}
    last_heartbeat = None

    while True:
        msg = mlog.recv_match(blocking=False)
        if msg is None:
            break

        if not hasattr(msg, "get_type"):
            continue

        msg_type = msg.get_type()
        timestamp = getattr(msg, '_timestamp', None)

        # ALTITUDE & SUDDEN CHANGES
        if msg_type == "GPS":
            if hasattr(msg, "Alt"):
                alt = msg.Alt / 1000.0  # millimeters → meters
                max_alt = max(max_alt, alt)
                min_alt = min(min_alt, alt)
                
                # Detect sudden altitude changes (>5m/s)
                if last_altitude is not None and timestamp and last_timestamp:
                    dt = timestamp - last_timestamp
                    if dt > 0:
                        altitude_change_rate = abs(alt - last_altitude) / dt
                        if altitude_change_rate > 5.0:  # >5 m/s change
                            data["sudden_altitude_changes"].append({
                                "time": timestamp,
                                "rate": round(altitude_change_rate, 2),
                                "from_alt": round(last_altitude, 2),
                                "to_alt": round(alt, 2)
                            })
                
                last_altitude = alt

        # GPS QUALITY & LOSS DETECTION
        if msg_type == "GPS_RAW_INT":
            fix_type = getattr(msg, "fix_type", 0)
            if fix_type >= 3:
                gps_fix_count["3d"] += 1
                data["gps_fix_quality"]["good"] += 1
            elif fix_type == 2:
                gps_fix_count["2d"] += 1
                data["gps_fix_quality"]["poor"] += 1
            else:
                gps_fix_count["none"] += 1
                data["gps_fix_quality"]["lost"] += 1
                if data["gps_fix_lost_time"] is None:
                    data["gps_fix_lost_time"] = timestamp
                    data["gps_loss_events"].append({
                        "time": timestamp,
                        "fix_type": fix_type,
                        "event": "GPS fix lost"
                    })

        # BATTERY MONITORING & VOLTAGE DROPS
        if msg_type in ["BATTERY_STATUS", "SYS_STATUS", "POWER_STATUS"]:
            voltage = None
            if hasattr(msg, "voltages") and msg.voltages:
                voltage = msg.voltages[0] / 1000.0  # mV to V
            elif hasattr(msg, "voltage_battery"):
                voltage = msg.voltage_battery / 1000.0
            elif hasattr(msg, "battery_voltage"):
                voltage = msg.battery_voltage
            
            if voltage:
                if data["min_battery_voltage"] is None or voltage < data["min_battery_voltage"]:
                    data["min_battery_voltage"] = voltage
                if data["max_battery_voltage"] is None or voltage > data["max_battery_voltage"]:
                    data["max_battery_voltage"] = voltage
                
                # Detect voltage drops (>0.5V in <5 seconds)
                if last_battery_voltage and timestamp and last_timestamp:
                    dt = timestamp - last_timestamp
                    if dt < 5.0 and dt > 0:
                        voltage_drop = last_battery_voltage - voltage
                        if voltage_drop > 0.5:
                            data["battery_voltage_drops"].append({
                                "time": timestamp,
                                "drop": round(voltage_drop, 2),
                                "from_voltage": round(last_battery_voltage, 2),
                                "to_voltage": round(voltage, 2)
                            })
                
                last_battery_voltage = voltage

        # COMMUNICATION LOSS DETECTION
        if msg_type == "HEARTBEAT":
            if last_heartbeat and timestamp:
                heartbeat_gap = timestamp - last_heartbeat
                if heartbeat_gap > 5.0:  # >5 second gap
                    data["communication_losses"].append({
                        "time": timestamp,
                        "gap_seconds": round(heartbeat_gap, 1),
                        "event": "Communication gap detected"
                    })
            last_heartbeat = timestamp

        # FLIGHT MODE CHANGES & EMERGENCY EVENTS
        if msg_type == "MODE" or (msg_type == "HEARTBEAT" and hasattr(msg, "custom_mode")):
            mode_name = getattr(msg, "mode", "Unknown")
            data["flight_mode_changes"].append({
                "time": timestamp,
                "mode": mode_name
            })
            
            # Emergency modes
            emergency_modes = ["LAND", "RTL", "BRAKE", "SMART_RTL"]
            if mode_name in emergency_modes:
                data["emergency_events"].append({
                    "time": timestamp,
                    "event": f"Emergency mode: {mode_name}"
                })

        # MOTOR FAILURE INDICATORS
        if msg_type == "SERVO_OUTPUT_RAW":
            # Detect if one motor output is significantly different
            outputs = [getattr(msg, f"servo{i}_raw", 0) for i in range(1, 9)]
            active_outputs = [o for o in outputs if o > 900]
            if len(active_outputs) >= 4:
                avg_output = sum(active_outputs) / len(active_outputs)
                for i, output in enumerate(active_outputs):
                    if abs(output - avg_output) > 200:  # 200 PWM difference
                        data["motor_failure_indicators"].append({
                            "time": timestamp,
                            "motor": i + 1,
                            "output": output,
                            "average": round(avg_output),
                            "difference": round(output - avg_output)
                        })

        # STATUSTEXT MESSAGES (Errors, Warnings, Pre-arm failures)
        if msg_type == "STATUSTEXT":
            text = getattr(msg, "text", "").strip()
            severity = getattr(msg, "severity", 6)
            
            # Pre-arm failures
            if "PreArm" in text or "Pre-arm" in text:
                data["pre_arm_failures"].append({
                    "time": timestamp,
                    "message": text,
                    "severity": severity
                })
            
            # EKF failures
            elif "EKF" in text or "ekf" in text:
                data["ekf_failures"].append({
                    "time": timestamp,
                    "message": text,
                    "severity": severity
                })
            
            # Compass errors
            elif "compass" in text.lower() or "mag" in text.lower():
                data["compass_errors"].append({
                    "time": timestamp,
                    "message": text,
                    "severity": severity
                })
            
            # Vibration warnings
            elif "vib" in text.lower() or "vibrat" in text.lower():
                data["vibration_warnings"].append({
                    "time": timestamp,
                    "message": text,
                    "severity": severity
                })
            
            # Failsafe events
            elif "Failsafe" in text or "failsafe" in text:
                data["failsafe_events"].append({
                    "time": timestamp,
                    "message": text,
                    "severity": severity
                })
            
            # Critical warnings (severity <= 3)
            if severity <= 3:
                data["critical_warnings"] += 1
        
        # TIMESTAMP TRACKING
        if timestamp:
            if first_timestamp is None:
                first_timestamp = timestamp
            last_timestamp = timestamp

    # Final calculations
    data["max_altitude"] = max_alt if max_alt > 0 else 0
    data["flight_time_sec"] = (last_timestamp - first_timestamp) if first_timestamp and last_timestamp else 0
    
    # Add analysis summary
    data["edge_case_summary"] = {
        "total_anomalies": (
            len(data["battery_voltage_drops"]) +
            len(data["gps_loss_events"]) +
            len(data["motor_failure_indicators"]) +
            len(data["sudden_altitude_changes"]) +
            len(data["communication_losses"]) +
            len(data["emergency_events"]) +
            len(data["pre_arm_failures"]) +
            len(data["ekf_failures"]) +
            len(data["compass_errors"]) +
            len(data["vibration_warnings"])
        ),
        "flight_safety_score": calculate_safety_score(data),
        "detected_issues": get_detected_issues(data)
    }

    return data

def calculate_safety_score(data):
    """Calculate a safety score from 0-100 based on detected issues"""
    score = 100
    
    # Deduct points for various issues
    score -= len(data["failsafe_events"]) * 20
    score -= len(data["battery_voltage_drops"]) * 15
    score -= len(data["motor_failure_indicators"]) * 25
    score -= len(data["sudden_altitude_changes"]) * 10
    score -= len(data["gps_loss_events"]) * 15
    score -= len(data["ekf_failures"]) * 20
    score -= len(data["compass_errors"]) * 10
    score -= data["critical_warnings"] * 5
    
    return max(0, min(100, score))

def get_detected_issues(data):
    """Get a list of all detected issues for quick overview"""
    issues = []
    
    if data["failsafe_events"]:
        issues.append(f"Failsafe events: {len(data['failsafe_events'])}")
    if data["battery_voltage_drops"]:
        issues.append(f"Battery voltage drops: {len(data['battery_voltage_drops'])}")
    if data["motor_failure_indicators"]:
        issues.append(f"Motor issues: {len(data['motor_failure_indicators'])}")
    if data["gps_loss_events"]:
        issues.append(f"GPS loss events: {len(data['gps_loss_events'])}")
    if data["sudden_altitude_changes"]:
        issues.append(f"Sudden altitude changes: {len(data['sudden_altitude_changes'])}")
    if data["emergency_events"]:
        issues.append(f"Emergency mode activations: {len(data['emergency_events'])}")
    if data["pre_arm_failures"]:
        issues.append(f"Pre-arm failures: {len(data['pre_arm_failures'])}")
    if data["ekf_failures"]:
        issues.append(f"EKF failures: {len(data['ekf_failures'])}")
    if data["compass_errors"]:
        issues.append(f"Compass errors: {len(data['compass_errors'])}")
    if data["vibration_warnings"]:
        issues.append(f"Vibration warnings: {len(data['vibration_warnings'])}")
    
    return issues if issues else ["No major issues detected"]
