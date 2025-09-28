import os
import sys
import feedparser
from datetime import datetime
from time import mktime

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from bitcoin_predictor.storage.db_connection import get_db_connection
from bitcoin_predictor.processing.sentiment_analysis import get_sentiment_score

NEWS_FEEDS = {
    "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "CNBC Crypto": "https://www.cnbc.com/id/10000664/device/rss/rss.html"
}

def fetch_news(feed_url):
    """Parses an RSS feed and returns a list of news articles."""
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": datetime.fromtimestamp(mktime(entry.published_parsed))
        })
    return articles

def insert_news_data(conn, articles, source):
    """Inserts news data into the news table."""
    with conn.cursor() as cur:
        for article in articles:
            sentiment = get_sentiment_score(article['title'])
            cur.execute(
                """
                INSERT INTO news (timestamp, source, title, url, sentiment_score)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
                """,
                (article['published'], source, article['title'], article['link'], sentiment)
            )
    conn.commit()

def main():
    """Main function to fetch and store news data."""
    all_articles = []
    for source, url in NEWS_FEEDS.items():
        print(f"Fetching news from {source}...")
        articles = fetch_news(url)
        if articles:
            print(f"Fetched {len(articles)} articles.")
            # Store with the specific source name
            conn = get_db_connection()
            if conn:
                insert_news_data(conn, articles, source)
                print(f"News from {source} inserted successfully.")
                conn.close()
    print("Database connection closed after processing all feeds.")

if __name__ == "__main__":
    main()