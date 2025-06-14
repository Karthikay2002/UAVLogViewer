from functools import lru_cache
from pymavlink import mavutil
import pandas as pd
import os

WANTED = {
    "GPS": ["Lat", "Lon", "Alt", "NSats", "HDop"],
    "ATT": ["Pitch", "Roll", "Yaw"],
    "CTUN": ["Alt", "NavRoll", "ThrOut"],
    "EV":  ["Id"],                      # Event messages (failsafes, errors)
    "ERR": ["Subsys", "ECode"],         # ArduPilot error codes
    "BAT": ["Volt", "Curr"],
    "CURR": ["Volt", "Curr"],
    "PM":  ["Volt1", "Curr1"],
    "POWR": ["Vcc"],
    "RCIN": ["C3"],                     # throttle input
    "RCOUT": ["C1", "C2", "C3", "C4"],  # motor outputs
}

@lru_cache(maxsize=32)
def load_log(path: str) -> dict:
    """Parse .BIN/.LOG once, memoise in RAM."""
    mav = mavutil.mavlink_connection(path, dialect="ardupilotmega", quiet=True)
    frames = {k: [] for k in WANTED}
    first_ts, last_ts = None, None
    altitude_series = []
    
    while True:
        msg = mav.recv_match(blocking=False)
        if msg is None:
            break
            
        mtype = msg.get_type()
        
        # Extract timestamps
        if hasattr(msg, '_timestamp'):
            ts = getattr(msg, '_timestamp')
            if first_ts is None:
                first_ts = ts
            last_ts = ts
        
        # Extract altitude data from GPS and CTUN messages
        if mtype == "GPS" and hasattr(msg, "Alt"):
            altitude_series.append(msg.Alt / 100.0)  # Convert cm to meters
        elif mtype == "CTUN" and hasattr(msg, "Alt"):
            altitude_series.append(msg.Alt)  # Already in meters
            
        # Collect other message types
        if mtype in WANTED:
            row = {}
            for field in WANTED[mtype]:
                row[field] = getattr(msg, field, None)
            frames[mtype].append(row)
    
    # Convert lists to DataFrames (empty → None)
    out = {k: (pd.DataFrame(v) if v else None) for k, v in frames.items()}
    
    # Add extracted data
    out['_first_timestamp'] = first_ts
    out['_last_timestamp'] = last_ts
    out['altitude_series'] = altitude_series
    
    return out 