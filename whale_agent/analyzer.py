import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_transaction(transaction: dict) -> dict | None:
    """
    Analyzes a single whale transaction to determine its significance.

    Args:
        transaction (dict): A dictionary representing one transaction.

    Returns:
        dict | None: A formatted report dictionary or None if not significant.
    """
    if transaction.get("symbol") != "BTC" or not transaction.get("amount"):
        return None

    amount = transaction.get("amount", 0)
    from_owner_type = transaction.get("from", {}).get("owner_type")
    to_owner_type = transaction.get("to", {}).get("owner_type")

    event_type = "unknown"
    impact = "low"

    # Detect exchange inflow (potential sell pressure)
    if from_owner_type != "exchange" and to_owner_type == "exchange":
        event_type = "exchange_inflow"
        logging.info(f"Detected exchange inflow: {amount} BTC")

    # Detect exchange outflow (potential accumulation)
    elif from_owner_type == "exchange" and to_owner_type != "exchange":
        event_type = "exchange_outflow"
        logging.info(f"Detected exchange outflow: {amount} BTC")

    # Ignore exchange-to-exchange or unknown-to-unknown transfers
    else:
        logging.info(f"Ignoring non-impactful transfer: {from_owner_type} to {to_owner_type}")
        return None

    # Determine impact based on amount
    if amount >= 5000:
        impact = "high"
    elif amount >= 1000:
        impact = "medium"
    else:
        impact = "low"

    # We only care about medium or high impact events
    if impact in ["low"]:
        return None

    report = {
        "timestamp": datetime.utcfromtimestamp(transaction.get("timestamp")).isoformat() + "Z",
        "type": "whale",
        "source": "WhaleAlert",
        "event": event_type,
        "impact": impact,
        "details": {
            "amount_btc": amount,
            "amount_usd": transaction.get("amount_usd"),
            "from_address": transaction.get("from", {}).get("address"),
            "to_address": transaction.get("to", {}).get("address"),
            "transaction_hash": transaction.get("hash")
        },
        "confidence": 0.95 # High confidence as it's on-chain data
    }

    return report