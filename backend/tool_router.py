# tool_router.py

from mcp_logger import log_pattern_match

from tools import (
    get_max_altitude,
    detect_gps_loss,
    check_battery_health,
    summarize_warnings,
    get_flight_time,
    detect_altitude_fluctuations,
    check_vibration_levels,
    detect_failsafe_triggers,
    get_mode_changes,
    analyze_current_draw,
    detect_unarmed_takeoff,
    evaluate_rc_signal_health,
    summarize_autotune
)

def route_tool(question: str):
    q_lower = question.lower()
    matched_tool = None

    # Flight time and duration
    if any(phrase in q_lower for phrase in ["flight time", "duration", "how long"]):
        matched_tool = "get_flight_time"

    # Altitude related
    elif "max altitude" in q_lower:
        matched_tool = "get_max_altitude"
    elif any(phrase in q_lower for phrase in ["altitude fluctuation", "altitude change", "altitude variation"]):
        matched_tool = "detect_altitude_fluctuations"

    # GPS related
    elif "gps" in q_lower and ("loss" in q_lower or "issue" in q_lower or "anomal" in q_lower):
        matched_tool = "detect_gps_loss"

    # Battery and power related
    elif "battery" in q_lower:
        matched_tool = "check_battery_health"
    elif any(phrase in q_lower for phrase in ["current", "amp", "power draw"]):
        matched_tool = "analyze_current_draw"

    # Warnings and failsafes
    elif "warning" in q_lower or "error" in q_lower:
        matched_tool = "summarize_warnings"
    elif "failsafe" in q_lower:
        matched_tool = "detect_failsafe_triggers"

    # Flight modes
    elif any(phrase in q_lower for phrase in ["mode", "flight mode", "mode change"]):
        matched_tool = "get_mode_changes"

    # RC signal
    elif any(phrase in q_lower for phrase in ["rc", "signal", "radio", "control"]):
        matched_tool = "evaluate_rc_signal_health"

    # Vibration and stability
    elif any(phrase in q_lower for phrase in ["vibration", "shake", "stability"]):
        matched_tool = "check_vibration_levels"

    # Safety checks
    elif "unarmed" in q_lower and "takeoff" in q_lower:
        matched_tool = "detect_unarmed_takeoff"
    elif "autotune" in q_lower:
        matched_tool = "summarize_autotune"

    # Log the pattern match if a tool was found
    if matched_tool:
        log_pattern_match(question, matched_tool)

    return matched_tool

def route_tool_call(question: str, log_dict: dict) -> str | None:
    q = question.lower()

    if "max altitude" in q or "highest altitude" in q:
        return get_max_altitude(log_dict)

    elif "gps" in q or "gps loss" in q or "no gps" in q:
        return detect_gps_loss(log_dict)

    elif "battery" in q or "voltage" in q or "power" in q:
        return check_battery_health(log_dict)

    elif "warning" in q or "error" in q or "failsafe" in q:
        return summarize_warnings(log_dict)

    return None  # fallback to LLM
