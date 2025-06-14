import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import csv
from pathlib import Path
from fastapi import APIRouter
from backend.flight_awareness import analyze_flight_awareness

class LogAnalyzer:
    def __init__(self, log_dir: str = "mcp_logs"):
        self.log_dir = log_dir
        self.tool_usage_data = []
        self.pattern_match_data = []
        self.error_patterns = defaultdict(int)
        self.flight_awareness_data = []

    def load_recent_logs(self, days: int = 7):
        """Load recent log data into memory."""
        today = datetime.now()
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y%m%d')
            
            # Load tool usage logs
            tool_log = os.path.join(self.log_dir, f"tool_usage_{date}.jsonl")
            if os.path.exists(tool_log):
                with open(tool_log) as f:
                    for line in f:
                        self.tool_usage_data.append(json.loads(line))
            
            # Load pattern match logs
            pattern_log = os.path.join(self.log_dir, f"pattern_matches_{date}.jsonl")
            if os.path.exists(pattern_log):
                with open(pattern_log) as f:
                    for line in f:
                        self.pattern_match_data.append(json.loads(line))
            
            # Load flight awareness logs
            flight_log = os.path.join(self.log_dir, f"flight_awareness_{date}.jsonl")
            if os.path.exists(flight_log):
                with open(flight_log) as f:
                    for line in f:
                        self.flight_awareness_data.append(json.loads(line))

    def get_tool_usage_stats(self) -> Dict:
        """Get statistics about tool usage."""
        stats = {
            "total_calls": len(self.tool_usage_data),
            "success_rate": 0,
            "avg_execution_time": 0,
            "tool_frequency": defaultdict(int),
            "hourly_usage": defaultdict(int)
        }
        
        if not self.tool_usage_data:
            return stats

        success_count = 0
        total_time = 0
        
        for entry in self.tool_usage_data:
            # Count successes
            if entry["success"]:
                success_count += 1
            
            # Track execution time
            total_time += entry["execution_time_ms"]
            
            # Count tool frequency
            stats["tool_frequency"][entry["tool_name"]] += 1
            
            # Track hourly usage
            hour = datetime.fromisoformat(entry["timestamp"]).hour
            stats["hourly_usage"][hour] += 1
        
        stats["success_rate"] = (success_count / len(self.tool_usage_data)) * 100
        stats["avg_execution_time"] = total_time / len(self.tool_usage_data)
        
        return stats

    def get_pattern_match_stats(self) -> Dict:
        """Get statistics about pattern matching."""
        stats = {
            "total_matches": len(self.pattern_match_data),
            "tool_matches": defaultdict(int),
            "common_phrases": defaultdict(int)
        }
        
        if not self.pattern_match_data:
            return stats

        for entry in self.pattern_match_data:
            # Count tool matches
            stats["tool_matches"][entry["matched_tool"]] += 1
            
            # Extract and count common phrases
            words = entry["question"].lower().split()
            for word in words:
                if len(word) > 3:  # Ignore short words
                    stats["common_phrases"][word] += 1
        
        return stats

    def analyze_flight_awareness(self) -> Dict:
        """Analyze flight awareness data and generate insights."""
        if not self.flight_awareness_data:
            return {}
            
        df = pd.DataFrame(self.flight_awareness_data)
        
        # Calculate statistics for each metric
        stats = {
            "altitude_issues": len(df[df["altitude_variance"] > 4]),
            "battery_issues": len(df[df["min_battery_voltage"] < 10.4]),
            "gps_issues": df["gps_glitches"].sum(),
            "rc_signal_issues": df["rc_signal_drops"].sum(),
            "mode_transition_issues": len(df[df["mode_changes"].apply(len) > 6]),
            "failsafe_events": len(df[df["failsafe_events"].notna()])
        }
        
        # Calculate hourly distribution of issues
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        hourly_issues = df.groupby(df["timestamp"].dt.hour).agg({
            "altitude_variance": lambda x: (x > 4).sum(),
            "min_battery_voltage": lambda x: (x < 10.4).sum(),
            "gps_glitches": "sum",
            "rc_signal_drops": "sum",
            "mode_changes": lambda x: (x.apply(len) > 6).sum(),
            "failsafe_events": lambda x: x.notna().sum()
        }).to_dict()
        
        return {
            "total_issues": sum(stats.values()),
            "issue_breakdown": stats,
            "hourly_distribution": hourly_issues
        }

    def plot_flight_awareness(self, save_path: str = None):
        """Generate flight awareness visualizations."""
        if not self.flight_awareness_data:
            return
            
        df = pd.DataFrame(self.flight_awareness_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Issue Distribution
        issues = self.analyze_flight_awareness()["issue_breakdown"]
        ax1.bar(issues.keys(), issues.values())
        ax1.set_title("Distribution of Flight Issues")
        ax1.set_xticklabels(issues.keys(), rotation=45)
        ax1.set_ylabel("Number of Issues")
        
        # Plot 2: Hourly Issue Distribution
        hourly = self.analyze_flight_awareness()["hourly_distribution"]
        for issue_type, counts in hourly.items():
            ax2.plot(range(24), counts, label=issue_type)
        ax2.set_title("Hourly Distribution of Issues")
        ax2.set_xlabel("Hour of Day")
        ax2.set_ylabel("Number of Issues")
        ax2.legend()
        
        # Plot 3: Battery Voltage Over Time
        ax3.plot(df["timestamp"], df["min_battery_voltage"])
        ax3.axhline(y=10.4, color='r', linestyle='--', label='Warning Threshold')
        ax3.set_title("Battery Voltage Over Time")
        ax3.set_xlabel("Time")
        ax3.set_ylabel("Voltage (V)")
        ax3.legend()
        
        # Plot 4: GPS and RC Signal Issues
        ax4.plot(df["timestamp"], df["gps_glitches"], label="GPS Glitches")
        ax4.plot(df["timestamp"], df["rc_signal_drops"], label="RC Signal Drops")
        ax4.set_title("GPS and RC Signal Issues")
        ax4.set_xlabel("Time")
        ax4.set_ylabel("Number of Issues")
        ax4.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

    def generate_usage_report(self) -> str:
        """Generate a human-readable usage report."""
        tool_stats = self.get_tool_usage_stats()
        pattern_stats = self.get_pattern_match_stats()
        flight_stats = self.analyze_flight_awareness()
        
        report = [
            "=== Tool Usage Report ===",
            f"Total Tool Calls: {tool_stats['total_calls']}",
            f"Success Rate: {tool_stats['success_rate']:.1f}%",
            f"Average Execution Time: {tool_stats['avg_execution_time']:.2f}ms",
            "\nMost Used Tools:",
        ]
        
        # Add top 5 most used tools
        sorted_tools = sorted(tool_stats["tool_frequency"].items(), 
                            key=lambda x: x[1], reverse=True)[:5]
        for tool, count in sorted_tools:
            report.append(f"- {tool}: {count} calls")
        
        report.extend([
            "\n=== Pattern Matching Report ===",
            f"Total Pattern Matches: {pattern_stats['total_matches']}",
            "\nMost Common Tool Matches:",
        ])
        
        # Add top 5 most matched tools
        sorted_matches = sorted(pattern_stats["tool_matches"].items(), 
                              key=lambda x: x[1], reverse=True)[:5]
        for tool, count in sorted_matches:
            report.append(f"- {tool}: {count} matches")
        
        # Add flight awareness report
        if flight_stats:
            report.extend([
                "\n=== Flight Awareness Report ===",
                f"Total Issues Detected: {flight_stats['total_issues']}",
                "\nIssue Breakdown:",
            ])
            for issue, count in flight_stats["issue_breakdown"].items():
                report.append(f"- {issue}: {count} occurrences")
        
        return "\n".join(report)

    def plot_usage_trends(self, save_path: str = None):
        """Generate plots of usage trends."""
        if not self.tool_usage_data:
            return
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(self.tool_usage_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot 1: Tool usage over time
        df.groupby('tool_name').size().plot(kind='bar', ax=ax1)
        ax1.set_title('Tool Usage Frequency')
        ax1.set_ylabel('Number of Calls')
        
        # Plot 2: Success rate by tool
        success_rate = df.groupby('tool_name')['success'].mean() * 100
        success_rate.plot(kind='bar', ax=ax2)
        ax2.set_title('Success Rate by Tool')
        ax2.set_ylabel('Success Rate (%)')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

    def plot_time_trends(self, save_path: str = None):
        """Generate time-based trend visualizations."""
        if not self.tool_usage_data:
            return
            
        df = pd.DataFrame(self.tool_usage_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Plot 1: Hourly distribution
        df.groupby(df['timestamp'].dt.hour).size().plot(kind='bar', ax=ax1)
        ax1.set_title('Usage by Hour')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Number of Calls')
        
        # Plot 2: Daily distribution
        df.groupby(df['timestamp'].dt.day_name()).size().plot(kind='bar', ax=ax2)
        ax2.set_title('Usage by Day')
        ax2.set_xlabel('Day of Week')
        ax2.set_ylabel('Number of Calls')
        
        # Plot 3: Response time by hour
        df.groupby(df['timestamp'].dt.hour)['execution_time_ms'].mean().plot(kind='line', ax=ax3)
        ax3.set_title('Average Response Time by Hour')
        ax3.set_xlabel('Hour of Day')
        ax3.set_ylabel('Response Time (ms)')
        
        # Plot 4: Success rate by hour
        df.groupby(df['timestamp'].dt.hour)['success'].mean().plot(kind='line', ax=ax4)
        ax4.set_title('Success Rate by Hour')
        ax4.set_xlabel('Hour of Day')
        ax4.set_ylabel('Success Rate')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

    def export_analysis(self, output_dir: str = "analysis_reports"):
        """Export analysis results to various formats."""
        Path(output_dir).mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export usage report
        with open(os.path.join(output_dir, f"usage_report_{timestamp}.txt"), "w") as f:
            f.write(self.generate_usage_report())
        
        # Export error analysis
        error_stats = self.analyze_error_patterns()
        with open(os.path.join(output_dir, f"error_analysis_{timestamp}.json"), "w") as f:
            json.dump(error_stats, f, indent=2)
        
        # Export time trends
        time_trends = self.analyze_time_trends()
        with open(os.path.join(output_dir, f"time_trends_{timestamp}.json"), "w") as f:
            json.dump(time_trends, f, indent=2)
        
        # Export flight awareness analysis
        flight_stats = self.analyze_flight_awareness()
        with open(os.path.join(output_dir, f"flight_awareness_{timestamp}.json"), "w") as f:
            json.dump(flight_stats, f, indent=2)
        
        # Export raw data for further analysis
        with open(os.path.join(output_dir, f"tool_usage_{timestamp}.csv"), "w") as f:
            writer = csv.DictWriter(f, fieldnames=self.tool_usage_data[0].keys())
            writer.writeheader()
            writer.writerows(self.tool_usage_data)
        
        # Generate visualizations
        self.plot_usage_trends(os.path.join(output_dir, f"usage_trends_{timestamp}.png"))
        self.plot_time_trends(os.path.join(output_dir, f"time_trends_{timestamp}.png"))
        self.plot_flight_awareness(os.path.join(output_dir, f"flight_awareness_{timestamp}.png"))
        
        return f"Analysis exported to {output_dir}"

    def analyze_error_patterns(self) -> Dict:
        """Analyze patterns in tool failures and errors."""
        error_stats = {
            "total_errors": 0,
            "error_by_tool": defaultdict(int),
            "error_by_hour": defaultdict(int),
            "consecutive_errors": defaultdict(int),
            "error_patterns": defaultdict(int)
        }
        
        if not self.tool_usage_data:
            return error_stats
            
        # Sort data by timestamp
        sorted_data = sorted(self.tool_usage_data, 
                           key=lambda x: datetime.fromisoformat(x["timestamp"]))
        
        current_streak = 0
        last_tool = None
        
        for entry in sorted_data:
            if not entry["success"]:
                error_stats["total_errors"] += 1
                tool = entry["tool_name"]
                hour = datetime.fromisoformat(entry["timestamp"]).hour
                
                # Track errors by tool and hour
                error_stats["error_by_tool"][tool] += 1
                error_stats["error_by_hour"][hour] += 1
                
                # Track consecutive errors
                if tool == last_tool:
                    current_streak += 1
                    error_stats["consecutive_errors"][tool] = max(
                        error_stats["consecutive_errors"][tool],
                        current_streak
                    )
                else:
                    current_streak = 1
                
                # Analyze error patterns in input arguments
                args = entry.get("input_args", "")
                if args:
                    error_stats["error_patterns"][args] += 1
                
                last_tool = tool
            else:
                current_streak = 0
                last_tool = None
        
        return error_stats

    def analyze_time_trends(self) -> Dict:
        """Analyze usage patterns over time."""
        if not self.tool_usage_data:
            return {}
            
        df = pd.DataFrame(self.tool_usage_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day_name()
        
        trends = {
            "hourly_distribution": df.groupby('hour').size().to_dict(),
            "daily_distribution": df.groupby('day').size().to_dict(),
            "avg_response_time_by_hour": df.groupby('hour')['execution_time_ms'].mean().to_dict(),
            "success_rate_by_hour": df.groupby('hour')['success'].mean().to_dict()
        }
        
        return trends

    def suggest_improvements(self) -> List[str]:
        """Analyze logs and suggest improvements."""
        suggestions = []
        tool_stats = self.get_tool_usage_stats()
        pattern_stats = self.get_pattern_match_stats()
        
        # Check for underutilized tools
        total_calls = tool_stats["total_calls"]
        for tool, count in tool_stats["tool_frequency"].items():
            if count / total_calls < 0.05:  # Less than 5% of total calls
                suggestions.append(f"Tool '{tool}' is underutilized. Consider improving its pattern matching or functionality.")
        
        # Check for high failure rates
        for entry in self.tool_usage_data:
            if not entry["success"]:
                suggestions.append(f"Tool '{entry['tool_name']}' failed. Check its implementation and error handling.")
        
        # Check for pattern matching issues
        if pattern_stats["total_matches"] < tool_stats["total_calls"] * 0.8:
            suggestions.append("Pattern matching might be too strict. Consider adding more trigger phrases.")
        
        return suggestions

    def get_advanced_suggestions(self) -> List[str]:
        """Generate advanced improvement suggestions based on comprehensive analysis."""
        suggestions = []
        tool_stats = self.get_tool_usage_stats()
        pattern_stats = self.get_pattern_match_stats()
        error_stats = self.analyze_error_patterns()
        time_trends = self.analyze_time_trends()
        
        # Performance suggestions
        avg_time = tool_stats["avg_execution_time"]
        if avg_time > 1000:  # More than 1 second
            suggestions.append(f"High average execution time ({avg_time:.2f}ms). Consider optimizing tool performance.")
        
        # Error pattern suggestions
        for tool, count in error_stats["error_by_tool"].items():
            if count > 5:  # More than 5 errors
                suggestions.append(f"Tool '{tool}' has {count} errors. Investigate error patterns and improve error handling.")
        
        # Time-based suggestions
        peak_hours = [hour for hour, count in time_trends["hourly_distribution"].items() 
                     if count > sum(time_trends["hourly_distribution"].values()) / 24 * 1.5]
        if peak_hours:
            suggestions.append(f"High usage during hours {peak_hours}. Consider load balancing or optimization.")
        
        # Pattern matching suggestions
        common_phrases = sorted(pattern_stats["common_phrases"].items(), 
                              key=lambda x: x[1], reverse=True)[:5]
        suggestions.append(f"Most common phrases: {', '.join(phrase for phrase, _ in common_phrases)}")
        
        return suggestions

# Example usage
if __name__ == "__main__":
    analyzer = LogAnalyzer()
    analyzer.load_recent_logs()
    
    # Generate and print report
    print(analyzer.generate_usage_report())
    
    # Export comprehensive analysis
    print(analyzer.export_analysis())
    
    # Get advanced suggestions
    suggestions = analyzer.get_advanced_suggestions()
    print("\nAdvanced Improvement Suggestions:")
    for suggestion in suggestions:
        print(f"- {suggestion}")

router = APIRouter()

@router.get("/api/log-analysis")
def log_analysis():
    analyzer = LogAnalyzer()
    analyzer.load_recent_logs()
    report = analyzer.generate_usage_report()
    error_stats = analyzer.analyze_error_patterns()
    time_trends = analyzer.analyze_time_trends()
    flight_stats = analyzer.analyze_flight_awareness()
    suggestions = analyzer.get_advanced_suggestions()
    return {
        "report": report,
        "errors": error_stats,
        "time_trends": time_trends,
        "flight_awareness": flight_stats,
        "suggestions": suggestions
    }

# In your main.py, include this router:
# from your_router_file import router as analysis_router
# app.include_router(analysis_router) 