#!/bin/bash

# Test Docker build and run script for PostrAI backend

echo "🐳 Building Docker image..."
docker build -t postrai-backend .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    
    echo "🚀 Starting container..."
    docker run -d \
        --name postrai-backend-test \
        -p 8000:8000 \
        -e MONGODB_URI="${MONGODB_URI:-mongodb+srv://athishrajesh:89GaXb80iCkmJ4QX@wisentel.4aeym5h.mongodb.net/?retryWrites=true&w=majority&appName=Wisentel}" \
        postrai-backend
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully!"
        echo "🌐 API should be available at: http://localhost:8000"
        echo "📖 API docs available at: http://localhost:8000/docs"
        echo ""
        echo "Testing health endpoint..."
        sleep 5
        
        # Test health endpoint
        response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health)
        if [ "$response" -eq 200 ]; then
            echo "✅ Health check passed!"
        else
            echo "❌ Health check failed (HTTP $response)"
        fi
        
        echo ""
        echo "To stop the container, run:"
        echo "docker stop postrai-backend-test"
        echo "docker rm postrai-backend-test"
    else
        echo "❌ Failed to start container"
    fi
else
    echo "❌ Docker build failed"
fi 