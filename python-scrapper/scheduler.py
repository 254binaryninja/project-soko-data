# scheduler.py

import time
import schedule
import logging
from typing import Callable

logger = logging.getLogger(__name__)

def schedule_job(func: Callable) -> None:
    """
    Schedule the given function to run every FETCH_INTERVAL_MIN to
    FETCH_INTERVAL_MAX seconds, indefinitely.
    """
    from config import FETCH_INTERVAL_MIN, FETCH_INTERVAL_MAX

    logger.info(
        f"Scheduling job to run every {FETCH_INTERVAL_MIN} -- {FETCH_INTERVAL_MAX} seconds."
    )
    schedule.every(FETCH_INTERVAL_MIN).to(FETCH_INTERVAL_MAX).seconds.do(func)

    while True:
        schedule.run_pending()
        time.sleep(1)
