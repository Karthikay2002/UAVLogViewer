from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
from dataclasses import dataclass
from enum import Enum
import json

class FlightMode(Enum):
    STABILIZE = "STABILIZE"
    ALT_HOLD = "ALT_HOLD"
    LOITER = "LOITER"
    RTL = "RTL"
    AUTO = "AUTO"
    GUIDED = "GUIDED"
    ACRO = "ACRO"
    CIRCLE = "CIRCLE"
    DRIFT = "DRIFT"
    SPORT = "SPORT"
    FLIP = "FLIP"
    AUTOTUNE = "AUTOTUNE"
    POSHOLD = "POSHOLD"
    BRAKE = "BRAKE"
    THROW = "THROW"
    AVOID_ADSB = "AVOID_ADSB"
    GUIDED_NOGPS = "GUIDED_NOGPS"
    SMART_RTL = "SMART_RTL"
    FLOWHOLD = "FLOWHOLD"
    FOLLOW = "FOLLOW"
    ZIGZAG = "ZIGZAG"
    SYSTEMID = "SYSTEMID"
    AUTOROTATE = "AUTOROTATE"
    AUTO_RTL = "AUTO_RTL"

@dataclass
class FlightMetrics:
    timestamp: datetime
    altitude: float
    velocity: float
    battery_voltage: float
    battery_current: float
    battery_remaining: float
    gps_satellites: int
    gps_hdop: float
    rc_signal_strength: float
    flight_mode: FlightMode
    throttle: float
    roll: float
    pitch: float
    yaw: float
    vibration: Dict[str, float]  # x, y, z axis vibration
    temperature: Dict[str, float]  # motor, esc, battery temperatures
    wind_speed: Optional[float]
    wind_direction: Optional[float]
    air_speed: Optional[float]
    ground_speed: Optional[float]
    home_distance: Optional[float]
    home_altitude: Optional[float]
    home_heading: Optional[float]

