import feedparser
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_rss_feeds(feed_urls: list[str]) -> list[dict]:
    """
    Fetches and parses multiple RSS feeds.

    Args:
        feed_urls (list[str]): A list of RSS feed URLs.

    Returns:
        list[dict]: A list of articles, where each article is a dictionary.
    """
    articles = []
    for url in feed_urls:
        try:
            logging.info(f"Fetching RSS feed from: {url}")
            feed = feedparser.parse(url)
            for entry in feed.entries:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.summary,
                    'published': entry.get('published', 'N/A'),
                    'source': feed.feed.title
                })
        except Exception as e:
            logging.error(f"Failed to fetch or parse feed from {url}: {e}")
    return articles