import functools
import json
import os
from datetime import datetime
from typing import Callable, Any

# MCP logging configuration
MCP_LOG_DIR = "mcp_logs"
os.makedirs(MCP_LOG_DIR, exist_ok=True)

def log_tool_usage(func: Callable) -> Callable:
    """Decorator to log tool usage and performance."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": func.__name__,
            "execution_time_ms": (end_time - start_time).total_seconds() * 1000,
            "success": result is not None,
            "input_args": str(args),
            "input_kwargs": str(kwargs)
        }
        
        # Log to file
        log_file = os.path.join(MCP_LOG_DIR, f"tool_usage_{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        return result
    return wrapper

def log_pattern_match(question: str, matched_tool: str, confidence: float = 1.0):
    """Log pattern matching results for analysis."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "matched_tool": matched_tool,
        "confidence": confidence
    }
    
    log_file = os.path.join(MCP_LOG_DIR, f"pattern_matches_{datetime.now().strftime('%Y%m%d')}.jsonl")
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def analyze_tool_usage(days: int = 7) -> dict:
    """Analyze tool usage patterns from logs."""
    usage_stats = {}
    pattern_stats = {}
    
    # Get log files for the specified period
    today = datetime.now()
    for i in range(days):
        date = (today - timedelta(days=i)).strftime('%Y%m%d')
        tool_log = os.path.join(MCP_LOG_DIR, f"tool_usage_{date}.jsonl")
        pattern_log = os.path.join(MCP_LOG_DIR, f"pattern_matches_{date}.jsonl")
        
        # Analyze tool usage
        if os.path.exists(tool_log):
            with open(tool_log) as f:
                for line in f:
                    entry = json.loads(line)
                    tool = entry["tool_name"]
                    usage_stats[tool] = usage_stats.get(tool, 0) + 1
        
        # Analyze pattern matches
        if os.path.exists(pattern_log):
            with open(pattern_log) as f:
                for line in f:
                    entry = json.loads(line)
                    tool = entry["matched_tool"]
                    pattern_stats[tool] = pattern_stats.get(tool, 0) + 1
    
    return {
        "tool_usage": usage_stats,
        "pattern_matches": pattern_stats
    } 