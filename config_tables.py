# Simplified config tables for PX4 log downloader
# Based on ArduPilot flight modes and error labels

# Flight modes mapping (mode_id -> (mode_name, description))
flight_modes_table = {
    0: ("STABILIZE", "Stabilize mode"),
    1: ("ACRO", "Acrobatic mode"),
    2: ("ALT_HOLD", "Altitude hold mode"),
    3: ("AUTO", "Auto mode"),
    4: ("GUIDED", "Guided mode"),
    5: ("LOITER", "Loiter mode"),
    6: ("RTL", "Return to launch"),
    7: ("CIRCLE", "Circle mode"),
    8: ("POSITION", "Position mode"),
    9: ("LAND", "Land mode"),
    10: ("OF_LOITER", "Optical flow loiter"),
    11: ("DRIFT", "Drift mode"),
    13: ("SPORT", "Sport mode"),
    14: ("FLIP", "Flip mode"),
    15: ("AUTOTUNE", "Auto tune mode"),
    16: ("POSHOLD", "Position hold"),
    17: ("BRAKE", "Brake mode"),
    18: ("THROW", "Throw mode"),
    19: ("AVOID_ADSB", "ADSB avoidance"),
    20: ("GUIDED_NOGPS", "Guided no GPS"),
    21: ("SMART_RTL", "Smart RTL"),
    22: ("FLOWHOLD", "Flow hold"),
    23: ("FOLLOW", "Follow mode"),
    24: ("ZIGZAG", "Zigzag mode"),
    25: ("SYSTEMID", "System ID"),
    26: ("AUTOROTATE", "Autorotate"),
    27: ("AUTO_RTL", "Auto RTL")
}

# Error labels mapping (error_id -> error_label)
error_labels_table = {
    1: "Vibration",
    2: "GPS Glitch", 
    3: "Compass Error",
    4: "Battery Low",
    5: "Radio Failsafe",
    6: "EKF Error",
    7: "Barometer Error",
    8: "Motor Failure",
    9: "Crash Detected",
    10: "Fence Breach",
    11: "Terrain Error",
    12: "Navigation Error",
    13: "Sensor Error",
    14: "Temperature Error",
    15: "Power Error"
} 