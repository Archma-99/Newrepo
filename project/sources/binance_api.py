import os
import sys
import ccxt
import pandas as pd
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from project.db.db_handler import connect_to_db

def fetch_live_prices(exchange_name='kraken', symbol='BTC/USDT', timeframe='1m', limit=100):
    """
    Fetches the most recent OHLCV data from the specified exchange.
    Using Kraken as a stand-in for Binance due to API restrictions.
    """
    exchange = getattr(ccxt, exchange_name)()
    try:
        if exchange.has['fetchOHLCV']:
            # Fetch the last `limit` candles
            since = exchange.parse8601((datetime.utcnow() - timedelta(minutes=limit)).isoformat())
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)

            if not ohlcv:
                print(f"No data returned from {exchange_name} for {symbol}.")
                return None

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
            return df
    except Exception as e:
        print(f"Error fetching live data from {exchange_name}: {e}")
    return None

def insert_live_prices(conn, df, exchange, pair):
    """Inserts live market data into the live_prices table."""
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO live_prices (timestamp, exchange, pair, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (exchange, pair, timestamp) DO NOTHING;
                """,
                (row['timestamp'], exchange, pair, row['open'], row['high'], row['low'], row['close'], row['volume'])
            )
    conn.commit()

def main():
    """Main function to fetch and store live market data."""
    exchange_name = 'kraken' # Using Kraken as a substitute for Binance
    symbol = 'BTC/USDT'

    print(f"Fetching live prices for {symbol} from {exchange_name.capitalize()}...")
    price_data = fetch_live_prices(exchange_name, symbol, limit=10) # Fetch last 10 minutes

    if price_data is not None and not price_data.empty:
        print(f"Fetched {len(price_data)} recent data points.")
        conn = connect_to_db()
        if conn:
            try:
                insert_live_prices(conn, price_data, exchange_name, symbol)
                print("Live price data inserted successfully.")
            except Exception as e:
                print(f"Error inserting live prices: {e}")
            finally:
                conn.close()
                print("Database connection closed.")
    else:
        print("No live price data fetched.")

if __name__ == "__main__":
    main()