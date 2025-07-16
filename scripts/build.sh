#!/bin/bash
# Simple build script for NSE Scraper

echo "🐳 Building NSE Scraper with Docker Compose..."

# Build using docker-compose (recommended)
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "To run the scraper:"
    echo "  docker-compose up -d"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f nse-scraper"
else
    echo "❌ Build failed!"
    exit 1
fi
