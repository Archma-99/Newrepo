from src.data_storage import store_data
from src.model import main as train_model

def main():
    """
    Main entry point for the Multi-Modal Crypto Prediction System.

    This script orchestrates the two main processes:
    1. Data Collection: Fetches and stores data from all sources.
    2. Model Training: Trains the predictive model on the collected data.
    """
    print("======================================================")
    print("  Multi-Modal Crypto Prediction System (v2.0)         ")
    print("======================================================")
    print("\nThis application requires several environment variables to be set:")
    print(" - For Database Connection: DATABASE_URL")
    print(" - For Reddit API: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT")
    print("\nSince these are not set, the script will demonstrate the execution flow")
    print("and show the error handling for missing credentials and connections.")
    print("-" * 54)

    # --- Step 1: Run the data collection and storage pipeline ---
    print("\n>>> STEP 1: Kicking off the data ingestion and storage process...")
    # In a real application, you might want to run this for multiple symbols.
    # For this demonstration, we'll just run it for BTC and ETH as before.
    try:
        store_data(crypto_symbol='BTC', crypto_pair='BTC/USDT')
        store_data(crypto_symbol='ETH', crypto_pair='ETH/USDT')
    except Exception as e:
        print(f"An error occurred during the data storage step: {e}")
    print(">>> Data ingestion and storage process finished.")


    # --- Step 2: Run the model training pipeline ---
    print("\n>>> STEP 2: Kicking off the model training pipeline...")
    try:
        train_model()
    except Exception as e:
        print(f"An error occurred during the model training step: {e}")
    print(">>> Model training pipeline finished.")

    print("\n======================================================")
    print("  Application run finished.                           ")
    print("======================================================")


if __name__ == '__main__':
    main()