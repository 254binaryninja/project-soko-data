# fetcher.py

import time
import logging
from typing import Optional
import requests
import config

# Configure module-level logger
logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": f"Mozilla/5.0 (compatible; NSE-Scraper/1.0; +{config.URL})",
}

def fetch_html(url: str, timeout: float = 10.0, retries: int = 3, backoff: float = 2.0) -> Optional[str]:
    """
    Fetch HTML content from the given URL with retry logic.
    Returns the HTML text if successful, otherwise None.
    """
    headers = DEFAULT_HEADERS.copy()
    session = requests.Session()
    session.headers.update(headers)

    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.RequestException as e:
            logger.warning(f"Fetch attempt {attempt} failed: {e}")
            if attempt < retries:
                sleep_d = backoff ** attempt
                logger.info(f"Retrying in {sleep_d:.1f}s...")
                time.sleep(sleep_d)
            else:
                logger.error(f"All {retries} fetch attempts failed.")
    return None
