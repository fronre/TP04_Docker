#!/usr/bin/env python3
"""
Smart Parking IoT Sensor
Simulates parking spot sensors that detect vehicle presence and environmental conditions.
Publishes data to MQTT broker every 2-3 seconds.
"""

import json
import random
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# MQTT Configuration
MQTT_BROKER = "mosquitto"
MQTT_PORT = 1883
MQTT_TOPIC = "parking/sensors"

# Sensor Configuration
SENSOR_ID = f"PARKING_{random.randint(100, 999)}"
PARKING_SPOT_ID = f"SPOT_{random.randint(1, 50)}"

# Thresholds
TEMPERATURE_THRESHOLD = 30.0  # Celsius
HUMIDITY_RANGE = (30, 80)     # Percentage

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker"""
    if rc == 0:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Sensor {SENSOR_ID} connected to MQTT broker")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Failed to connect, return code {rc}")

def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects from the broker"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔌 Sensor {SENSOR_ID} disconnected from MQTT broker")

def generate_sensor_data():
    """
    Generate realistic parking sensor data
    Returns: Dictionary with sensor readings
    """
    # Simulate vehicle presence (70% chance of being occupied)
    is_occupied = random.random() < 0.7
    
    # Generate environmental data
    temperature = round(random.uniform(15, 40), 1)  # Celsius
    humidity = round(random.uniform(*HUMIDITY_RANGE), 1)  # Percentage
    
    # Generate additional sensor data
    battery_level = round(random.uniform(20, 100), 1)  # Percentage
    signal_strength = round(random.uniform(-80, -30), 0)  # dBm
    
    # Time vehicle has been parked (if occupied)
    vehicle_duration = random.randint(1, 180) if is_occupied else 0  # minutes
    
    data = {
        "sensor_id": SENSOR_ID,
        "parking_spot_id": PARKING_SPOT_ID,
        "timestamp": datetime.now().isoformat(),
        "is_occupied": is_occupied,
        "temperature_celsius": temperature,
        "humidity_percent": humidity,
        "battery_level_percent": battery_level,
        "signal_strength_dbm": signal_strength,
        "vehicle_duration_minutes": vehicle_duration,
        "location": {
            "zone": f"Zone_{random.choice(['A', 'B', 'C'])}",
            "floor": random.randint(1, 3)
        }
    }
    
    return data

def main():
    """Main sensor loop"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚗 Starting Smart Parking Sensor: {SENSOR_ID}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📍 Monitoring Parking Spot: {PARKING_SPOT_ID}")
    
    # Create MQTT client
    client = mqtt.Client(client_id=SENSOR_ID)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    # Connect to broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        # Main sensor loop
        while True:
            try:
                # Generate sensor data
                sensor_data = generate_sensor_data()
                
                # Convert to JSON and publish
                payload = json.dumps(sensor_data, indent=2)
                result = client.publish(MQTT_TOPIC, payload)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    status = "🚗 OCCUPIED" if sensor_data["is_occupied"] else "🅿️ FREE"
                    temp_alert = "🔥 HIGH TEMP!" if sensor_data["temperature_celsius"] > TEMPERATURE_THRESHOLD else ""
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📡 Data sent | {status} | "
                          f"Temp: {sensor_data['temperature_celsius']}°C | "
                          f"Humidity: {sensor_data['humidity_percent']}% | "
                          f"Battery: {sensor_data['battery_level_percent']}% {temp_alert}")
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Failed to publish data")
                
                # Wait 2-3 seconds before next reading
                sleep_time = random.uniform(2, 3)
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🛑 Sensor stopped by user")
                break
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ Error in sensor loop: {e}")
                time.sleep(5)
                
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ Failed to connect to MQTT broker: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔌 Sensor {SENSOR_ID} shutdown complete")

if __name__ == "__main__":
    main()
