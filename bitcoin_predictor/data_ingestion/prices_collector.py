import os
import sys
import ccxt
import pandas as pd
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from bitcoin_predictor.storage.db_connection import get_db_connection

def fetch_historical_prices(exchange_name, symbol, timeframe, since):
    """Fetches historical OHLCV data from the specified exchange."""
    exchange = getattr(ccxt, exchange_name)()
    try:
        if exchange.has['fetchOHLCV']:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
    except Exception as e:
        print(f"Error fetching data from {exchange_name}: {e}")
    return None

def insert_prices_data(conn, df, exchange, pair):
    """Inserts market data into the prices table."""
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO prices (timestamp, exchange, pair, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (exchange, pair, timestamp) DO NOTHING;
                """,
                (row['timestamp'], exchange, pair, row['open'], row['high'], row['low'], row['close'], row['volume'])
            )
    conn.commit()

def main():
    """Main function to fetch and store market data."""
    exchange = 'kraken'
    symbol = 'BTC/USDT'
    timeframe = '1m'
    # Fetch data for the last 24 hours
    since = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)

    print(f"Fetching {symbol} data from {exchange.capitalize()}...")
    price_data = fetch_historical_prices(exchange, symbol, timeframe, since)

    if price_data is not None and not price_data.empty:
        print(f"Fetched {len(price_data)} data points.")
        conn = get_db_connection()
        if conn:
            insert_prices_data(conn, price_data, exchange, symbol)
            print("Market data inserted successfully.")
            conn.close()
            print("Database connection closed.")
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()