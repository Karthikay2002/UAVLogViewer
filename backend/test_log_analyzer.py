import json
import os
from datetime import datetime, timedelta
import random
from log_analyzer import LogAnalyzer

def generate_sample_logs():
    """Generate sample log data for testing."""
    log_dir = "mcp_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Sample tools and their success rates
    tools = [
        "get_max_altitude",
        "detect_gps_loss",
        "check_battery_health",
        "summarize_warnings",
        "get_flight_time",
        "detect_altitude_fluctuations",
        "check_vibration_levels"
    ]
    
    # Generate tool usage logs
    tool_log = os.path.join(log_dir, f"tool_usage_{datetime.now().strftime('%Y%m%d')}.jsonl")
    with open(tool_log, "w") as f:
        for _ in range(100):  # Generate 100 log entries
            tool = random.choice(tools)
            timestamp = datetime.now() - timedelta(
                hours=random.randint(0, 24),
                minutes=random.randint(0, 60)
            )
            
            log_entry = {
                "timestamp": timestamp.isoformat(),
                "tool_name": tool,
                "execution_time_ms": random.randint(50, 2000),
                "success": random.random() > 0.1,  # 90% success rate
                "input_args": f"log_{random.randint(1, 1000)}",
                "input_kwargs": "{}"
            }
            f.write(json.dumps(log_entry) + "\n")
    
    # Generate pattern match logs
    pattern_log = os.path.join(log_dir, f"pattern_matches_{datetime.now().strftime('%Y%m%d')}.jsonl")
    with open(pattern_log, "w") as f:
        questions = [
            "What was the maximum altitude?",
            "Did we lose GPS signal?",
            "How's the battery looking?",
            "Any warnings during flight?",
            "How long was the flight?",
            "Were there altitude fluctuations?",
            "Check vibration levels"
        ]
        
        for _ in range(50):  # Generate 50 pattern matches
            question = random.choice(questions)
            tool = random.choice(tools)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "matched_tool": tool,
                "confidence": random.uniform(0.7, 1.0)
            }
            f.write(json.dumps(log_entry) + "\n")

def main():
    # Generate sample logs
    print("Generating sample log data...")
    generate_sample_logs()
    
    # Initialize analyzer
    print("\nInitializing log analyzer...")
    analyzer = LogAnalyzer()
    
    # Load logs
    print("Loading logs...")
    analyzer.load_recent_logs()
    
    # Generate and print basic report
    print("\n=== Basic Usage Report ===")
    print(analyzer.generate_usage_report())
    
    # Get error analysis
    print("\n=== Error Analysis ===")
    error_stats = analyzer.analyze_error_patterns()
    print(f"Total errors: {error_stats['total_errors']}")
    print("\nErrors by tool:")
    for tool, count in error_stats["error_by_tool"].items():
        print(f"- {tool}: {count} errors")
    
    # Get time trends
    print("\n=== Time Trends ===")
    time_trends = analyzer.analyze_time_trends()
    print("\nPeak usage hours:")
    for hour, count in sorted(time_trends["hourly_distribution"].items()):
        print(f"- Hour {hour}: {count} calls")
    
    # Export analysis
    print("\n=== Exporting Analysis ===")
    output_dir = "analysis_reports"
    result = analyzer.export_analysis(output_dir)
    print(result)
    
    # Get advanced suggestions
    print("\n=== Advanced Suggestions ===")
    suggestions = analyzer.get_advanced_suggestions()
    for suggestion in suggestions:
        print(f"- {suggestion}")
    
    print("\nAnalysis complete! Check the 'analysis_reports' directory for detailed reports and visualizations.")

if __name__ == "__main__":
    main() 