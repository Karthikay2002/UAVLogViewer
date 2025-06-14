def detect_battery_failsafe(log):
    ev = log.get("EV")
    if ev is not None and "Id" in ev and (ev["Id"] == 10).any():  # 10 == BAT_FS_LOW
        return True
    # fallback: voltage < 10.5 V during flight
    for df, col in [(log.get("BAT"), "Volt"), (log.get("CURR"), "Volt"), (log.get("PM"), "Volt1")]:
        if df is not None and col in df and (df[col] < 1050).any():  # centivolts or millivolts
            return True
    return False

def detect_motor_failure(log):
    rc_out = log.get("RCOUT")
    ctun = log.get("CTUN")
    if rc_out is None or ctun is None:
        return False
    # large commanded throttle (ThrOut) but low motor outputs
    if "ThrOut" in ctun and all(c in rc_out for c in ["C1", "C2", "C3", "C4"]):
        high_thr = ctun["ThrOut"] > 700
        low_out = rc_out[["C1", "C2", "C3", "C4"]].max(axis=1) < 300
        return bool((high_thr & low_out).sum() > 20)
    return False

def gps_lock_lost(log):
    gps = log.get("GPS")
    return bool((gps["NSats"] < 4).any()) if gps is not None and "NSats" in gps else False 