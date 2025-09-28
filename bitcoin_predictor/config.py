import os
from dotenv import load_dotenv

# Load environment variables from a .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Database Credentials
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")

# Etherscan API Key
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

# Reddit API Credentials
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# News Feeds
NEWS_FEEDS = {
    "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "CNBC Crypto": "https://www.cnbc.com/id/10000664/device/rss/rss.html"
}

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")