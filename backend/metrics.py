import numpy as np

def max_altitude(log):
    # Use the new altitude_series from telemetry parser
    altitude_series = log.get("altitude_series", [])
    if altitude_series:
        return float(max(altitude_series))
    
    # Fallback to old method
    gps = log.get("GPS")
    if gps is not None and "Alt" in gps:
        return float(gps["Alt"].max())
    att = log.get("ATT")
    if att is not None and "Alt" in att:
        return float(att["Alt"].max())
    raise ValueError("No altitude data")

def flight_duration(log):
    first, last = log.get("_first_timestamp"), log.get("_last_timestamp")
    if first is not None and last is not None:
        return last - first
    raise ValueError("No timestamp data")

def battery_stats(log):
    bat = log.get("BAT")
    curr = log.get("CURR")
    pm = log.get("PM")
    powr = log.get("POWR")
    volts = []
    for df, col in [(bat, "Volt"), (curr, "Volt"), (pm, "Volt1"), (powr, "Vcc")]:
        if df is not None and col in df:
            volts.extend(df[col].dropna().tolist())
    if not volts:
        raise ValueError("Battery voltage data missing")
    return {
        "volts_max": float(np.max(volts)),
        "volts_min": float(np.min(volts)),
        "volts_mean": float(np.mean(volts)),
    } 