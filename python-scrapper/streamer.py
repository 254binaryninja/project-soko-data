# streamer.py

import time
import logging
from typing import Dict, Optional, Tuple
import redis
from redis import Redis
from redis.exceptions import ConnectionError, RedisError
import config

logger = logging.getLogger(__name__)

class RedisStreamer:
    def __init__(self):
        self.r: Redis = redis.Redis.from_url(config.REDIS_URL)
        self.last_prices: Dict[str, float] = {}
        self._test_connection()
        logger.info(f"Connected to Redis: {config.REDIS_URL}")

    def _test_connection(self) -> None:
        """
        Test Redis connection and raise an exception if connection fails.
        """
        try:
            # Test the connection with a simple ping
            if not self.r.ping():
                raise ConnectionError("Redis ping failed")
            logger.info("Redis connection test successful")
        except (ConnectionError, RedisError, Exception) as e:
            logger.error(f"Failed to connect to Redis at {config.REDIS_URL}: {e}")
            raise ConnectionError(f"Redis connection failed: {e}") from e

    def publish_changes(self, data: Dict[str, Tuple[float, Optional[float]]]) -> None:
        """
        Compare incoming ticker-price data with cached prices,
        publish only on change, and trim the Redis stream.
        
        Args:
            data: Dict mapping ticker -> (current_price, price_change)
        """
        ts = int(time.time() * (1000 if config.TIMESTAMP_MS else 1))
        for ticker, (price, price_change) in data.items():
            last = self.last_prices.get(ticker)
            if last is None or price != last:
                # Create fields dict - Redis accepts string keys and values
                fields = {
                    "ticker": str(ticker),
                    "price": str(price),
                    "ts": str(ts)
                }
                
                # Add price change if available
                if price_change is not None:
                    fields["price_change"] = str(price_change)
                    fields["price_change_abs"] = str(abs(price_change))
                    fields["price_change_direction"] = "up" if price_change > 0 else "down" if price_change < 0 else "neutral"
                
                # Calculate percentage change if we have previous price
                if last is not None and last != 0:
                    calculated_change = price - last
                    pct_change = (calculated_change / last) * 100
                    fields["calculated_change"] = str(calculated_change)
                    fields["calculated_pct_change"] = str(round(pct_change, 4))
                
                # XADD with approximate trimming for efficiency
                self.r.xadd(
                    config.STREAM_NAME,
                    fields=fields,  # type: ignore[arg-type]
                    maxlen=config.STREAM_MAXLEN,
                    approximate=True
                )
                self.last_prices[ticker] = price
                
                change_info = f" (change: {price_change:+.2f})" if price_change is not None else ""
                logger.debug(f"Published update: {ticker} -> {price}{change_info}")
        # Optionally trim by time-based logic using XTRIM
        # e.g., remove entries older than an hour (commented out for simplicity)
        # self._trim_by_age()

    def _trim_by_age(self, min_age_sec: int = 3600) -> None:
        """
        Remove entries older than current_time - min_age_sec.
        Converts min-id based on timestamp in the ID.
        """
        threshold = int((time.time() - min_age_sec) * 1000 if config.TIMESTAMP_MS else 0)
        # ID format: "<ms_timestamp>-0"
        min_id = f"{threshold}-0"
        removed = self.r.xtrim(config.STREAM_NAME, minid=min_id)
        logger.info(f"Trimmed stream entries older than {min_age_sec}s: {removed} removed")

