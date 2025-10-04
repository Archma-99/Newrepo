import time
import json
import logging
import os
import sys

# Add the shared directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared')))

from whale_api import get_whale_transactions
from analyzer import analyze_transaction
from message_protocol import send_to_main

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Loads the configuration from config.json."""
    try:
        with open('whale_agent/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Please create it.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("Error decoding config.json. Please check its format.")
        sys.exit(1)

def main():
    """Main loop for the Whale Agent."""
    config = load_config()
    main_server_url = config.get("MAIN_SERVER_URL")
    api_key = config.get("WHALE_ALERT_API_KEY", "")

    if not main_server_url:
        logger.error("Configuration is missing MAIN_SERVER_URL.")
        return

    if "YOUR_API_KEY" in api_key:
        logger.warning("Whale Alert API key is a placeholder. The agent will use mocked data.")

    logger.info("Whale Agent started. Monitoring for large transactions...")

    while True:
        try:
            # 1. Fetch transactions from API
            # In a real scenario, you'd pass a start timestamp to avoid duplicates.
            response = get_whale_transactions(api_key, min_value=500000)

            if response and response.get("result") == "success":
                transactions = response.get("transactions", [])
                logger.info(f"Fetched {len(transactions)} transaction(s) from the API.")

                # 2. Analyze each transaction
                for tx in transactions:
                    analysis_report = analyze_transaction(tx)

                    # 3. Report if significant
                    if analysis_report:
                        logger.info(f"Significant whale event detected: {analysis_report['event']} of {analysis_report['details']['amount_btc']} BTC")
                        send_to_main(analysis_report, main_server_url)

            # 4. Wait for the next cycle (Whale Alert free tier has a 10-min cache)
            logger.info("Cycle complete. Waiting for 600 seconds...")
            time.sleep(600)

        except KeyboardInterrupt:
            logger.info("Whale Agent shutting down.")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
            time.sleep(60)

if __name__ == "__main__":
    main()