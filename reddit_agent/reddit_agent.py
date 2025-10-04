import time
import json
import logging
import os
import sys

# Add the shared directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared')))

from reddit_scraper import get_reddit_client, scrape_subreddits
from sentiment_analyzer import analyze_reddit_sentiment
from message_protocol import send_to_main

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Loads the configuration from config.json."""
    try:
        with open('reddit_agent/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Please create it.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("Error decoding config.json. Please check its format.")
        sys.exit(1)

def main():
    """Main loop for the Reddit Agent."""
    config = load_config()
    main_server_url = config.get("MAIN_SERVER_URL")
    subreddits = config.get("SUBREDDITS", [])

    if not all([main_server_url, subreddits]):
        logger.error("Configuration is missing required fields (MAIN_SERVER_URL or SUBREDDITS).")
        return

    # Initialize Reddit client
    reddit_client = get_reddit_client(config)

    if reddit_client is None:
        logger.warning("Could not initialize Reddit client. Agent will run with mock data.")

    logger.info("Reddit Agent started. Monitoring subreddits...")

    while True:
        try:
            # 1. Scrape posts
            posts = scrape_subreddits(reddit_client, subreddits, limit=50)
            logger.info(f"Scraped {len(posts)} posts from {len(subreddits)} subreddits.")

            if not posts:
                logger.info("No posts scraped in this cycle.")
                time.sleep(300) # Wait longer if no posts found
                continue

            # 2. Analyze sentiment
            analysis_report = analyze_reddit_sentiment(posts)

            # 3. Report if significant
            if analysis_report and analysis_report.get("impact") in ["medium", "high"]:
                logger.info(f"Reddit sentiment event detected: {analysis_report['sentiment']}")
                send_to_main(analysis_report, main_server_url)

            # 4. Wait for the next cycle
            logger.info("Cycle complete. Waiting for 300 seconds...")
            time.sleep(300)

        except KeyboardInterrupt:
            logger.info("Reddit Agent shutting down.")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
            time.sleep(60)

if __name__ == "__main__":
    main()