#!/bin/bash

# Start Web Frontend Service
cd "$(dirname "$0")/.."

echo "Starting Web Frontend Service..."
echo "===================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "Please update .env with your configuration before running services."
fi

# Set PYTHONPATH to include the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the web frontend service
cd services/web_frontend
python app.py