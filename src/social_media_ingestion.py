import praw
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from datetime import datetime, timedelta

def fetch_and_analyze_reddit_data(crypto_symbol='BTC', time_window_hours=24):
    """
    Fetches recent Reddit posts for a crypto symbol and analyzes their sentiment.

    :param crypto_symbol: The crypto symbol to search for (e.g., 'BTC', 'ETH').
    :param time_window_hours: The number of hours to look back for posts.
    :return: A dictionary with social volume and net sentiment.
    """
    # --- Reddit API Credentials ---
    # For this script to work, you must set the following environment variables:
    # REDDIT_CLIENT_ID: Your Reddit application's client ID.
    # REDDIT_CLIENT_SECRET: Your Reddit application's client secret.
    # REDDIT_USER_AGENT: A descriptive user agent (e.g., 'CryptoSentimentScraper by u/YourUsername').

    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')

    if not all([client_id, client_secret, user_agent]):
        print("Error: Reddit API credentials not found in environment variables.")
        print("Please set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT.")
        return {'social_volume': 0, 'social_sentiment_net': 0.0}

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    except Exception as e:
        print(f"Failed to initialize Reddit API: {e}")
        return {'social_volume': 0, 'social_sentiment_net': 0.0}


    # Subreddits to search
    subreddits = ['CryptoCurrency', 'bitcoin', 'ethtrader', 'altcoin']
    search_query = f'"{crypto_symbol}"'

    analyzer = SentimentIntensityAnalyzer()

    all_posts = []
    positive_scores = 0
    negative_scores = 0
    neutral_count = 0

    cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)

    # 1. Fetch posts from subreddits
    for sub in subreddits:
        try:
            subreddit = reddit.subreddit(sub)
            # Using search, as it's more direct than iterating hot/new
            for submission in subreddit.search(search_query, sort='new', time_filter='day', limit=100):
                 all_posts.append(submission)
        except Exception as e:
            print(f"Could not access subreddit {sub}: {e}")
            continue

    if not all_posts:
        return {'social_volume': 0, 'social_sentiment_net': 0.0}

    # 2. Analyze sentiment
    for post in all_posts:
        text_to_analyze = post.title + ". " + post.selftext
        sentiment = analyzer.polarity_scores(text_to_analyze)

        if sentiment['compound'] > 0.05:
            positive_scores += 1
        elif sentiment['compound'] < -0.05:
            negative_scores += 1
        else:
            neutral_count += 1

    # 3. Aggregate results
    social_volume = len(all_posts)
    if social_volume == 0:
        social_sentiment_net = 0.0
    else:
        social_sentiment_net = (positive_scores - negative_scores) / social_volume

    return {
        'social_volume': social_volume,
        'social_sentiment_net': social_sentiment_net
    }

if __name__ == '__main__':
    # Example usage:
    print("--- Reddit Social Media Ingestion ---")
    print("This script requires Reddit API credentials set as environment variables:")
    print(" - REDDIT_CLIENT_ID")
    print(" - REDDIT_CLIENT_SECRET")
    print(" - REDDIT_USER_AGENT")
    print("-" * 35)

    # Note: This will likely return 0 unless you have set up your credentials.
    crypto = 'BTC'
    print(f"\nFetching and analyzing Reddit data for {crypto}...")
    reddit_data = fetch_and_analyze_reddit_data(crypto_symbol=crypto)
    print(f"Social Volume: {reddit_data['social_volume']}")
    print(f"Net Sentiment Score: {reddit_data['social_sentiment_net']:.4f}")

    crypto = 'ETH'
    print(f"\nFetching and analyzing Reddit data for {crypto}...")
    reddit_data = fetch_and_analyze_reddit_data(crypto_symbol=crypto)
    print(f"Social Volume: {reddit_data['social_volume']}")
    print(f"Net Sentiment Score: {reddit_data['social_sentiment_net']:.4f}")