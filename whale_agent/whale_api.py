import requests
import logging
import random
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Known exchange addresses (placeholders)
KNOWN_EXCHANGES = {
    "binance_hot_wallet": "bc1qgdjqv0av3q56jvd82tkdjpy7gdp9ut8tlqmgrpmv24sq90ecnvqqjwvw97",
    "coinbase_cold_storage": "3D2oetdNuZUqQHPJmcMDD2hkzrs5F6SK3f",
    "kraken_deposit_address": "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"
}

def get_whale_transactions_mock(api_key: str) -> dict:
    """
    Mocks a call to the Whale Alert API.
    In a real scenario, this would make an HTTP request to the actual API.

    Args:
        api_key (str): The API key for the service (unused in mock).

    Returns:
        dict: A mock API response containing transaction data.
    """
    if "YOUR_API_KEY" in api_key:
        logging.warning("Using placeholder API key for Whale Alert. Mocking API response.")

    # Simulate a random whale transaction
    mock_transaction = {
        "result": "success",
        "count": 1,
        "transactions": [
            {
                "blockchain": "bitcoin",
                "symbol": "BTC",
                "id": f"mock_tx_{random.randint(10000, 99999)}",
                "transaction_type": "transfer",
                "hash": f"mock_hash_{random.randint(10000, 99999)}",
                "from": {
                    "address": f"unknown_whale_{random.randint(1, 100)}",
                    "owner_type": "private_key"
                },
                "to": {
                    "address": random.choice(list(KNOWN_EXCHANGES.values())),
                    "owner_type": "exchange"
                },
                "timestamp": datetime.utcnow().timestamp(),
                "amount": random.choice([500, 1200, 3000, 5500]),
                "amount_usd": random.choice([35000000, 84000000, 210000000, 385000000])
            }
        ]
    }

    # Randomly simulate an exchange outflow
    if random.random() > 0.5:
        tx = mock_transaction["transactions"][0]
        tx["from"], tx["to"] = tx["to"], tx["from"] # Swap from and to
        tx["from"]["owner_type"] = "exchange"
        tx["to"]["owner_type"] = "private_key"

    logging.info("Fetched mock whale transaction data.")
    return mock_transaction

def get_whale_transactions(api_key: str, min_value: int = 500000) -> dict:
    """
    Fetches large transactions from the Whale Alert API.
    This is a placeholder for the actual implementation.

    Args:
        api_key (str): Your Whale Alert API key.
        min_value (int): The minimum USD value of transactions to return.

    Returns:
        dict: The API response from Whale Alert.
    """
    # This is where the actual API call would go.
    # For now, we'll just return the mocked data.
    logging.info(f"Pretending to call Whale Alert API with key: {api_key[:5]}... and min_value: ${min_value}")
    return get_whale_transactions_mock(api_key)