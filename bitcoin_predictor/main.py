import sys
import os

# Add project root to the Python path to allow for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bitcoin_predictor.data_ingestion import prices_collector, news_collector, onchain_collector, social_collector
from bitcoin_predictor import config

def run_all_collectors():
    """
    Runs all data ingestion modules sequentially.
    """
    print("--- Starting Data Ingestion ---")

    # 1. Ingest Market Prices
    try:
        print("\n[1/4] Ingesting Market Prices...")
        prices_collector.main()
    except Exception as e:
        print(f"Error in prices_collector: {e}")

    # 2. Ingest News Data
    try:
        print("\n[2/4] Ingesting News Data...")
        news_collector.main()
    except Exception as e:
        print(f"Error in news_collector: {e}")

    # 3. Ingest On-Chain Data (will skip if API key is not set)
    try:
        print("\n[3/4] Ingesting On-Chain Data...")
        onchain_collector.main()
    except Exception as e:
        print(f"Error in onchain_collector: {e}")

    # 4. Ingest Social Media Data (will skip if API keys are not set)
    try:
        print("\n[4/4] Ingesting Social Media Data...")
        social_collector.main()
    except Exception as e:
        print(f"Error in social_collector: {e}")

    print("\n--- Data Ingestion Complete ---")


if __name__ == "__main__":
    # This check ensures that the config variables are loaded before they are used
    if not all([config.DB_HOST, config.DB_USER, config.DB_PASSWORD, config.DB_NAME]):
        print("Database credentials are not fully configured. Please check your .env file.")
    else:
        run_all_collectors()