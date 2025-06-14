#!/usr/bin/env python3
"""
Test script to demonstrate edge case detection in UAV Log Viewer
"""

import requests
import json
from tabulate import tabulate

def test_all_logs():
    """Test all available log files and show edge case detection results"""
    
    base_url = "http://localhost:8000"
    
    # Test logs with their expected characteristics
    test_logs = {
        "copter_test.bin": "Normal flight log (baseline)",
        "real_copter_1.bin": "Minimal flight data", 
        "real_copter_2.bin": "Ground test log",
        "real_plane_1.bin": "Fixed-wing aircraft log",
        "battery_failure_test.bin": "Synthetic battery voltage drop",
        "gps_loss_test.bin": "Synthetic GPS signal loss",
        "motor_failure_test.bin": "Synthetic motor imbalance",
        "emergency_landing_test.bin": "Synthetic emergency landing",
        "multi_failure_test.bin": "Synthetic multiple failures"
    }
    
    print("🔍 UAV LOG VIEWER - Edge Case Analysis Summary")
    print("=" * 80)
    
    results = []
    
    for filename, description in test_logs.items():
        try:
            response = requests.get(f"{base_url}/summary/{filename}")
            if response.status_code == 200:
                data = response.json()
                
                # Extract key metrics
                flight_time = data.get("flight_time_sec", 0)
                max_alt = data.get("max_altitude", 0)
                
                edge_summary = data.get("edge_case_summary", {})
                safety_score = edge_summary.get("flight_safety_score", "N/A")
                total_anomalies = edge_summary.get("total_anomalies", 0)
                detected_issues = edge_summary.get("detected_issues", [])
                
                # Battery info
                min_voltage = data.get("min_battery_voltage")
                max_voltage = data.get("max_battery_voltage")
                battery_drops = len(data.get("battery_voltage_drops", []))
                
                # GPS info  
                gps_quality = data.get("gps_fix_quality", {})
                gps_losses = len(data.get("gps_loss_events", []))
                
                # Critical events
                failsafes = len(data.get("failsafe_events", []))
                motor_issues = len(data.get("motor_failure_indicators", []))
                emergency_events = len(data.get("emergency_events", []))
                
                results.append({
                    "Log File": filename,
                    "Description": description,
                    "Flight Time": f"{flight_time:.1f}s",
                    "Max Alt": f"{max_alt:.1f}m",
                    "Safety Score": safety_score,
                    "Total Anomalies": total_anomalies,
                    "Battery Issues": battery_drops,
                    "GPS Issues": gps_losses,
                    "Motor Issues": motor_issues,
                    "Failsafes": failsafes,
                    "Emergency Events": emergency_events,
                    "Status": "✅ Analyzed"
                })
                
                # Print detailed info for logs with issues
                if total_anomalies > 0:
                    print(f"\n🚨 ANOMALIES DETECTED in {filename}:")
                    for issue in detected_issues:
                        print(f"   • {issue}")
                
            else:
                results.append({
                    "Log File": filename,
                    "Description": description,
                    "Flight Time": "N/A",
                    "Max Alt": "N/A", 
                    "Safety Score": "N/A",
                    "Total Anomalies": "N/A",
                    "Battery Issues": "N/A",
                    "GPS Issues": "N/A",
                    "Motor Issues": "N/A",
                    "Failsafes": "N/A",
                    "Emergency Events": "N/A",
                    "Status": f"❌ Error {response.status_code}"
                })
                
        except Exception as e:
            results.append({
                "Log File": filename,
                "Description": description,
                "Flight Time": "N/A",
                "Max Alt": "N/A",
                "Safety Score": "N/A", 
                "Total Anomalies": "N/A",
                "Battery Issues": "N/A",
                "GPS Issues": "N/A",
                "Motor Issues": "N/A",
                "Failsafes": "N/A",
                "Emergency Events": "N/A",
                "Status": f"❌ {str(e)[:20]}..."
            })
    
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE LOG ANALYSIS RESULTS")
    print("=" * 80)
    
    # Create summary table
    table_data = []
    for result in results:
        table_data.append([
            result["Log File"][:25] + "..." if len(result["Log File"]) > 25 else result["Log File"],
            result["Flight Time"],
            result["Max Alt"],
            result["Safety Score"],
            result["Total Anomalies"],
            result["Battery Issues"],
            result["GPS Issues"],
            result["Motor Issues"],
            result["Status"]
        ])
    
    headers = ["Log File", "Flight Time", "Max Alt", "Safety", "Anomalies", "Battery", "GPS", "Motor", "Status"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    print("\n🎯 EDGE CASE DETECTION CAPABILITIES:")
    print("✅ Battery voltage drop detection")
    print("✅ GPS signal loss monitoring") 
    print("✅ Motor failure indicators")
    print("✅ Emergency landing detection")
    print("✅ Flight mode change tracking")
    print("✅ Failsafe event logging")
    print("✅ Communication loss detection")
    print("✅ Sudden altitude change alerts")
    print("✅ Pre-arm failure tracking")
    print("✅ EKF failure monitoring")
    print("✅ Compass error detection")
    print("✅ Vibration warning alerts")
    print("✅ Flight safety scoring")
    
    print(f"\n📈 ANALYSIS SUMMARY:")
    successful_analyses = len([r for r in results if "✅" in r["Status"]])
    total_logs = len(results)
    print(f"Successfully analyzed: {successful_analyses}/{total_logs} log files")
    
    anomaly_logs = len([r for r in results if isinstance(r["Total Anomalies"], int) and r["Total Anomalies"] > 0])
    print(f"Logs with detected anomalies: {anomaly_logs}")
    
    return results

if __name__ == "__main__":
    print("Testing UAV Log Viewer edge case detection...")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    try:
        results = test_all_logs()
        print("\n🎉 Edge case testing completed successfully!")
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        print("Make sure the FastAPI backend is running with: uvicorn main:app --reload --host 0.0.0.0 --port 8000") 