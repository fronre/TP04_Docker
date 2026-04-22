#!/bin/bash

# Smart Parking IoT - Docker Hub Deployment Script
# This script builds and pushes all components to Docker Hub

echo "🚗 Smart Parking IoT - Docker Hub Deployment"
echo "============================================"

# Configuration
DOCKER_USERNAME="fronre"
IMAGE_PREFIX="smart-parking-iot"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if user is logged in to Docker Hub
if ! docker info | grep -q "Username"; then
    print_warning "You are not logged in to Docker Hub."
    print_info "Please run: docker login"
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

echo ""
print_info "Building Smart Parking IoT images..."
echo ""

# Build Sensor Image
print_status "Building Parking Sensor image..."
docker build -t ${DOCKER_USERNAME}/${IMAGE_PREFIX}-sensor:latest ./sensor
if [ $? -eq 0 ]; then
    print_status "Sensor image built successfully"
else
    print_error "Failed to build Sensor image"
fi

# Build Server Image  
print_status "Building MQTT Server image..."
docker build -t ${DOCKER_USERNAME}/${IMAGE_PREFIX}-server:latest ./server
if [ $? -eq 0 ]; then
    print_status "Server image built successfully"
else
    print_error "Failed to build Server image"
fi

# Build Web Dashboard Image
print_status "Building Web Dashboard image..."
docker build -t ${DOCKER_USERNAME}/${IMAGE_PREFIX}-web:latest ./web
if [ $? -eq 0 ]; then
    print_status "Web Dashboard image built successfully"
else
    print_error "Failed to build Web Dashboard image"
fi

echo ""
print_info "All images built successfully!"
echo ""

# Push images to Docker Hub
print_info "Pushing images to Docker Hub..."
echo ""

# Push Sensor Image
print_status "Pushing Parking Sensor image..."
docker push ${DOCKER_USERNAME}/${IMAGE_PREFIX}-sensor:latest

# Push Server Image
print_status "Pushing MQTT Server image..."
docker push ${DOCKER_USERNAME}/${IMAGE_PREFIX}-server:latest

# Push Web Dashboard Image
print_status "Pushing Web Dashboard image..."
docker push ${DOCKER_USERNAME}/${IMAGE_PREFIX}-web:latest

echo ""
print_status "🎉 All images pushed to Docker Hub successfully!"
echo ""

# Display repository information
echo "============================================"
print_info "Docker Hub Repository:"
echo "https://hub.docker.com/u/${DOCKER_USERNAME}"
echo ""
echo "Available images:"
echo "  🚗 ${DOCKER_USERNAME}/${IMAGE_PREFIX}-sensor:latest"
echo "  📡 ${DOCKER_USERNAME}/${IMAGE_PREFIX}-server:latest"  
echo "  🖥️ ${DOCKER_USERNAME}/${IMAGE_PREFIX}-web:latest"
echo "============================================"

echo ""
print_info "To run the complete system:"
echo "docker-compose -f docker-compose-dockerhub.yml up -d"
echo ""

# Create docker-compose file for Docker Hub images
cat > docker-compose-dockerhub.yml << EOF
version: '3.8'

services:
  # MQTT Broker (Eclipse Mosquitto)
  mosquitto:
    image: eclipse-mosquitto:2.0
    container_name: mosquitto-broker
    ports:
      - "1883:1883"
    volumes:
      - mosquitto_data:/mosquitto/data
      - mosquitto_log:/mosquitto/log
    restart: unless-stopped
    networks:
      - iot-network

  # Smart Parking Server (Subscriber)
  server:
    image: fronre/${IMAGE_PREFIX}-server:latest
    container_name: parking-server
    depends_on:
      - mosquitto
    restart: unless-stopped
    networks:
      - iot-network
    environment:
      - PYTHONUNBUFFERED=1

  # Smart Parking Sensor (Publisher)
  sensor:
    image: fronre/${IMAGE_PREFIX}-sensor:latest
    container_name: parking-sensor
    depends_on:
      - mosquitto
      - server
    restart: unless-stopped
    networks:
      - iot-network
    environment:
      - PYTHONUNBUFFERED=1

  # Web Dashboard
  web:
    image: fronre/${IMAGE_PREFIX}-web:latest
    container_name: parking-web
    ports:
      - "5000:5000"
    depends_on:
      - mosquitto
    restart: unless-stopped
    networks:
      - iot-network
    environment:
      - PYTHONUNBUFFERED=1

volumes:
  mosquitto_data:
    driver: local
  mosquitto_log:
    driver: local

networks:
  iot-network:
    driver: bridge
EOF

print_status "Created docker-compose-dockerhub.yml for Docker Hub images"
echo ""
print_info "Deployment complete! 🎉"
