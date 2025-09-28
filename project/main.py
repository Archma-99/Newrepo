import sys
import os

# Add project root to Python path to ensure all modules are accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from project import config
from project.sources import binance_api, rss_feed, etherscan_api, reddit_api
from project.db import db_handler, load_historical_data

def run_data_pipeline():
    """
    Orchestrates the entire data ingestion pipeline.
    """
    print("--- Starting Bitcoin Data Prediction System ---")

    # --- Step 1: Set up the database ---
    print("\n[1/5] Setting up the database schema...")
    db_handler.setup_database()

    # --- Step 2: Load historical data (if available) ---
    print("\n[2/5] Loading historical data...")
    historical_data_path = os.path.join(os.path.dirname(__file__), 'data', 'bitcoin_history.csv')
    load_historical_data.load_historical_data(historical_data_path)

    # --- Step 3: Fetch live market prices ---
    print("\n[3/5] Fetching live market prices...")
    try:
        binance_api.main()
    except Exception as e:
        print(f"Error in Binance (Kraken) API collector: {e}")

    # --- Step 4: Fetch news and sentiment ---
    print("\n[4/5] Fetching news and sentiment...")
    try:
        rss_feed.main()
    except Exception as e:
        print(f"Error in RSS feed collector: {e}")

    # --- Step 5: Fetch on-chain and social data (will skip if keys are missing) ---
    print("\n[5/5] Fetching on-chain and social media data...")
    try:
        etherscan_api.main()
    except Exception as e:
        print(f"Error in Etherscan API collector: {e}")

    try:
        reddit_api.main()
    except Exception as e:
        print(f"Error in Reddit API collector: {e}")

    print("\n--- Data pipeline run complete. ---")

if __name__ == "__main__":
    # First, check if database credentials are provided in the .env file
    if not config.check_db_credentials():
        print("FATAL: Database credentials are not configured.")
        print("Please create a .env file in the project root with your NeonDB details.")
    else:
        run_data_pipeline()