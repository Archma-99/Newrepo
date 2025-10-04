import time
import json
import logging
import os
import sys

# Add the shared directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared')))

from rss_parser import fetch_rss_feeds
from sentiment_analyzer import analyze_sentiment_with_ai
from message_protocol import send_to_main

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Loads the configuration from config.json."""
    try:
        with open('news_agent/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Please create it.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("Error decoding config.json. Please check its format.")
        sys.exit(1)

def main():
    """Main loop for the News Agent."""
    config = load_config()
    feed_urls = [config.get("BBC_RSS_FEED"), config.get("CNBC_RSS_FEED")]
    main_server_url = config.get("MAIN_SERVER_URL")

    if not all([feed_urls, main_server_url]):
        logger.error("Configuration is missing required fields (RSS feeds or main server URL).")
        return

    logger.info("News Agent started. Monitoring RSS feeds...")

    while True:
        try:
            # 1. Fetch articles
            articles = fetch_rss_feeds(feed_urls)
            logger.info(f"Fetched {len(articles)} new articles.")

            # 2. Analyze and report
            for article in articles:
                analysis_report = analyze_sentiment_with_ai(article)

                if analysis_report and analysis_report.get("impact") in ["medium", "high"]:
                    logger.info(f"High impact event detected: {analysis_report['details']['title']}")
                    # 3. Send to main server
                    send_to_main(analysis_report, main_server_url)

            # 4. Wait for the next cycle
            logger.info("Cycle complete. Waiting for 120 seconds...")
            time.sleep(120)

        except KeyboardInterrupt:
            logger.info("News Agent shutting down.")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
            time.sleep(60) # Wait a bit longer after an error

if __name__ == "__main__":
    main()