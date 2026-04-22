# 🚗 Smart Parking IoT System

A complete IoT project using Docker and MQTT for smart parking monitoring with environmental sensors.

## 🏗️ Project Overview

This system simulates a smart parking infrastructure where sensors monitor parking spots and environmental conditions. The system includes:

- **MQTT Broker**: Eclipse Mosquitto for message communication
- **Parking Sensors**: Simulated sensors that detect vehicle presence and environmental data
- **Server**: Central monitoring system that processes data and generates alerts
- **Docker Orchestration**: Complete containerized deployment

## 📋 Features

### Smart Parking Scenario
- **Vehicle Detection**: Monitors parking spot occupancy (70% chance of being occupied)
- **Environmental Monitoring**: Temperature and humidity sensing
- **Location Tracking**: Zone and floor information for each parking spot
- **Battery & Signal Monitoring**: Sensor health tracking
- **Parking Duration**: Tracks how long vehicles have been parked

### Alert System
- **🔥 High Temperature Alert**: Triggered when temperature > 30°C
- **🔋 Low Battery Alert**: Triggered when battery < 25%
- **📶 Weak Signal Alert**: Triggered when signal < -70dBm
- **⏰ Long Parking Alert**: Triggered when parked > 2 hours
- **📊 Real-time Statistics**: Occupancy rates and system health

### Enhanced Logging
- **Timestamped Messages**: All logs include precise timestamps
- **Emoji Indicators**: Visual indicators for quick status identification
- **Formatted Output**: Clean, readable console output
- **Alert History**: Tracks recent alerts for analysis

## 🏛️ System Architecture

```
┌─────────────────┐    MQTT     ┌─────────────────┐
│   Parking       │◄──────────►│   Mosquitto     │
│   Sensor        │   Topic:   │   Broker        │
│   (Publisher)   │parking/sensors│   (1883)       │
└─────────────────┘            └─────────────────┘
                                        │
                                        ▼
                              ┌─────────────────┐
                              │   Parking       │
                              │   Server        │
                              │   (Subscriber)  │
                              └─────────────────┘
```

## 📁 Project Structure

```
mini-project/
├── docker-compose.yml          # Docker orchestration
├── mosquitto.conf             # MQTT broker configuration
├── README.md                  # This file
├── sensor/                    # Parking sensor component
│   ├── Dockerfile
│   ├── requirements.txt
│   └── sensor.py
├── server/                    # Monitoring server component
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server.py
├── web-dashboard/             # Web dashboard component
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── docker-compose.yml          # Docker Hub deployment configuration
    ├── Dockerfile
    ├── requirements.txt
    └── server.py
```

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Docker Compose installed
- Git (for cloning)

### Step 1: Clone/Download the Project
```bash
# If using git
git clone <repository-url>
cd mini-project

# Or download and extract the files to a folder
```

### Step 2: Build and Start the System
```bash
# Build and start all containers
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### Step 3: Monitor the System
You should see output from three containers:

1. **Mosquitto Broker**: MQTT broker startup logs
2. **Parking Server**: Server connection and data processing
3. **Parking Sensor**: Sensor data generation and publishing

### Step 4: View Real-time Data
The system will immediately start generating and processing data:

**Sensor Output:**
```
[2026-04-22 20:43:15] 🚗 Starting Smart Parking Sensor: PARKING_456
[2026-04-22 20:43:15] 📍 Monitoring Parking Spot: SPOT_23
[2026-04-22 20:43:17] ✅ Sensor PARKING_456 connected to MQTT broker
[2026-04-22 20:43:19] 📡 Data sent | 🚗 OCCUPIED | Temp: 32.5°C | Humidity: 65.2% | Battery: 87.3% 🔥 HIGH TEMP!
```

**Server Output:**
```
[2026-04-22 20:43:20] 🏢 Starting Smart Parking Server
[2026-04-22 20:43:21] ✅ Server connected to MQTT broker
[2026-04-22 20:43:21] 📡 Subscribed to topic: parking/sensors

[2026-04-22 20:43:25] 📥 Data received from PARKING_456
    📍 Spot: SPOT_23 | 🚗 OCCUPIED
    🌡️  Temp: 32.5°C | 💧 Humidity: 65.2%
    🔋 Battery: 87.3% | 📶 Signal: -45dBm
    📍 Location: Zone_A, Floor 2
    ⏱️  Parked for: 45 minutes

⚠️ [2026-04-22 20:43:25] WARNING ALERT
   🔥 HIGH TEMPERATURE ALERT: 32.5°C exceeds threshold of 30.0°C
   Sensor: PARKING_456 | Spot: SPOT_23
