@echo off
REM Smart Parking IoT - Docker Hub Deployment Script for Windows
REM This script builds and pushes all components to Docker Hub

echo ============================================
echo 🚗 Smart Parking IoT - Docker Hub Deployment
echo ============================================

REM Configuration
set DOCKER_USERNAME=fronre
set IMAGE_PREFIX=smart-parking-iot

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

echo.
echo ℹ️  Building Smart Parking IoT images...
echo.

REM Build Sensor Image
echo ✅ Building Parking Sensor image...
docker build -t %DOCKER_USERNAME%/%IMAGE_PREFIX%-sensor:latest ./sensor
if %errorlevel% equ 0 (
    echo ✅ Sensor image built successfully
) else (
    echo ❌ Failed to build Sensor image
)

REM Build Server Image  
echo ✅ Building MQTT Server image...
docker build -t %DOCKER_USERNAME%/%IMAGE_PREFIX%-server:latest ./server
if %errorlevel% equ 0 (
    echo ✅ Server image built successfully
) else (
    echo ❌ Failed to build Server image
)

REM Build Web Dashboard Image
echo ✅ Building Web Dashboard image...
docker build -t %DOCKER_USERNAME%/%IMAGE_PREFIX%-web:latest ./web
if %errorlevel% equ 0 (
    echo ✅ Web Dashboard image built successfully
) else (
    echo ❌ Failed to build Web Dashboard image
)

echo.
echo ℹ️  All images built successfully!
echo.

echo ℹ️  Pushing images to Docker Hub...
echo.

REM Push Sensor Image
echo ✅ Pushing Parking Sensor image...
docker push %DOCKER_USERNAME%/%IMAGE_PREFIX%-sensor:latest

REM Push Server Image
echo ✅ Pushing MQTT Server image...
docker push %DOCKER_USERNAME%/%IMAGE_PREFIX%-server:latest

REM Push Web Dashboard Image
echo ✅ Pushing Web Dashboard image...
docker push %DOCKER_USERNAME%/%IMAGE_PREFIX%-web:latest

echo.
echo 🎉 All images pushed to Docker Hub successfully!
echo.

REM Display repository information
echo ============================================
echo ℹ️  Docker Hub Repository:
echo https://hub.docker.com/u/%DOCKER_USERNAME%
echo.
echo Available images:
echo   🚗 %DOCKER_USERNAME%/%IMAGE_PREFIX%-sensor:latest
echo   📡 %DOCKER_USERNAME%/%IMAGE_PREFIX%-server:latest  
echo   🖥️ %DOCKER_USERNAME%/%IMAGE_PREFIX%-web:latest
echo ============================================

echo.
echo ℹ️  To run the complete system:
echo docker-compose -f docker-compose-dockerhub.yml up -d
echo.

REM Create docker-compose file for Docker Hub images
(
echo version: '3.8'
echo.
echo services:
echo   # MQTT Broker ^(Eclipse Mosquitto^)
echo   mosquitto:
echo     image: eclipse-mosquitto:2.0
echo     container_name: mosquitto-broker
echo     ports:
echo       - "1883:1883"
echo     volumes:
echo       - mosquitto_data:/mosquitto/data
echo       - mosquitto_log:/mosquitto/log
echo     restart: unless-stopped
echo     networks:
echo       - iot-network
echo.
echo   # Smart Parking Server ^(Subscriber^)
echo   server:
echo     image: %DOCKER_USERNAME%/%IMAGE_PREFIX%-server:latest
echo     container_name: parking-server
echo     depends_on:
echo       - mosquitto
echo     restart: unless-stopped
echo     networks:
echo       - iot-network
echo     environment:
echo       - PYTHONUNBUFFERED=1
echo.
echo   # Smart Parking Sensor ^(Publisher^)
echo   sensor:
echo     image: %DOCKER_USERNAME%/%IMAGE_PREFIX%-sensor:latest
echo     container_name: parking-sensor
echo     depends_on:
echo       - mosquitto
echo       - server
echo     restart: unless-stopped
echo     networks:
echo       - iot-network
echo     environment:
echo       - PYTHONUNBUFFERED=1
echo.
echo   # Web Dashboard
echo   web:
echo     image: %DOCKER_USERNAME%/%IMAGE_PREFIX%-web:latest
echo     container_name: parking-web
echo     ports:
echo       - "5000:5000"
echo     depends_on:
echo       - mosquitto
echo     restart: unless-stopped
echo     networks:
echo       - iot-network
echo     environment:
echo       - PYTHONUNBUFFERED=1
echo.
echo volumes:
echo   mosquitto_data:
echo     driver: local
echo   mosquitto_log:
echo     driver: local
echo.
echo networks:
echo   iot-network:
echo     driver: bridge
) > docker-compose-dockerhub.yml

echo ✅ Created docker-compose-dockerhub.yml for Docker Hub images
echo.
echo 🎉 Deployment complete!
echo.
pause