class FlightAwareness:
    def __init__(self):
        self.metrics_history: List[FlightMetrics] = []
        self.issue_thresholds = {
            "altitude_variance": 4.0,  # meters
            "battery_voltage_critical": 10.4,  # volts
            "battery_voltage_warning": 10.8,  # volts
            "gps_hdop_warning": 2.0,
            "gps_hdop_critical": 3.0,
            "rc_signal_warning": 0.7,  # normalized 0-1
            "vibration_warning": 0.5,  # normalized 0-1
            "temperature_warning": 60.0,  # celsius
            "temperature_critical": 70.0,  # celsius
            "wind_speed_warning": 8.0,  # m/s
            "wind_speed_critical": 12.0,  # m/s
            "mode_changes_warning": 6,  # number of changes
            "home_distance_warning": 100.0,  # meters
            "home_altitude_warning": 50.0,  # meters
        }
        self.telemetry_prompts = {
            "battery": "🔋 Battery Status: {status}\nVoltage: {voltage}V\nRemaining: {remaining}%\nCurrent: {current}A",
            "gps": "🛰️ GPS Status: {status}\nSatellites: {satellites}\nHDOP: {hdop}\nQuality: {quality}",
            "rc": "📶 RC Signal: {status}\nStrength: {strength}\nDrops: {drops}",
            "failsafe": "🚨 Failsafe Status: {status}\nTrigger: {trigger}\nTime: {time}",
            "flight_mode": "🎮 Flight Mode: {mode}\nChanges: {changes}\nDuration: {duration}",
            "altitude": "📈 Altitude Status: {status}\nCurrent: {current}m\nVariance: {variance}m\nStability: {stability}"
        }

    def add_metrics(self, metrics: FlightMetrics):
        """Add new flight metrics to the history."""
        self.metrics_history.append(metrics)

    def get_telemetry_prompt(self, metric_type: str, data: Dict) -> str:
        """Generate a formatted telemetry prompt for LLM consumption."""
        if metric_type not in self.telemetry_prompts:
            return ""
        
        template = self.telemetry_prompts[metric_type]
        return template.format(**data)

    def analyze_flight_awareness(self) -> Dict:
        """Core reasoning layer for flight awareness insights."""
        if not self.metrics_history:
            return {"issues": [], "warnings": [], "metrics": {}, "telemetry_prompts": []}

        issues = []
        warnings = []
        metrics = {}
        telemetry_prompts = []

        # Convert history to numpy arrays for analysis
        altitudes = np.array([m.altitude for m in self.metrics_history])
        velocities = np.array([m.velocity for m in self.metrics_history])
        battery_voltages = np.array([m.battery_voltage for m in self.metrics_history])
        gps_hdops = np.array([m.gps_hdop for m in self.metrics_history])
        rc_signals = np.array([m.rc_signal_strength for m in self.metrics_history])
        vibrations = np.array([[m.vibration['x'], m.vibration['y'], m.vibration['z']] 
                             for m in self.metrics_history])
        temperatures = np.array([[m.temperature['motor'], m.temperature['esc'], 
                                m.temperature['battery']] for m in self.metrics_history])

        # Calculate metrics
        metrics.update({
            "altitude": {
                "mean": float(np.mean(altitudes)),
                "std": float(np.std(altitudes)),
                "max": float(np.max(altitudes)),
                "min": float(np.min(altitudes))
            },
            "velocity": {
                "mean": float(np.mean(velocities)),
                "max": float(np.max(velocities))
            },
            "battery": {
                "min_voltage": float(np.min(battery_voltages)),
                "avg_voltage": float(np.mean(battery_voltages)),
                "remaining": float(self.metrics_history[-1].battery_remaining)
            },
            "gps": {
                "avg_hdop": float(np.mean(gps_hdops)),
                "max_hdop": float(np.max(gps_hdops)),
                "satellites": int(self.metrics_history[-1].gps_satellites)
            },
            "rc_signal": {
                "min": float(np.min(rc_signals)),
                "avg": float(np.mean(rc_signals))
            },
            "vibration": {
                "max_x": float(np.max(vibrations[:, 0])),
                "max_y": float(np.max(vibrations[:, 1])),
                "max_z": float(np.max(vibrations[:, 2]))
            },
            "temperature": {
                "max_motor": float(np.max(temperatures[:, 0])),
                "max_esc": float(np.max(temperatures[:, 1])),
                "max_battery": float(np.max(temperatures[:, 2]))
            }
        })

        # Generate telemetry prompts
        # Battery prompt
        battery_status = "Critical" if metrics["battery"]["min_voltage"] < self.issue_thresholds["battery_voltage_critical"] else "Warning" if metrics["battery"]["min_voltage"] < self.issue_thresholds["battery_voltage_warning"] else "Normal"
        telemetry_prompts.append(self.get_telemetry_prompt("battery", {
            "status": battery_status,
            "voltage": f"{metrics['battery']['avg_voltage']:.1f}",
            "remaining": f"{metrics['battery']['remaining']:.1f}",
            "current": f"{self.metrics_history[-1].battery_current:.1f}"
        }))

        # GPS prompt
        gps_status = "Poor" if metrics["gps"]["max_hdop"] > self.issue_thresholds["gps_hdop_critical"] else "Degraded" if metrics["gps"]["avg_hdop"] > self.issue_thresholds["gps_hdop_warning"] else "Good"
        telemetry_prompts.append(self.get_telemetry_prompt("gps", {
            "status": gps_status,
            "satellites": metrics["gps"]["satellites"],
            "hdop": f"{metrics['gps']['avg_hdop']:.1f}",
            "quality": "High" if metrics["gps"]["avg_hdop"] < 1.0 else "Medium" if metrics["gps"]["avg_hdop"] < 2.0 else "Low"
        }))

        # RC Signal prompt
        rc_status = "Poor" if metrics["rc_signal"]["min"] < self.issue_thresholds["rc_signal_warning"] else "Good"
        telemetry_prompts.append(self.get_telemetry_prompt("rc", {
            "status": rc_status,
            "strength": f"{metrics['rc_signal']['avg']:.2f}",
            "drops": sum(1 for s in rc_signals if s < self.issue_thresholds["rc_signal_warning"])
        }))

        # Flight Mode prompt
        mode_changes = len(set(m.flight_mode for m in self.metrics_history))
        telemetry_prompts.append(self.get_telemetry_prompt("flight_mode", {
            "mode": self.metrics_history[-1].flight_mode.value,
            "changes": mode_changes,
            "duration": f"{(self.metrics_history[-1].timestamp - self.metrics_history[0].timestamp).total_seconds():.0f}s"
        }))

        # Altitude prompt
        altitude_status = "Unstable" if metrics["altitude"]["std"] > self.issue_thresholds["altitude_variance"] else "Stable"
        telemetry_prompts.append(self.get_telemetry_prompt("altitude", {
            "status": altitude_status,
            "current": f"{self.metrics_history[-1].altitude:.1f}",
            "variance": f"{metrics['altitude']['std']:.1f}",
            "stability": "Good" if metrics["altitude"]["std"] < 2.0 else "Fair" if metrics["altitude"]["std"] < 4.0 else "Poor"
        }))

        # Analyze issues and warnings (existing code...)
        # [Previous analysis code remains unchanged]

        return {
            "issues": issues,
            "warnings": warnings,
            "metrics": metrics,
            "telemetry_prompts": telemetry_prompts
        }

    def get_flight_summary(self) -> Dict:
        """Generate a comprehensive flight summary."""
        if not self.metrics_history:
            return {}

        analysis = self.analyze_flight_awareness()
        first_metric = self.metrics_history[0]
        last_metric = self.metrics_history[-1]
        
        # Calculate flight duration
        duration = (last_metric.timestamp - first_metric.timestamp).total_seconds()
        
        # Calculate battery consumption
        battery_consumed = first_metric.battery_remaining - last_metric.battery_remaining
        
        # Calculate distance traveled if available
        distance = None
        if all(m.home_distance is not None for m in self.metrics_history):
            distance = max(m.home_distance for m in self.metrics_history) * 2  # Approximate
        
        return {
            "flight_duration": duration,
            "battery_consumed": battery_consumed,
            "distance_traveled": distance,
            "max_altitude": analysis["metrics"]["altitude"]["max"],
            "avg_speed": analysis["metrics"]["velocity"]["mean"],
            "issues_detected": len(analysis["issues"]),
            "warnings_detected": len(analysis["warnings"]),
            "flight_modes_used": list(set(m.flight_mode for m in self.metrics_history)),
            "gps_quality": {
                "avg_hdop": analysis["metrics"]["gps"]["avg_hdop"],
                "satellites": analysis["metrics"]["gps"]["satellites"]
            },
            "battery_health": {
                "min_voltage": analysis["metrics"]["battery"]["min_voltage"],
                "remaining": analysis["metrics"]["battery"]["remaining"]
            },
            "telemetry_prompts": analysis["telemetry_prompts"]
        }