📊 Summary: 1/1 spots occupied (100.0%)
```

## 🛠️ Configuration

### MQTT Broker Settings
Edit `mosquitto.conf` to customize:
- Port (default: 1883)
- Authentication
- Persistence settings
- Logging levels

### Alert Thresholds
Edit `server/server.py` to modify:
```python
TEMPERATURE_THRESHOLD = 30.0  # Celsius
LOW_BATTERY_THRESHOLD = 25.0  # Percentage
WEAK_SIGNAL_THRESHOLD = -70   # dBm
LONG_PARKING_DURATION = 120   # minutes
```

### Sensor Settings
Edit `sensor/sensor.py` to customize:
- Data generation frequency (2-3 seconds)
- Simulation parameters
- MQTT topic and broker settings

## 🔧 Management Commands

### Start the System
```bash
docker-compose up --build
```

### Stop the System
```bash
docker-compose down
```

### View Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs server
docker-compose logs sensor
docker-compose logs mosquitto

# Follow logs in real-time
docker-compose logs -f
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart server
```

### Scale Sensors (Multiple Sensors)
```bash
# Run 3 sensor instances
docker-compose up --build --scale sensor=3
```

## 📊 Data Format

### Sensor Message Format (JSON)
```json
{
  "sensor_id": "PARKING_456",
  "parking_spot_id": "SPOT_23",
  "timestamp": "2026-04-22T20:43:25.123456",
  "is_occupied": true,
  "temperature_celsius": 32.5,
  "humidity_percent": 65.2,
  "battery_level_percent": 87.3,
  "signal_strength_dbm": -45,
  "vehicle_duration_minutes": 45,
  "location": {
    "zone": "Zone_A",
    "floor": 2
  }
}
```

## 🚨 Alert Types

| Alert Type | Severity | Trigger | Icon |
|------------|----------|---------|------|
| HIGH_TEMPERATURE | WARNING | Temp > 30°C | 🔥 |
| LOW_BATTERY | CRITICAL | Battery < 25% | 🔋 |
| WEAK_SIGNAL | WARNING | Signal < -70dBm | 📶 |
| LONG_PARKING | INFO | Parked > 2 hours | ⏰ |

## 🔍 Troubleshooting

### Common Issues

1. **Port 1883 already in use**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep 1883
   # Stop conflicting service or change port in docker-compose.yml
   ```

2. **Container won't start**
   ```bash
   # Check for build errors
   docker-compose build
   
   # Check container logs
   docker-compose logs [service-name]
   ```

3. **MQTT Connection Issues**
   ```bash
   # Verify broker is running
   docker-compose ps mosquitto
   
   # Test MQTT connection
   docker exec -it mosquitto-broker mosquitto_pub -h localhost -t test -m "hello"
   ```

4. **Permission Issues**
   ```bash
   # Reset Docker permissions
   docker-compose down -v
   docker system prune -f
   ```

### Health Checks
The system includes health checks for all services:
- MQTT broker health check via mosquitto_pub
- Python environment health checks
- Automatic restart on failure

## 🧪 Testing

### Manual Testing
1. **Test MQTT Connection**:
   ```bash
   docker exec -it mosquitto-broker mosquitto_sub -h localhost -t "parking/sensors"
   ```

2. **Test Sensor Data**:
   ```bash
   docker exec -it parking-sensor python -c "import sensor; print('Sensor module OK')"
   ```

3. **Test Server**:
   ```bash
   docker exec -it parking-server python -c "import server; print('Server module OK')"
   ```

## 📈 Monitoring

### System Metrics
- **Occupancy Rate**: Real-time parking utilization
- **Alert Frequency**: Number of alerts in last 5 minutes
- **Sensor Health**: Battery levels and signal strength
- **Temperature Trends**: Environmental monitoring

### Performance
- **Message Rate**: ~1 message every 2-3 seconds per sensor
- **Memory Usage**: < 100MB per container
- **Network Traffic**: < 1MB/minute per sensor

## 🔮 Future Enhancements

- **Web Dashboard**: Real-time visualization
- **Database Integration**: Historical data storage
- **Mobile App**: Parking spot finder
- **AI Analytics**: Predictive parking patterns
- **Multiple Sensor Types**: Additional IoT sensors

## 📝 License

This project is provided as-is for educational and demonstration purposes.

## 🤝 Contributing

Feel free to modify and enhance the system for your specific use case!

---

**🎉 Enjoy your Smart Parking IoT System!**
