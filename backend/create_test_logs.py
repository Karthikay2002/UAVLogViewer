#!/usr/bin/env python3
"""
Create synthetic test logs with specific edge cases and anomalies
for comprehensive UAV Log Viewer testing
"""

import os
import struct
import time
from pymavlink import mavutil
from pymavlink.mavutil import mavlink

def create_edge_case_logs():
    """Create various edge case log files for testing"""
    
    # Test case 1: Battery voltage drop
    create_battery_failure_log()
    
    # Test case 2: GPS loss
    create_gps_loss_log()
    
    # Test case 3: Motor failure
    create_motor_failure_log()
    
    # Test case 4: Emergency landing
    create_emergency_landing_log()
    
    # Test case 5: Multiple issues
    create_multi_failure_log()

def create_battery_failure_log():
    """Create a log with sudden battery voltage drop"""
    print("Creating battery failure test log...")
    
    # Create a simple log structure
    log_data = []
    start_time = time.time()
    
    # Normal flight for 30 seconds
    for i in range(30):
        timestamp = start_time + i
        
        # Normal battery voltage (12.4V initially)
        if i < 20:
            voltage = 12.4 - (i * 0.02)  # Slow normal drain
        else:
            voltage = 11.8 - ((i-20) * 0.3)  # Sudden drop
        
        # Add GPS message
        log_data.append({
            'timestamp': timestamp,
            'type': 'GPS',
            'Alt': int(5000 + i * 100),  # Rising altitude
        })
        
        # Add battery message  
        log_data.append({
            'timestamp': timestamp,
            'type': 'SYS_STATUS',
            'voltage_battery': int(voltage * 1000),  # mV
        })
        
        # Add failsafe message when voltage drops
        if i == 22:
            log_data.append({
                'timestamp': timestamp,
                'type': 'STATUSTEXT',
                'text': 'Battery Failsafe: Low Voltage',
                'severity': 2
            })
    
    write_simple_log("uploaded/battery_failure_test.bin", log_data)

def create_gps_loss_log():
    """Create a log with GPS signal loss"""
    print("Creating GPS loss test log...")
    
    log_data = []
    start_time = time.time()
    
    for i in range(40):
        timestamp = start_time + i
        
        # GPS fix degrades over time
        if i < 10:
            fix_type = 3  # 3D fix
        elif i < 20:
            fix_type = 2  # 2D fix  
        else:
            fix_type = 0  # No fix
        
        log_data.append({
            'timestamp': timestamp,
            'type': 'GPS_RAW_INT',
            'fix_type': fix_type,
        })
        
        # Add GPS loss message
        if i == 20:
            log_data.append({
                'timestamp': timestamp,
                'type': 'STATUSTEXT',
                'text': 'GPS: Lost 3D Fix',
                'severity': 3
            })
        
        if i == 25:
            log_data.append({
                'timestamp': timestamp,
                'type': 'STATUSTEXT',
                'text': 'EKF2 IMU0 is using GPS',
                'severity': 4
            })
    
    write_simple_log("uploaded/gps_loss_test.bin", log_data)

def create_motor_failure_log():
    """Create a log with motor failure indicators"""
    print("Creating motor failure test log...")
    
    log_data = []
    start_time = time.time()
    
    for i in range(30):
        timestamp = start_time + i
        
        # Normal motor outputs initially
        if i < 15:
            outputs = [1500, 1505, 1498, 1502]  # Normal, balanced
        else:
            # Motor 1 starts failing
            outputs = [1200, 1650, 1648, 1652]  # Motor 1 much lower
        
        log_data.append({
            'timestamp': timestamp,
            'type': 'SERVO_OUTPUT_RAW',
            'servo1_raw': outputs[0],
            'servo2_raw': outputs[1], 
            'servo3_raw': outputs[2],
            'servo4_raw': outputs[3],
        })
        
        # Add motor failure message
        if i == 18:
            log_data.append({
                'timestamp': timestamp,
                'type': 'STATUSTEXT',
                'text': 'Motor output imbalance detected',
                'severity': 2
            })
    
    write_simple_log("uploaded/motor_failure_test.bin", log_data)

