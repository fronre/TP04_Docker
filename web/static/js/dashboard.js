// Smart Parking Dashboard JavaScript

let updateInterval;
let connectionStatus = false;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    startDataUpdates();
});

// Start real-time data updates
function startDataUpdates() {
    updateDashboard();
    updateInterval = setInterval(updateDashboard, 2000); // Update every 2 seconds
}

// Update all dashboard components
function updateDashboard() {
    Promise.all([
        fetch('/api/stats').then(r => r.json()),
        fetch('/api/data').then(r => r.json()),
        fetch('/api/alerts').then(r => r.json()),
        fetch('/api/sensors').then(r => r.json())
    ])
    .then(([stats, data, alerts, sensors]) => {
        updateStatistics(stats);
        updateParkingGrid(data);
        updateAlerts(alerts);
        updateSensorsTable(sensors);
        updateConnectionStatus(stats.mqtt_connected);
    })
    .catch(error => {
        console.error('Error updating dashboard:', error);
        updateConnectionStatus(false);
    });
}

// Update statistics cards
function updateStatistics(stats) {
    document.getElementById('total-spots').textContent = stats.total_spots;
    document.getElementById('occupied-spots').textContent = stats.occupied_spots;
    document.getElementById('free-spots').textContent = stats.free_spots;
    document.getElementById('alert-count').textContent = stats.recent_alerts;
    
    // Update occupancy rate in title
    if (stats.total_spots > 0) {
        document.title = `Smart Parking (${stats.occupancy_rate}% occupied)`;
    }
}

// Update parking spots grid
function updateParkingGrid(data) {
    const grid = document.getElementById('parking-grid');
    grid.innerHTML = '';
    
    Object.values(data).forEach(spot => {
        const spotCard = createParkingSpotCard(spot);
        grid.appendChild(spotCard);
    });
}

// Create parking spot card
function createParkingSpotCard(spot) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4';
    
    const card = document.createElement('div');
    card.className = `parking-spot ${spot.is_occupied ? 'occupied' : 'free'}`;
    
    const icon = spot.is_occupied ? 'fa-car' : 'fa-square';
    const temp = spot.temperature_celsius ? `${spot.temperature_celsius}°C` : 'N/A';
    
    card.innerHTML = `
        <div class="spot-icon">
            <i class="fas ${icon}"></i>
        </div>
        <div class="spot-id">${spot.parking_spot_id}</div>
        <div class="sensor-id">${spot.sensor_id}</div>
        <div class="temperature">
            <i class="fas fa-thermometer-half me-1"></i>
            ${temp}
        </div>
        ${spot.is_occupied ? `
            <div class="mt-2">
                <small>
                    <i class="fas fa-clock me-1"></i>
                    ${spot.vehicle_duration_minutes || 0} min
                </small>
            </div>
        ` : ''}
    `;
    
    col.appendChild(card);
    return col;
}

// Update alerts list
function updateAlerts(alerts) {
    const alertsList = document.getElementById('alerts-list');
    alertsList.innerHTML = '';
    
    if (alerts.length === 0) {
        alertsList.innerHTML = '<p class="text-muted text-center">No recent alerts</p>';
        return;
    }
    
    // Show last 10 alerts
    alerts.slice(-10).reverse().forEach(alert => {
        const alertItem = createAlertItem(alert);
        alertsList.appendChild(alertItem);
    });
}

// Create alert item
function createAlertItem(alert) {
    const div = document.createElement('div');
    div.className = `alert-item ${alert.severity.toLowerCase()}`;
    
    const time = new Date(alert.timestamp).toLocaleTimeString();
    const icon = getAlertIcon(alert.type);
    
    div.innerHTML = `
        <div class="alert-time">
            <i class="fas fa-clock me-1"></i>
            ${time}
        </div>
        <div class="alert-message">
            <i class="fas ${icon} me-2"></i>
            ${alert.message}
        </div>
        <div class="alert-details">
            Sensor: ${alert.sensor_id} | Spot: ${alert.parking_spot_id}
        </div>
    `;
    
    return div;
}

// Get alert icon based on type
function getAlertIcon(type) {
    const icons = {
        'HIGH_TEMPERATURE': 'fa-thermometer-full',
        'LOW_BATTERY': 'fa-battery-quarter',
        'WEAK_SIGNAL': 'fa-wifi',
        'LONG_PARKING': 'fa-clock'
    };
    return icons[type] || 'fa-exclamation-circle';
}

// Update sensors table
function updateSensorsTable(sensors) {
    const table = document.getElementById('sensors-table');
    table.innerHTML = '';
    
    sensors.forEach(sensor => {
        const row = createSensorRow(sensor);
        table.appendChild(row);
    });
}

// Create sensor table row
function createSensorRow(sensor) {
    const row = document.createElement('tr');
    
    const statusBadge = sensor.is_occupied ? 
        '<span class="status-badge occupied">Occupied</span>' : 
        '<span class="status-badge free">Free</span>';
    
    const batteryIcon = getBatteryIcon(sensor.battery_level);
    const signalIcon = getSignalIcon(sensor.signal_strength);
    
    row.innerHTML = `
        <td>${sensor.sensor_id}</td>
        <td>${sensor.parking_spot_id}</td>
        <td>${statusBadge}</td>
        <td>${sensor.temperature_celsius || 'N/A'}°C</td>
        <td>
            <i class="fas ${batteryIcon} me-1"></i>
            ${sensor.battery_level || 'N/A'}%
        </td>
        <td>
            <i class="fas ${signalIcon} me-1"></i>
            ${sensor.signal_strength || 'N/A'} dBm
        </td>
        <td>
            ${sensor.location?.zone || 'N/A'}, Floor ${sensor.location?.floor || 'N/A'}
        </td>
        <td>
            <small class="text-muted">
                ${formatTime(sensor.last_seen)}
            </small>
        </td>
    `;
    
    return row;
}

// Get battery icon based on level
function getBatteryIcon(level) {
    if (level >= 75) return 'fa-battery-full';
    if (level >= 50) return 'fa-battery-three-quarters';
    if (level >= 25) return 'fa-battery-half';
    return 'fa-battery-quarter';
}

// Get signal icon based on strength
function getSignalIcon(strength) {
    if (strength >= -50) return 'fa-wifi';
    if (strength >= -70) return 'fa-wifi';
    return 'fa-wifi';
}

// Format time
function formatTime(timestamp) {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleTimeString();
}

// Update connection status
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    
    if (connected !== connectionStatus) {
        connectionStatus = connected;
        
        if (connected) {
            statusElement.className = 'badge bg-success';
            statusElement.innerHTML = '<i class="fas fa-circle me-1"></i>Connected';
        } else {
            statusElement.className = 'badge bg-danger';
            statusElement.innerHTML = '<i class="fas fa-circle me-1"></i>Disconnected';
        }
    }
}

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
