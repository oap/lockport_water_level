#!/bin/bash

# Production deployment script for Water Level Dashboard

echo "🌊 Starting Water Level Dashboard deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start the container
echo "🔨 Building and starting the Water Level Dashboard..."
docker-compose up --build -d

# Wait for container to be ready
echo "⏳ Waiting for application to start..."
sleep 10

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Water Level Dashboard is now running!"
    echo "🌐 Access the dashboard at: http://localhost"
    echo "📊 The dashboard shows water levels and discharge data for Lockport area stations"
    echo ""
    echo "🔧 Management commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop:         docker-compose down"
    echo "  Restart:      docker-compose restart"
    echo "  Update data:  Visit http://localhost and click 'Update Data'"
else
    echo "❌ Failed to start the container. Check logs with: docker-compose logs"
    exit 1
fi
