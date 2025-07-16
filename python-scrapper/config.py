# config.py
import os

ENV_MODE = os.getenv("ENV_MODE", "development").lower()
# Scraper settings
URL = "https://afx.kwayisi.org/nse/"
FETCH_INTERVAL_MIN = 5      # minimum seconds between fetches
FETCH_INTERVAL_MAX = 15     # maximum seconds between fetches

# Redis settings
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
STREAM_NAME = "nse:realtime"

# Stream retention
# Keep only the latest MAXLEN events (approximate)
STREAM_MAXLEN = int(os.getenv("STREAM_MAX_LENGTH", 1000))        # roughly corresponds to ~1000 price changes

# Timestamp format: seconds since epoch
TIMESTAMP_MS = os.getenv("TIMESTAMP_MS", "False").lower() == "true"       # set True if you prefer milliseconds

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
