import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlertManager:
    """
    Handles the sending of alerts to specified channels (e.g., Telegram).
    """
    def __init__(self, config: dict):
        self.telegram_token = config.get("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = config.get("TELEGRAM_CHAT_ID")
        self.is_configured = False

        if "YOUR_TELEGRAM" not in self.telegram_token and self.telegram_chat_id:
            self.is_configured = True
            logger.info("Telegram alert manager configured.")
        else:
            logger.warning("Telegram token or chat ID is a placeholder. Alerts will be logged but not sent.")

    def send_alert(self, message: str, level: str = "info"):
        """
        Sends an alert. Currently supports Telegram.

        Args:
            message (str): The message to send.
            level (str): The alert level (e.g., 'info', 'high', 'critical'). Used for logging.
        """
        log_message = f"ALERT [{level.upper()}]: {message}"
        logger.info(log_message)

        if self.is_configured:
            self._send_telegram_message(message)
        else:
            logger.info("Alert not sent because Telegram is not configured. Message was logged.")

    def _send_telegram_message(self, message: str):
        """
        Sends a message to the configured Telegram chat.
        """
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown" # Allows for bold, italics, etc.
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info("Successfully sent alert to Telegram.")
        except requests.RequestException as e:
            logger.error(f"Failed to send alert to Telegram: {e}")