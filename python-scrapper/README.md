# NSE Real-time Stock Price Scraper

A Python application that scrapes real-time stock prices from the Nigeria Stock Exchange (NSE) and streams price changes to Redis for real-time consumption.

## Overview

This application continuously monitors stock prices from the NSE website (`https://afx.kwayisi.org/nse/`) and publishes only price changes to a Redis stream, making it efficient for real-time financial data processing.

## Architecture

The application consists of several modular components:

- **`fetcher.py`** - HTTP client with retry logic for fetching NSE web pages
- **`parser.py`** - HTML parser that extracts ticker symbols and prices from NSE tables
- **`streamer.py`** - Redis client that publishes price changes to Redis streams
- **`scheduler.py`** - Job scheduler that runs the scraping process at configurable intervals
- **`main.py`** - Main application entry point that orchestrates the scraping workflow
- **`config.py`** - Configuration management with environment variable support

## Features

- **Smart Change Detection**: Only publishes price updates when prices actually change
- **Redis Streams**: Uses Redis streams for efficient real-time data distribution
- **Automatic Retry Logic**: Built-in retry mechanism for network requests
- **Stream Management**: Automatic trimming of old entries to manage memory usage
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Type Safety**: Full type annotations for better code reliability
- **Connection Testing**: Validates Redis connectivity on startup

## Configuration

The application can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `STREAM_MAX_LENGTH` | `1000` | Maximum number of entries to keep in the stream |
| `TIMESTAMP_MS` | `False` | Use milliseconds for timestamps (set to "true" to enable) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ENV_MODE` | `development` | Environment mode |

## Installation

1. Ensure you have Python 3.12+ installed
2. Install dependencies:
   using uv:
   ```bash
   uv sync
   ```

## Dependencies

- `beautifulsoup4>=4.13.4` - HTML parsing
- `redis>=6.2.0` - Redis client
- `requests>=2.32.4` - HTTP requests
- `schedule>=1.2.2` - Job scheduling
-  `lxml`-Beautifulsoup backend

## Usage

1. **Start Redis** (if not already running):
   ```bash
   redis-server
   ```

2. **Run the scraper**:
   ```bash
   python main.py
   ```

The application will:
- Connect to Redis and test the connection
- Start scraping NSE prices every 5-15 seconds (randomized interval)
- Publish price changes to the `nse:realtime` Redis stream
- Continue running indefinitely until stopped

## Redis Stream Format

Price updates are published to the Redis stream with the following format:

```json
{
  "ticker": "STOCK_SYMBOL",
  "price": "123.45",
  "ts": "1642694400"
}
```

## Monitoring

The application provides detailed logging for:
- Connection status and errors
- Parsing results and warnings
- Price changes and publications
- Network retries and failures

## Error Handling

- **Network Issues**: Automatic retry with exponential backoff
- **Parse Errors**: Graceful handling of malformed HTML with detailed logging
- **Redis Failures**: Connection testing and clear error messages
- **Data Validation**: Robust validation of extracted price data

## Testing

The project includes a comprehensive test suite covering all modules and functionality.

### Test Structure

```
tests/
├── conftest.py          # Shared fixtures and configuration
├── test_parser.py       # Tests for NSE HTML parsing logic
├── test_fetcher.py      # Tests for HTTP request handling
├── test_streamer.py     # Tests for Redis streaming functionality
└── test_main.py         # Tests for main orchestration logic
```

### Running Tests

**Basic test execution:**
```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_parser.py

# Run specific test method
uv run pytest tests/test_parser.py::TestParseNSE::test_parse_valid_nse_table
```

**Coverage reports:**
```bash
# Run tests with coverage
uv run pytest --cov=. --cov-report=term-missing

# Generate HTML coverage report
uv run pytest --cov=. --cov-report=html
# View in browser: htmlcov/index.html
```

**Using Makefile (recommended):**
```bash
make test              # Basic test run
make test-verbose      # Verbose output
make test-coverage     # With coverage report
make ci-test          # CI-friendly (XML output)
```

### Test Categories

1. **Parser Tests** - Validate HTML parsing and data extraction
   - Edge cases: empty HTML, malformed tables
   - Data validation: price and change extraction
   - Type safety: proper float/None handling

2. **Fetcher Tests** - HTTP request handling and retry logic
   - Network error scenarios
   - Timeout handling
   - Retry mechanisms with exponential backoff

3. **Streamer Tests** - Redis functionality and data streaming
   - Connection handling
   - Price change detection and publishing
   - Message format validation
   - Stream management

4. **Main Tests** - Integration and orchestration
   - Full workflow testing
   - Error propagation
   - Component interaction

### Test Features

- **Comprehensive mocking**: No external dependencies during testing
- **Type safety**: Full type annotations in test data
- **Edge case coverage**: Network failures, malformed data, connection issues
- **CI/CD ready**: JUnit XML output and coverage reporting
- **Fast execution**: Isolated tests with mocked dependencies

### Development Testing

**Debug specific tests:**
```bash
# Run with debug output
uv run pytest -s -v

# Stop on first failure
uv run pytest -x

# Run only failed tests from last run
uv run pytest --lf

# Debug with Python debugger
uv run pytest --pdb tests/test_parser.py::test_specific_function
```

**Test-driven development:**
```bash
# Watch mode (requires pytest-watch)
ptw tests/

# Run specific test repeatedly during development
uv run pytest tests/test_parser.py -v --tb=short
```

## Development

The codebase follows Python best practices:
- Type hints throughout
- Comprehensive error handling
- Modular, testable design
- Clear separation of concerns
- Detailed documentation
- Full test coverage with pytest

### Development Workflow

1. **Setup development environment:**
   ```bash
   uv sync  # Install all dependencies including dev tools
   ```

2. **Run tests before changes:**
   ```bash
   make test-coverage
   ```

3. **Make your changes**

4. **Verify tests pass:**
   ```bash
   make test
   ```

5. **Check coverage:**
   ```bash
   make test-coverage
   # Aim for >90% coverage
   ```

## License

[Add your license information here]