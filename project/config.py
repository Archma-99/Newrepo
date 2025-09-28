import os
from dotenv import load_dotenv

def load_environment():
    """
    Loads environment variables from a .env file located in the project root.
    This function should be called once at the start of the application.
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)

# --- Call the function to load the environment variables ---
load_environment()

# --- Database Credentials ---
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")

# --- API Keys ---
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "bitcoin_predictor/v1.0")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- News Feeds ---
NEWS_FEEDS = {
    "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "CNBC Crypto": "https://www.cnbc.com/id/10000664/device/rss/rss.html"
}

def check_db_credentials():
    """Helper function to check if essential DB credentials are set."""
    return all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD])