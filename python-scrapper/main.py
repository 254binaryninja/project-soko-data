from fetcher import fetch_html
from parser import parse_nse
from streamer import RedisStreamer
import scheduler, config, logging

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def job():
    """Main job function that fetches, parses, and streams NSE data"""
    logger = logging.getLogger(__name__)
    
    try:
        html = fetch_html(config.URL)
        if not html:
            logger.error("Fetch failed, skipping run")
            return
        
        data = parse_nse(html)
        if data:
            streamer = RedisStreamer()
            streamer.publish_changes(data)
            logger.info(f"Processed {len(data)} tickers")
        else:
            logger.warning("No data parsed from HTML")
    except Exception as e:
        logger.error(f"Error in scraping job: {e}", exc_info=True)

def main():
    """Main entry point for the application"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting NSE scraper...")
        scheduler.schedule_job(job)
    except KeyboardInterrupt:
        logger.info("NSE scraper stopped by user")
    except Exception as e:
        logger.error(f"NSE scraper failed: {e}")
        raise

if __name__ == "__main__":
    main()
