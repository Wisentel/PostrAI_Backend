#!/bin/bash

# Test script for Render deployment
echo "Testing PostrAI Backend deployment..."

# Set environment variables like Render would
export PORT=10000
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Build and run the Docker container
echo "Building Docker image..."
docker build -t postrai-backend .

echo "Running container on port $PORT..."
docker run -p $PORT:$PORT \
    -e PORT=$PORT \
    -e PYTHONUNBUFFERED=1 \
    -e PYTHONDONTWRITEBYTECODE=1 \
    -e MONGODB_URI="$MONGODB_URI" \
    postrai-backend

echo "Container should be running on http://localhost:$PORT"
echo "Test endpoints:"
echo "  - Root: http://localhost:$PORT/"
echo "  - Health: http://localhost:$PORT/api/health" 