import asyncio
import json
import logging
import os
import sys
from functools import partial

# Add the shared directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared')))

from binance_ws import BinanceWSClient
from market_analyzer import MarketAnalyzer
from message_protocol import send_to_main

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Loads the configuration from config.json."""
    try:
        with open('market_agent/config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Please create it.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error("Error decoding config.json. Please check its format.")
        sys.exit(1)

async def report_callback(data: dict, main_server_url: str):
    """Callback function to send reports to the main server."""
    logger.info(f"Event triggered. Sending report to main server: {data}")
    send_to_main(data, main_server_url)

async def main():
    """Main function to run the Market Agent."""
    config = load_config()
    main_server_url = config.get("MAIN_SERVER_URL")
    symbols = config.get("BINANCE_SYMBOLS", [])

    if not all([main_server_url, symbols]):
        logger.error("Configuration is missing required fields (MAIN_SERVER_URL or BINANCE_SYMBOLS).")
        return

    logger.info("Market Agent started. Monitoring Binance WebSocket...")

    # Create a partial function for the report callback, pre-filling the server URL
    bound_report_callback = partial(report_callback, main_server_url=main_server_url)

    # Initialize the analyzer
    analyzer = MarketAnalyzer(config, bound_report_callback)

    # Initialize the WebSocket client with the analyzer's processing method as its callback
    ws_client = BinanceWSClient(symbols, analyzer.process_kline_data)

    try:
        await ws_client.start()
    except KeyboardInterrupt:
        logger.info("Market Agent shutting down.")
        ws_client.stop()
    except Exception as e:
        logger.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
        ws_client.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested.")