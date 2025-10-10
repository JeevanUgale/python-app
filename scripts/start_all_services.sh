#!/bin/bash

# Start all microservices
cd "$(dirname "$0")/.."

echo "Starting All Microservices..."
echo "===================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "Please update .env with your configuration before running services."
    echo "Press any key to continue..."
    read -n 1
fi

# Function to start a service in background
start_service() {
    local service_name=$1
    local script_name=$2
    
    echo "Starting $service_name..."
    ./scripts/$script_name &
    local pid=$!
    echo "$service_name started with PID: $pid"
    echo $pid > "/tmp/${service_name}_pid.txt"
    sleep 2
}

# Start services
start_service "User Service" "start_user_service.sh"
start_service "Web Frontend" "start_web_frontend.sh"

echo ""
echo "===================================="
echo "All services started!"
echo "===================================="
echo "User Service: http://localhost:5001"
echo "Web Frontend: http://localhost:5000"
echo ""
echo "To stop all services, run: ./scripts/stop_all_services.sh"
echo ""
echo "Press Ctrl+C to stop monitoring..."

# Wait and monitor
while true; do
    sleep 5
    echo "Services running... ($(date))"
done