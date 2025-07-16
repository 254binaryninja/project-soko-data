# Simple Docker Setup Guide

This guide shows how to run the NSE Scraper using Docker with `uv` package manager.

## 🚀 Quick Start

### 1. Build and Run Everything
```bash
# Build and start both Redis and scraper
docker-compose up -d

# View logs
docker-compose logs -f nse-scraper

# Stop everything
docker-compose down
```

### 2. Using Build Scripts
```bash
# Linux/Mac
./scripts/build.sh

# Windows
scripts\build.bat
```

## 📦 What's Included

### Services
- **Redis**: Stores the stock price streams
- **NSE Scraper**: Fetches and processes stock data

### Files
- `Dockerfile.simple`: Simple Docker image for the scraper
- `docker-compose.yml`: Runs Redis + Scraper together
- `scripts/build.sh`: Linux/Mac build script
- `scripts/build.bat`: Windows build script

## ⚙️ Configuration

The scraper uses these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://redis:6379` | Where to find Redis |
| `LOG_LEVEL` | `INFO` | How much logging to show |

## 🔍 Monitoring

### View What's Happening
```bash
# See all container status
docker-compose ps

# Follow scraper logs
docker-compose logs -f nse-scraper

# Follow Redis logs
docker-compose logs -f redis
```

### Check Redis Data
```bash
# Connect to Redis
docker exec -it nse-redis redis-cli

# See the latest stock prices
XREAD STREAMS nse:realtime $
```

## 🛠️ Development

### Make Changes and Rebuild
```bash
# Rebuild after code changes
docker-compose build nse-scraper

# Restart with new code
docker-compose restart nse-scraper
```

### Debug Mode
```bash
# Run scraper with debug logging
docker-compose run --rm -e LOG_LEVEL=DEBUG nse-scraper
```

## 🐛 Troubleshooting

### Common Commands
```bash
# Check if containers are running
docker ps

# Restart everything
docker-compose restart

# Clean up and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Common Issues
1. **"Redis connection failed"** - Make sure Redis is running: `docker-compose logs redis`
2. **"Build failed"** - Check if you have the latest `pyproject.toml` and `uv.lock` files
3. **"Permission denied"** - Make sure Docker is running and you have permissions

## 📚 Why UV?

UV is a fast Python package manager that:
- Installs dependencies much faster than pip
- Handles virtual environments automatically
- Works great with Docker
- Uses lock files for reproducible builds

That's it! Simple Docker setup for learning and development. 🎉
