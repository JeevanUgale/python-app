#!/bin/bash

# Health check script for all services
echo "Health Check for Microservices"
echo "===================================="

check_service() {
    local service_name=$1
    local url=$2
    
    echo -n "Checking $service_name... "
    
    if curl -s "$url/health" > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy"
    fi
}

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set default ports if not specified
USER_SERVICE_PORT=${USER_SERVICE_PORT:-5001}
WEB_FRONTEND_PORT=${WEB_FRONTEND_PORT:-5000}

# Check services
check_service "User Service" "http://localhost:$USER_SERVICE_PORT"
check_service "Web Frontend" "http://localhost:$WEB_FRONTEND_PORT"

echo ""
echo "Service URLs:"
echo "User Service: http://localhost:$USER_SERVICE_PORT"
echo "Web Frontend: http://localhost:$WEB_FRONTEND_PORT"