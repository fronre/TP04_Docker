#!/usr/bin/env python3
"""
Smart Parking Web Dashboard
Real-time web interface for monitoring parking sensors
"""

import json
import time
from datetime import datetime
from collections import defaultdict, deque
from flask import Flask, render_template, jsonify
import paho.mqtt.client as mqtt
import threading

# Flask App
app = Flask(__name__)

# MQTT Configuration
MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
MQTT_TOPIC = "parking/sensors"

# Data Storage
parking_data = defaultdict(lambda: deque(maxlen=100))
alert_history = deque(maxlen=50)
sensor_stats = defaultdict(dict)

# Global variables for threading
mqtt_client = None
client_connected = False

# Alert Thresholds
TEMPERATURE_THRESHOLD = 30.0
LOW_BATTERY_THRESHOLD = 25.0
WEAK_SIGNAL_THRESHOLD = -70
LONG_PARKING_DURATION = 120

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker"""
    global client_connected
    if rc == 0:
        client_connected = True
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Web Dashboard connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects from the broker"""
    global client_connected
    client_connected = False
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Web Dashboard disconnected from MQTT broker")

def on_message(client, userdata, msg):
    """Callback for when a message is received"""
    try:
        # Parse incoming sensor data
        sensor_data = json.loads(msg.payload.decode())
        
        # Store data for web display
        sensor_id = sensor_data.get('sensor_id', 'UNKNOWN')
        parking_data[sensor_id].append(sensor_data)
        
        # Check for alerts
        check_alerts(sensor_data)
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error processing message: {e}")

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
            'message': f"High temperature: {temperature}°C",
            'sensor_id': sensor_id,
            'parking_spot_id': parking_spot_id,
            'timestamp': datetime.now().isoformat()
        })
    
    # Low battery alert
    if battery_level < LOW_BATTERY_THRESHOLD:
        alerts.append({
            'type': 'LOW_BATTERY',
            'severity': 'CRITICAL',
            'message': f"Low battery: {battery_level}%",
            'sensor_id': sensor_id,
            'parking_spot_id': parking_spot_id,
            'timestamp': datetime.now().isoformat()
        })
    
    # Weak signal alert
    if signal_strength < WEAK_SIGNAL_THRESHOLD:
        alerts.append({
            'type': 'WEAK_SIGNAL',
            'severity': 'WARNING',
            'message': f"Weak signal: {signal_strength}dBm",
            'sensor_id': sensor_id,
            'parking_spot_id': parking_spot_id,
            'timestamp': datetime.now().isoformat()
        })
    
    # Long parking duration alert
    if is_occupied and vehicle_duration > LONG_PARKING_DURATION:
        alerts.append({
            'type': 'LONG_PARKING',
            'severity': 'INFO',
            'message': f"Long parking: {vehicle_duration} minutes",
            'sensor_id': sensor_id,
            'parking_spot_id': parking_spot_id,
            'timestamp': datetime.now().isoformat()
        })
    
    # Store alerts
    for alert in alerts:
        alert_history.append(alert)

def mqtt_thread():
    """MQTT client thread"""
    global mqtt_client
    mqtt_client = mqtt.Client(client_id="web_dashboard")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message
    
    while True:
        try:
            if not client_connected:
                mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
                mqtt_client.loop_start()
                time.sleep(5)
            else:
                time.sleep(1)
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MQTT connection error: {e}")
            time.sleep(5)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """API endpoint for real-time data"""
    data = {}
    
    # Get latest data from each sensor
    for sensor_id, data_queue in parking_data.items():
        if data_queue:
            latest_data = data_queue[-1]
            data[sensor_id] = latest_data
    
    return jsonify(data)

@app.route('/api/stats')
def get_stats():
    """API endpoint for statistics"""
    total_spots = len(parking_data)
    occupied_spots = 0
    total_readings = 0
    
    for sensor_id, data_queue in parking_data.items():
        if data_queue:
            latest_data = data_queue[-1]
            if latest_data.get('is_occupied', False):
                occupied_spots += 1
            total_readings += len(data_queue)
    
    occupancy_rate = (occupied_spots / total_spots * 100) if total_spots > 0 else 0
    
    stats = {
        'total_spots': total_spots,
        'occupied_spots': occupied_spots,
        'free_spots': total_spots - occupied_spots,
        'occupancy_rate': round(occupancy_rate, 1),
        'total_readings': total_readings,
        'recent_alerts': len(alert_history),
        'mqtt_connected': client_connected
    }
    
    return jsonify(stats)

@app.route('/api/alerts')
def get_alerts():
    """API endpoint for alerts"""
    alerts = list(alert_history)
    return jsonify(alerts)

@app.route('/api/sensors')
def get_sensors():
    """API endpoint for sensor list"""
    sensors = []
    
    for sensor_id, data_queue in parking_data.items():
        if data_queue:
            latest_data = data_queue[-1]
            sensors.append({
                'sensor_id': sensor_id,
                'parking_spot_id': latest_data.get('parking_spot_id', 'UNKNOWN'),
                'is_occupied': latest_data.get('is_occupied', False),
                'battery_level': latest_data.get('battery_level_percent', 0),
                'signal_strength': latest_data.get('signal_strength_dbm', 0),
                'last_seen': latest_data.get('timestamp', ''),
                'location': latest_data.get('location', {})
            })
    
    return jsonify(sensors)

if __name__ == '__main__':
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Smart Parking Web Dashboard")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    
    # Start MQTT thread
    mqtt_thread_obj = threading.Thread(target=mqtt_thread, daemon=True)
    mqtt_thread_obj.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)
