import os
import psycopg2
import pandas as pd
from datetime import datetime

# Import ingestion functions from other modules
from data_ingestion import fetch_and_process_time_series_data
from news_ingestion import fetch_and_analyze_news
from social_media_ingestion import fetch_and_analyze_reddit_data

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    return psycopg2.connect(db_url)

def store_data(crypto_symbol='BTC', crypto_pair='BTC/USDT', timeframe='1h'):
    """
    Orchestrates fetching, processing, and storing data from all sources.
    """
    print(f"--- Starting data storage process for {crypto_symbol} ---")

    # 1. Fetch all data
    print("Fetching time-series data...")
    ts_df = fetch_and_process_time_series_data(symbol=crypto_pair, timeframe=timeframe, limit=24) # Fetch last 24 hours
    if ts_df.empty:
        print("No time-series data fetched. Aborting.")
        return

    print("Fetching news data...")
    news_data = fetch_and_analyze_news(crypto_symbol=crypto_symbol)

    print("Fetching social media data...")
    social_data = fetch_and_analyze_reddit_data(crypto_symbol=crypto_symbol)

    # 2. Connect to the database
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")
        return

    # 3. Insert data into tables
    for timestamp, row in ts_df.iterrows():
        # Insert into time_series_data
        try:
            cur.execute(
                """
                INSERT INTO time_series_data (crypto_symbol, timestamp, close_price, volume, rsi_14, macd, bollinger_high, bollinger_low, atr, sma_50, ema_20)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (timestamp, crypto_symbol) DO NOTHING;
                """,
                (
                    crypto_symbol, timestamp, row['close_price'], row['volume'],
                    row.get('rsi_14'), row.get('macd'), row.get('bollinger_high'),
                    row.get('bollinger_low'), row.get('atr'), row.get('sma_50'), row.get('ema_20')
                )
            )

            # Insert into sentiment_features
            # We use the same aggregated sentiment for each of the recent time intervals
            cur.execute(
                """
                INSERT INTO sentiment_features (crypto_symbol, timestamp, social_volume, social_sentiment_net, news_count, news_sentiment_avg)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (timestamp, crypto_symbol) DO NOTHING;
                """,
                (
                    crypto_symbol, timestamp, social_data['social_volume'],
                    social_data['social_sentiment_net'], news_data['news_count'],
                    news_data['news_sentiment_avg']
                )
            )
        except Exception as e:
            print(f"Error inserting data for timestamp {timestamp}: {e}")
            conn.rollback() # Rollback on error
            continue

    # 4. Commit and close
    conn.commit()
    cur.close()
    conn.close()
    print("--- Data storage process completed successfully. ---")

if __name__ == '__main__':
    print("--- Data Storage Orchestrator ---")
    print("This script fetches data from all sources and stores it in the database.")
    print("It requires the following environment variables:")
    print(" - DATABASE_URL: For connecting to the PostgreSQL database.")
    print(" - REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT: For social media data.")
    print("-" * 35)

    # Note: This will fail if DATABASE_URL is not set.
    # The Reddit part will return zeros if its credentials are not set.
    store_data(crypto_symbol='BTC', crypto_pair='BTC/USDT')
    store_data(crypto_symbol='ETH', crypto_pair='ETH/USDT')