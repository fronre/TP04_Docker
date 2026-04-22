#!/usr/bin/env python3
"""
Smart Parking IoT Server
Subscribes to MQTT topics to receive parking sensor data and generates alerts.
Monitors temperature thresholds and parking occupancy patterns.
"""

import json
import time
from datetime import datetime
from collections import defaultdict, deque
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
MQTT_TOPIC = "parking/sensors"

# Alert Thresholds
TEMPERATURE_THRESHOLD = 30.0  # Celsius
LOW_BATTERY_THRESHOLD = 25.0  # Percentage
WEAK_SIGNAL_THRESHOLD = -70   # dBm
LONG_PARKING_DURATION = 120   # minutes (2 hours)

# Data tracking
parking_data = defaultdict(lambda: deque(maxlen=100))
alert_history = deque(maxlen=50)
sensor_stats = defaultdict(dict)

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker"""
    if rc == 0:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Server connected to MQTT broker")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📡 Subscribed to topic: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects from the broker"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔌 Server disconnected from MQTT broker")

def on_message(client, userdata, msg):
    """Callback for when a message is received"""
    try:
        # Parse incoming sensor data
        sensor_data = json.loads(msg.payload.decode())
        
        # Extract key information
        sensor_id = sensor_data.get('sensor_id', 'UNKNOWN')
        parking_spot_id = sensor_data.get('parking_spot_id', 'UNKNOWN')
        timestamp = sensor_data.get('timestamp', datetime.now().isoformat())
        is_occupied = sensor_data.get('is_occupied', False)
        temperature = sensor_data.get('temperature_celsius', 0)
        humidity = sensor_data.get('humidity_percent', 0)
        battery_level = sensor_data.get('battery_level_percent', 100)
        signal_strength = sensor_data.get('signal_strength_dbm', -50)
        vehicle_duration = sensor_data.get('vehicle_duration_minutes', 0)
        location = sensor_data.get('location', {})
        
        # Store data for analysis
        parking_data[sensor_id].append(sensor_data)
        
        # Update sensor statistics
        update_sensor_stats(sensor_id, sensor_data)
        
        # Display received data
        status = "🚗 OCCUPIED" if is_occupied else "🅿️ FREE"
        print(f"\n[{timestamp}] 📥 Data received from {sensor_id}")
        print(f"    📍 Spot: {parking_spot_id} | {status}")
        print(f"    🌡️  Temp: {temperature}°C | 💧 Humidity: {humidity}%")
        print(f"    🔋 Battery: {battery_level}% | 📶 Signal: {signal_strength}dBm")
        print(f"    📍 Location: Zone {location.get('zone', 'N/A')}, Floor {location.get('floor', 'N/A')}")
        if is_occupied:
            print(f"    ⏱️  Parked for: {vehicle_duration} minutes")
        
        # Check for alerts
        check_alerts(sensor_data)
        
        # Display summary statistics
        display_summary()
        
    except json.JSONDecodeError as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ JSON decode error: {e}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Error processing message: {e}")

def update_sensor_stats(sensor_id, data):
    """Update statistics for a sensor"""
    if sensor_id not in sensor_stats:
        sensor_stats[sensor_id] = {
            'first_seen': datetime.now(),
            'last_seen': datetime.now(),
            'total_readings': 0,
            'max_temp': -float('inf'),
            'min_temp': float('inf'),
            'occupancy_count': 0
        }
    
    stats = sensor_stats[sensor_id]
    stats['last_seen'] = datetime.now()
    stats['total_readings'] += 1
    stats['max_temp'] = max(stats['max_temp'], data.get('temperature_celsius', 0))
    stats['min_temp'] = min(stats['min_temp'], data.get('temperature_celsius', 100))
    
    if data.get('is_occupied', False):
        stats['occupancy_count'] += 1

def check_alerts(sensor_data):
    """Check for various alert conditions"""
    sensor_id = sensor_data.get('sensor_id', 'UNKNOWN')
    parking_spot_id = sensor_data.get('parking_spot_id', 'UNKNOWN')
    temperature = sensor_data.get('temperature_celsius', 0)
    battery_level = sensor_data.get('battery_level_percent', 100)
    signal_strength = sensor_data.get('signal_strength_dbm', -50)
    vehicle_duration = sensor_data.get('vehicle_duration_minutes', 0)
    is_occupied = sensor_data.get('is_occupied', False)
    
    alerts = []
    
    # Temperature alert
    if temperature > TEMPERATURE_THRESHOLD:
        alerts.append({
            'type': 'HIGH_TEMPERATURE',
            'severity': 'WARNING',
            'message': f"🔥 HIGH TEMPERATURE ALERT: {temperature}°C exceeds threshold of {TEMPERATURE_THRESHOLD}°C",
            'sensor_id': sensor_id,
            'parking_spot_id': parking_spot_id
        })
    
    # Low battery alert
    if battery_level < LOW_BATTERY_THRESHOLD:
        alerts.append({
            'type': 'LOW_BATTERY',
            'severity': 'CRITICAL',
            'message': f"🔋 LOW BATTERY ALERT: {battery_level}% below threshold of {LOW_BATTERY_THRESHOLD}%",
            'sensor_id': sensor_id,
            'parking_spot_id': parking_spot_id
        })
    
    # Weak signal alert
    if signal_strength < WEAK_SIGNAL_THRESHOLD:
        alerts.append({
            'type': 'WEAK_SIGNAL',
            'severity': 'WARNING',
            'message': f"📶 WEAK SIGNAL ALERT: {signal_strength}dBm below threshold of {WEAK_SIGNAL_THRESHOLD}dBm",
            'sensor_id': sensor_id,
            'parking_spot_id': parking_spot_id
        })
    
    # Long parking duration alert
    if is_occupied and vehicle_duration > LONG_PARKING_DURATION:
        alerts.append({
            'type': 'LONG_PARKING',
            'severity': 'INFO',
            'message': f"⏰ LONG PARKING ALERT: Vehicle parked for {vehicle_duration} minutes (threshold: {LONG_PARKING_DURATION} min)",
            'sensor_id': sensor_id,
            'parking_spot_id': parking_spot_id
        })
    
    # Display alerts
    for alert in alerts:
        alert_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        severity_icon = {
            'CRITICAL': '🚨',
            'WARNING': '⚠️',
            'INFO': 'ℹ️'
        }.get(alert['severity'], '📢')
        
        print(f"\n{severity_icon} [{alert_time}] {alert['severity']} ALERT")
        print(f"   {alert['message']}")
        print(f"   Sensor: {alert['sensor_id']} | Spot: {alert['parking_spot_id']}")
        
        # Store alert in history
        alert_history.append({
            'timestamp': alert_time,
            **alert
        })

def display_summary():
    """Display summary statistics"""
    if len(parking_data) == 0:
        return
    
    # Count current occupancy
    total_spots = len(parking_data)
    occupied_spots = sum(1 for data in parking_data.values() 
                       if data and data[-1].get('is_occupied', False))
    
    occupancy_rate = (occupied_spots / total_spots * 100) if total_spots > 0 else 0
    
    print(f"� Summary: {occupied_spots}/{total_spots} spots occupied ({occupancy_rate:.1f}%)")
    
    # Show recent alerts count
    recent_alerts = len([a for a in alert_history 
                        if (datetime.now() - datetime.strptime(a['timestamp'], '%Y-%m-%d %H:%M:%S')).seconds < 300])
    if recent_alerts > 0:
        print(f"🚨 Recent alerts (last 5 min): {recent_alerts}")

def main():
    """Main server loop"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🏢 Starting Smart Parking Server")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📡 Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🎯 Monitoring topic: {MQTT_TOPIC}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🌡️  Temperature threshold: {TEMPERATURE_THRESHOLD}°C")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔋 Battery threshold: {LOW_BATTERY_THRESHOLD}%")
    print("=" * 80)
    
    # Create MQTT client
    client = mqtt.Client(client_id="parking_server")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    
    try:
        # Connect to broker
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Start the network loop
        client.loop_forever()
        
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🛑 Server stopped by user")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Server error: {e}")
    finally:
        client.disconnect()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔌 Server shutdown complete")

if __name__ == "__main__":
    main()
