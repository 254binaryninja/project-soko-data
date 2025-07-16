# Project Soko Data

A real-time financial data processing system for the Nigeria Stock Exchange (NSE) with a Python scraper and Java API components.

## Project Structure

```
project-soko-data/
├── python-scrapper/          # Python-based NSE data scraper
│   ├── main.py              # Main application entry point
│   ├── fetcher.py           # HTTP client for web scraping
│   ├── parser.py            # HTML parser for NSE data
│   ├── streamer.py          # Redis streaming client
│   ├── scheduler.py         # Job scheduling
│   ├── config.py            # Configuration management
│   ├── requirements.txt     # Python dependencies
│   ├── pyproject.toml       # Project metadata
│   └── README.md            # Detailed scraper documentation
├── java-api/                # Java API (planned/in development)
└── docker-compose.yml       # Docker orchestration (planned)
```

## Components

### Python Scraper (`python-scrapper/`)
Real-time stock price scraper that:
- Monitors NSE website for price changes
- Publishes updates to Redis streams
- Provides efficient change detection
- Includes comprehensive error handling

**Technology Stack**: Python 3.12+, Redis, BeautifulSoup, Requests

### Java API (`java-api/`)
API service (planned) for:
- Consuming Redis streams
- Providing REST endpoints
- Data aggregation and analytics
- Client applications integration

## Quick Start

1. **Start Redis**:
   ```bash
   redis-server
   ```

2. **Run the Python scraper**:
   ```bash
   cd python-scrapper
   pip install -r requirements.txt
   python main.py
   ```

3. **Monitor the Redis stream**:
   ```bash
   redis-cli XREAD STREAMS nse:realtime $
   ```

## Development Status

- ✅ **Python Scraper**: Complete and functional
- 🚧 **Java API**: Planned/In Development  
- 🚧 **Docker Setup**: Planned
- 🚧 **Documentation**: In Progress

## Contributing

[Add contribution guidelines here]

## License

[Add license information here]
