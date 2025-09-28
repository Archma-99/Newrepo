import os
import sys
import requests
from datetime import datetime
import pytz

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from project.db.db_handler import connect_to_db

# Etherscan API details from environment variables
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

# A small selection of on-chain metrics to fetch
ONCHAIN_METRICS = {
    "eth_supply": {"module": "stats", "action": "ethsupply"},
    # In a real system, you might add:
    # "gas_price": {"module": "gastracker", "action": "gasoracle"},
}

def fetch_metric_from_etherscan(metric_name, params):
    """Fetches a single on-chain metric from the Etherscan API."""
    if not ETHERSCAN_API_KEY:
        # This is expected if the key isn't provided
        return None

    all_params = {**params, "apikey": ETHERSCAN_API_KEY}
    try:
        response = requests.get(ETHERSCAN_API_URL, params=all_params)
        response.raise_for_status()
        data = response.json()
        if data['status'] == '1':
            return data['result']
        else:
            print(f"Etherscan API error for {metric_name}: {data['message']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"HTTP error fetching {metric_name}: {e}")
        return None

def insert_onchain_data(conn, source, metric, value):
    """Inserts a single on-chain data point into the onchain_data table."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO onchain_data (timestamp, source, metric, value)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (source, metric, timestamp) DO NOTHING;
            """,
            (datetime.now(pytz.utc), source, metric, value)
        )
    conn.commit()

def main():
    """Main function to fetch and store on-chain data."""
    if not ETHERSCAN_API_KEY:
        print("Etherscan API key not set. Skipping on-chain data collection.")
        return

    print("Fetching on-chain data from Etherscan...")
    conn = connect_to_db()
    if not conn:
        print("Database connection failed. Aborting on-chain data ingestion.")
        return

    try:
        for metric_name, params in ONCHAIN_METRICS.items():
            value = fetch_metric_from_etherscan(metric_name, params)
            if value is not None:
                # Special handling for certain metrics, e.g., converting Wei to Ether
                if metric_name == 'eth_supply':
                    value = int(value) / 10**18

                insert_onchain_data(conn, 'Etherscan', metric_name, value)
                print(f"-> Successfully stored '{metric_name}': {value}")
    except Exception as e:
        print(f"An error occurred during on-chain data ingestion: {e}")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()