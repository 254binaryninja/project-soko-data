# parser.py

import logging
from typing import Dict, Tuple, Optional
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

def parse_nse(html: str) -> Dict[str, Tuple[float, Optional[float]]]:
    """
    Parse the NSE page HTML and return a mapping of ticker -> (price, change).

    Args:
        html (str): Raw HTML content of the NSE page.

    Returns:
        Dict[str, Tuple[float, Optional[float]]]: A mapping from ticker symbol to 
        (current_price, price_change). price_change can be None if not available.
    """
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
    if not tables:
        logger.error("No <table> elements found.")
        return {}

    # Heuristic: choose the table with the most rows (full NSE)
    table = max(
        (tbl for tbl in tables if isinstance(tbl, Tag)),
        key=lambda tbl: len(tbl.select("tbody tr")),
        default=None
    )
    if table is None:
        logger.error("Could not locate the NSE list table.")
        return {}

    data: Dict[str, Tuple[float, Optional[float]]] = {}
    for idx, row in enumerate(table.select("tbody tr"), start=1):
        cells = row.find_all("td")
        if len(cells) < 5:
            logger.debug(f"Skipping row {idx}: only {len(cells)} cells")
            continue
            
        ticker = cells[0].get_text(strip=True)
        price_text = cells[3].get_text(strip=True).replace(",", "")
        
        # Extract price change from the 5th column (index 4)
        change_text = cells[4].get_text(strip=True) if len(cells) > 4 else ""

        if not ticker or not price_text:
            logger.debug(f"Row {idx} skipped: empty ticker or price")
            continue

        try:
            price = float(price_text)
            
            # Parse price change (can be +0.05, -0.10, or empty/dash)
            price_change: Optional[float] = None
            if change_text and change_text not in ["—", "-", ""]:
                # Remove any non-numeric characters except +, -, and decimal point
                clean_change = change_text.replace("+", "").replace(",", "").strip()
                if clean_change:
                    try:
                        price_change = float(clean_change)
                    except ValueError:
                        logger.debug(f"Could not parse change '{change_text}' for {ticker}")
            
            data[ticker] = (price, price_change)
            logger.debug(f"Parsed: {ticker} -> price: {price}, change: {price_change}")
            
        except ValueError:
            logger.warning(f"Row {idx} ticker {ticker}: invalid price '{price_text}'")
            continue

    logger.info(f"Parsed {len(data)} tickers from NSE table.")
    return data
