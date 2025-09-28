import os
import sys
import requests
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from bitcoin_predictor.storage.db_connection import get_db_connection

# Etherscan API details
ETHERSCAN_API_KEY = os.environ.get("ETHERSCAN_API_KEY")
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

# Placeholder for metrics to be fetched
# For now, we'll use a simple example like total ether supply.
# In a real scenario, this would be expanded to include gas prices, transaction volumes, etc.
ONCHAIN_METRICS = {
    "eth_supply": {"module": "stats", "action": "ethsupply"},
    # Add other metrics here, e.g.,
    # "total_nodes": {"module": "stats", "action": "nodecount"},
}

def fetch_onchain_metric(metric_name, params):
    """Fetches a single on-chain metric from the Etherscan API."""
    if not ETHERSCAN_API_KEY:
        print("Etherscan API key is not set. Skipping on-chain data ingestion.")
        return None

    all_params = {**params, "apikey": ETHERSCAN_API_KEY}
    try:
        response = requests.get(ETHERSCAN_API_URL, params=all_params)
        response.raise_for_status()
        data = response.json()
        if data['status'] == '1':
            return data['result']
        else:
            print(f"Error from Etherscan API for {metric_name}: {data['message']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching on-chain data for {metric_name}: {e}")
        return None

def insert_onchain_data(conn, metric, value):
    """Inserts a single on-chain data point into the database."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO onchain (timestamp, metric, value)
            VALUES (%s, %s, %s)
            ON CONFLICT (metric, timestamp) DO NOTHING;
            """,
            (datetime.now(), metric, value)
        )
    conn.commit()

def main():
    """Main function to fetch and store on-chain data."""
    print("Fetching on-chain data...")
    conn = get_db_connection()
    if not conn:
        print("Database connection failed. Aborting on-chain data ingestion.")
        return

    for metric_name, params in ONCHAIN_METRICS.items():
        value = fetch_onchain_metric(metric_name, params)
        if value is not None:
            # The value for ethsupply is in Wei, convert to Ether for storage
            if metric_name == 'eth_supply':
                value = int(value) / 10**18

            insert_onchain_data(conn, metric_name, value)
            print(f"Successfully fetched and stored '{metric_name}': {value}")

    conn.close()
    print("Database connection closed.")

if __name__ == "__main__":
    main()