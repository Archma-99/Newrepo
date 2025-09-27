import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

def fetch_and_analyze_news(crypto_symbol='BTC'):
    """
    Fetches news from RSS feeds, filters by a crypto symbol, and performs sentiment analysis.

    :param crypto_symbol: The crypto symbol to filter news for (e.g., 'BTC', 'ETH').
    :return: A dictionary containing the number of articles and the average sentiment score.
    """
    # List of relevant RSS feeds
    rss_feeds = [
        'https://cointelegraph.com/rss',
        'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'https://bitcoinmagazine.com/feed',
        'https://news.bitcoin.com/feed/',
        'https://cryptoslate.com/feed/',
    ]

    analyzer = SentimentIntensityAnalyzer()

    all_articles = []

    # 1. Fetch news from all feeds
    for url in rss_feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            all_articles.append({
                'title': entry.title,
                'summary': entry.get('summary', ''),
                'link': entry.link,
                'published': entry.get('published_parsed'),
            })

    # 2. Filter articles by crypto_symbol
    relevant_articles = [
        article for article in all_articles
        if crypto_symbol.lower() in article['title'].lower() or \
           crypto_symbol.lower() in article['summary'].lower()
    ]

    if not relevant_articles:
        return {'news_count': 0, 'news_sentiment_avg': 0.0}

    # 3. Perform sentiment analysis
    sentiments = []
    for article in relevant_articles:
        text_to_analyze = article['title'] + ". " + article['summary']
        sentiment = analyzer.polarity_scores(text_to_analyze)
        sentiments.append(sentiment['compound']) # Using compound score

    # 4. Aggregate results
    news_count = len(relevant_articles)
    news_sentiment_avg = sum(sentiments) / news_count if news_count > 0 else 0.0

    return {
        'news_count': news_count,
        'news_sentiment_avg': news_sentiment_avg
    }

if __name__ == '__main__':
    # Example usage:
    crypto = 'BTC'
    print(f"Fetching and analyzing news for {crypto}...")

    news_data = fetch_and_analyze_news(crypto_symbol=crypto)

    print("\n--- Aggregated News Sentiment ---")
    print(f"Number of relevant articles: {news_data['news_count']}")
    print(f"Average sentiment score: {news_data['news_sentiment_avg']:.4f}")

    crypto = 'ETH'
    print(f"\nFetching and analyzing news for {crypto}...")

    news_data = fetch_and_analyze_news(crypto_symbol=crypto)

    print("\n--- Aggregated News Sentiment ---")
    print(f"Number of relevant articles: {news_data['news_count']}")
    print(f"Average sentiment score: {news_data['news_sentiment_avg']:.4f}")