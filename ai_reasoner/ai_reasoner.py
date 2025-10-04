import time
import json
import logging
import os
import sys
import requests
import random

# Add the shared directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared')))

from gemini_client import GeminiClient, format_ai_response
from message_protocol import send_to_main

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Loads the configuration from config.json."""
    try:
        with open('ai_reasoner/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Please create it.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("Error decoding config.json. Please check its format.")
        sys.exit(1)

def get_recent_events_from_main_server(server_url: str) -> list[dict]:
    """
    Fetches recent, high-impact events from the main server's cache.
    In a real system, the main server would have an endpoint like '/get_events'.
    """
    try:
        # This endpoint doesn't exist yet, so we mock the functionality.
        # response = requests.get(f"{server_url}/get_events?limit=10", timeout=5)
        # response.raise_for_status()
        # return response.json()
        logger.warning("Mocking the fetch of recent events from the main server.")
        return [
            {
                "type": "whale", "source": "WhaleAlert", "impact": "high",
                "event": "exchange_outflow", "details": {"amount_btc": 5000}
            },
            {
                "type": "news", "source": "BBC", "impact": "medium",
                "sentiment": "positive", "details": {"title": "Major bank announces Bitcoin ETF."}
            },
            {
                "type": "social", "source": "reddit", "impact": "neutral",
                "sentiment": "neutral", "details": {"btc_mentions": 150}
            }
        ] if random.random() > 0.3 else [] # Sometimes return no events
    except requests.RequestException as e:
        logger.error(f"Could not fetch recent events from main server: {e}")
        return []

def main():
    """Main loop for the AI Reasoner."""
    config = load_config()
    main_server_url = config.get("MAIN_SERVER_URL")
    api_key = config.get("GEMINI_API_KEY", "")
    interval = config.get("REASONING_INTERVAL_SECONDS", 1800)

    if not main_server_url:
        logger.error("Configuration is missing MAIN_SERVER_URL.")
        return

    # Initialize Gemini client
    gemini_client = GeminiClient(api_key)

    logger.info(f"AI Reasoner started. Will perform reasoning every {interval} seconds.")

    while True:
        try:
            # 1. Fetch recent data from the main server
            logger.info("Fetching recent events from main server...")
            recent_events = get_recent_events_from_main_server(main_server_url)

            if not recent_events:
                logger.info("No significant events to analyze in this cycle.")
            else:
                # 2. Get AI-driven analysis
                ai_prediction = gemini_client.get_ai_reasoning(recent_events)

                if ai_prediction:
                    # 3. Format and send the prediction back to the main server
                    report = format_ai_response(ai_prediction)
                    logger.info(f"AI reasoning complete. Prediction: {report['sentiment']}. Sending to main server...")
                    send_to_main(report, f"{main_server_url}/report")

            # 4. Wait for the next reasoning cycle
            logger.info(f"Cycle complete. Waiting for {interval} seconds...")
            time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("AI Reasoner shutting down.")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
            time.sleep(60)

if __name__ == "__main__":
    main()