def create_emergency_landing_log():
    """Create a log with emergency landing sequence"""
    print("Creating emergency landing test log...")
    
    log_data = []
    start_time = time.time()
    
    for i in range(25):
        timestamp = start_time + i
        
        # Altitude drops rapidly after emergency
        if i < 10:
            altitude = 20000  # 20m
        else:
            altitude = max(1000, 20000 - (i-10) * 2000)  # Rapid descent
        
        log_data.append({
            'timestamp': timestamp,
            'type': 'GPS',
            'Alt': altitude,
        })
        
        # Flight mode changes
        if i == 10:
            log_data.append({
                'timestamp': timestamp,
                'type': 'MODE',
                'mode': 'LAND'
            })
            log_data.append({
                'timestamp': timestamp,
                'type': 'STATUSTEXT',
                'text': 'LAND mode activated - Emergency',
                'severity': 1
            })
    
    write_simple_log("uploaded/emergency_landing_test.bin", log_data)

def create_multi_failure_log():
    """Create a log with multiple simultaneous failures"""
    print("Creating multi-failure test log...")
    
    log_data = []
    start_time = time.time()
    
    for i in range(50):
        timestamp = start_time + i
        
        # Multiple issues cascade
        # Battery drops
        voltage = 12.4 - (i * 0.05) if i < 30 else 10.8
        
        # GPS degrades 
        fix_type = 3 if i < 20 else (2 if i < 35 else 0)
        
        # Motor issues
        if i > 25:
            outputs = [1300, 1700, 1650, 1600]  # Imbalanced
        else:
            outputs = [1500, 1505, 1498, 1502]  # Normal
        
        log_data.extend([
            {
                'timestamp': timestamp,
                'type': 'SYS_STATUS',
                'voltage_battery': int(voltage * 1000),
            },
            {
                'timestamp': timestamp,
                'type': 'GPS_RAW_INT',
                'fix_type': fix_type,
            },
            {
                'timestamp': timestamp,
                'type': 'SERVO_OUTPUT_RAW',
                'servo1_raw': outputs[0],
                'servo2_raw': outputs[1],
                'servo3_raw': outputs[2], 
                'servo4_raw': outputs[3],
            }
        ])
        
        # Add various failure messages
        if i == 25:
            log_data.append({
                'timestamp': timestamp,
                'type': 'STATUSTEXT',
                'text': 'Multiple system failures detected',
                'severity': 1
            })
        
        if i == 30:
            log_data.append({
                'timestamp': timestamp,
                'type': 'STATUSTEXT', 
                'text': 'Battery Failsafe: Critical Voltage',
                'severity': 1
            })
            
        if i == 35:
            log_data.append({
                'timestamp': timestamp,
                'type': 'STATUSTEXT',
                'text': 'EKF2 lost GPS - using flow',
                'severity': 2
            })
    
    write_simple_log("uploaded/multi_failure_test.bin", log_data)

def write_simple_log(filename, log_data):
    """Write a simple test log file"""
    print(f"Writing {filename} with {len(log_data)} messages...")
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Create a minimal binary log format
    with open(filename, 'wb') as f:
        # Write a simple header
        f.write(b'TESTLOG\x00')
        
        for msg in log_data:
            # Write timestamp (8 bytes)
            f.write(struct.pack('<d', msg['timestamp']))
            
            # Write message type (16 bytes, padded)
            msg_type = msg['type'].encode('ascii')
            f.write(msg_type.ljust(16, b'\x00'))
            
            # Write message data (simplified)
            if msg['type'] == 'GPS':
                f.write(struct.pack('<i', msg.get('Alt', 0)))
            elif msg['type'] == 'SYS_STATUS':
                f.write(struct.pack('<H', msg.get('voltage_battery', 0)))
            elif msg['type'] == 'GPS_RAW_INT':
                f.write(struct.pack('<B', msg.get('fix_type', 0)))
            elif msg['type'] == 'SERVO_OUTPUT_RAW':
                for i in range(1, 5):
                    f.write(struct.pack('<H', msg.get(f'servo{i}_raw', 1500)))
            elif msg['type'] == 'STATUSTEXT':
                text = msg.get('text', '').encode('ascii')[:50]
                f.write(text.ljust(50, b'\x00'))
                f.write(struct.pack('<B', msg.get('severity', 6)))
            elif msg['type'] == 'MODE':
                mode = msg.get('mode', '').encode('ascii')[:10]
                f.write(mode.ljust(10, b'\x00'))
    
    print(f"Created {filename}")

if __name__ == "__main__":
    print("Creating edge case test logs...")
    create_edge_case_logs()
    print("✅ All edge case test logs created successfully!")
    print("\nTest logs created:")
    print("- battery_failure_test.bin (sudden voltage drop)")
    print("- gps_loss_test.bin (GPS signal degradation)")  
    print("- motor_failure_test.bin (motor output imbalance)")
    print("- emergency_landing_test.bin (emergency landing sequence)")
    print("- multi_failure_test.bin (multiple simultaneous failures)") 