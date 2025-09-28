import os
import sys
import feedparser
from datetime import datetime
from time import mktime
import pytz

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from project.db.db_handler import connect_to_db
from project.utils.sentiment import get_sentiment_score

NEWS_FEEDS = {
    "BBC Business": "http://feeds.bbci.co.uk/news/business/rss.xml",
    "CNBC Crypto": "https://www.cnbc.com/id/10000664/device/rss/rss.html"
}

def fetch_news_from_feed(feed_url):
    """Parses an RSS feed and returns a list of news articles."""
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        # Ensure the published time is timezone-aware (UTC)
        published_time = datetime.fromtimestamp(mktime(entry.published_parsed), tz=pytz.utc)
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "published": published_time
        })
    return articles

def insert_news_data(conn, articles, source):
    """Inserts news data into the news_feed table."""
    with conn.cursor() as cur:
        for article in articles:
            sentiment = get_sentiment_score(article['title'])
            cur.execute(
                """
                INSERT INTO news_feed (timestamp, source, title, url, sentiment_score)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
                """,
                (article['published'], source, article['title'], article['link'], sentiment)
            )
    conn.commit()

def main():
    """Main function to fetch and store news data from all feeds."""
    print("Fetching news from RSS feeds...")
    conn = connect_to_db()
    if not conn:
        print("Database connection failed. Aborting news ingestion.")
        return

    try:
        for source, url in NEWS_FEEDS.items():
            print(f"-> Processing feed: {source}")
            articles = fetch_news_from_feed(url)
            if articles:
                insert_news_data(conn, articles, source)
                print(f"    Fetched and stored {len(articles)} articles.")
            else:
                print(f"    No articles found for {source}.")
    except Exception as e:
        print(f"An error occurred during news ingestion: {e}")
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()