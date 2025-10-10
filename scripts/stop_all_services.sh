#!/bin/bash

# Stop all microservices
echo "Stopping All Microservices..."
echo "===================================="

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file="/tmp/${service_name}_pid.txt"
    
    if [ -f $pid_file ]; then
        local pid=$(cat $pid_file)
        if ps -p $pid > /dev/null 2>&1; then
            echo "Stopping $service_name (PID: $pid)..."
            kill $pid
            rm $pid_file
        else
            echo "$service_name is not running"
            rm -f $pid_file
        fi
    else
        echo "No PID file found for $service_name"
    fi
}

# Stop services
stop_service "User Service"
stop_service "Web Frontend"

# Kill any remaining processes
echo "Cleaning up remaining processes..."
pkill -f "services/user_service/app.py" 2>/dev/null
pkill -f "services/web_frontend/app.py" 2>/dev/null

echo "All services stopped!"