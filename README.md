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
   uv sync
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

We welcome contributions to Project Soko Data! Here's how you can help:

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/project-soko-data.git
   cd project-soko-data
   ```
3. **Set up the development environment**:
   ```bash
   cd python-scrapper
   uv sync  # Install all dependencies including dev tools
   ```

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards:
   - Use type hints throughout your code
   - Add comprehensive tests for new functionality
   - Follow existing code style and patterns
   - Update documentation as needed

3. **Run tests** to ensure everything works:
   ```bash
   cd python-scrapper
   uv run pytest -v # Run tests with coverage report
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

### Code Standards

- **Python**: Follow PEP 8 style guidelines
- **Type Hints**: All functions should have proper type annotations
- **Testing**: Maintain >90% test coverage
- **Documentation**: Update README and docstrings for new features
- **Error Handling**: Include proper error handling and logging

### Areas for Contribution

- 🐛 **Bug fixes**: Check existing issues
- ✨ **New features**: Parser improvements, additional data sources
- 📚 **Documentation**: Improve existing docs or add examples
- 🧪 **Testing**: Add more test cases or improve coverage
- 🔧 **DevOps**: Docker setup, CI/CD improvements
- 🚀 **Performance**: Optimization and efficiency improvements

### Reporting Issues

When reporting bugs or requesting features:
- Use the GitHub issue tracker
- Provide clear description and steps to reproduce
- Include relevant logs and error messages
- Specify your environment (Python version, OS, etc.)

### Questions?

Feel free to open an issue for discussion or reach out to the maintainers.

## License

[MIT License](LICENSE)

