import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_to_main(data: dict, main_url: str):
    """
    Sends data to the main server via HTTP POST.

    Args:
        data (dict): The JSON payload to send.
        main_url (str): The URL of the main server's reporting endpoint.
    """
    try:
        response = requests.post(main_url, json=data, timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        logging.info(f"Successfully sent data to {main_url}. Status: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send data to {main_url}: {e}")
        return False