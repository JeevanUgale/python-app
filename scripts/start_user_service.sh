#!/bin/bash

# Start User Service
cd "$(dirname "$0")/.."

echo "Starting User Service..."
echo "===================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "Please update .env with your configuration before running services."
fi

# Set PYTHONPATH to include the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the user service
cd services/user_service
python app.py