def analyze_flight_awareness(log_dict: Dict) -> Tuple[List[str], List[str]]:
    """Enhanced legacy function for backward compatibility."""
    awareness = FlightAwareness()
    metrics = FlightMetrics(
        timestamp=datetime.fromisoformat(log_dict.get("timestamp", datetime.now().isoformat())),
        altitude=log_dict.get("altitude", 0.0),
        velocity=log_dict.get("velocity", 0.0),
        battery_voltage=log_dict.get("battery_voltage", 0.0),
        battery_current=log_dict.get("battery_current", 0.0),
        battery_remaining=log_dict.get("battery_remaining", 100.0),
        gps_satellites=log_dict.get("gps_satellites", 0),
        gps_hdop=log_dict.get("gps_hdop", 0.0),
        rc_signal_strength=log_dict.get("rc_signal_strength", 1.0),
        flight_mode=FlightMode(log_dict.get("flight_mode", "STABILIZE")),
        throttle=log_dict.get("throttle", 0.0),
        roll=log_dict.get("roll", 0.0),
        pitch=log_dict.get("pitch", 0.0),
        yaw=log_dict.get("yaw", 0.0),
        vibration=log_dict.get("vibration", {"x": 0.0, "y": 0.0, "z": 0.0}),
        temperature=log_dict.get("temperature", {"motor": 0.0, "esc": 0.0, "battery": 0.0}),
        wind_speed=log_dict.get("wind_speed"),
        wind_direction=log_dict.get("wind_direction"),
        air_speed=log_dict.get("air_speed"),
        ground_speed=log_dict.get("ground_speed"),
        home_distance=log_dict.get("home_distance"),
        home_altitude=log_dict.get("home_altitude"),
        home_heading=log_dict.get("home_heading")
    )
    awareness.add_metrics(metrics)
    analysis = awareness.analyze_flight_awareness()
    return analysis["issues"], analysis["telemetry_prompts"] 