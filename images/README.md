# Smart Parking IoT Images

This folder contains images for the Smart Parking IoT system components.

## Images Description

### 🚗 Parking Sensor
- **Purpose**: IoT sensor for detecting vehicle presence
- **Features**: Temperature, humidity, battery, signal monitoring
- **Technology**: Python + paho-mqtt + Docker

### 📡 MQTT Server  
- **Purpose**: Real-time message broker
- **Technology**: Eclipse Mosquitto
- **Port**: 1883
- **Protocol**: MQTT

### 🖥️ Control Dashboard
- **Purpose**: Central monitoring interface
- **Features**: Real-time data visualization, alerts, statistics
- **Technology**: Flask + Bootstrap + JavaScript

### 🌡️ Temperature Monitoring
- **Purpose**: Environmental sensor data collection
- **Alerts**: High temperature warnings (>30°C)

### 🔋 Battery Management
- **Purpose**: Power monitoring system
- **Alerts**: Low battery warnings (<25%)

### 🏗️ Smart Infrastructure
- **Purpose**: Connected parking ecosystem
- **Architecture**: Containerized microservices

## Docker Hub Repository

All images will be pushed to Docker Hub under:
```
username/smart-parking-iot
```

## Build Commands

```bash
# Build all images
docker build -t username/smart-parking-sensor ./sensor
docker build -t username/smart-parking-server ./server  
docker build -t username/smart-parking-web ./web
docker build -t username/smart-parking-mosquitto ./mosquitto

# Push to Docker Hub
docker push username/smart-parking-sensor
docker push username/smart-parking-server
docker push username/smart-parking-web
docker push username/smart-parking-mosquitto
```
