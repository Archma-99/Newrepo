import ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime

def fetch_and_process_time_series_data(symbol='BTC/USDT', timeframe='1h', limit=100):
    """
    Fetches OHLCV data for a given symbol and calculates technical indicators.

    :param symbol: The trading pair symbol (e.g., 'BTC/USDT').
    :param timeframe: The timeframe for the OHLCV data (e.g., '1h', '15m').
    :param limit: The number of data points to fetch.
    :return: A pandas DataFrame with OHLCV data and technical indicators.
    """
    # 1. Fetch Data
    exchange = ccxt.kraken()  # Changed from binance to kraken
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    # 2. Convert to DataFrame
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    # 3. Calculate Technical Indicators
    # RSI (Relative Strength Index)
    df.ta.rsi(length=14, append=True)
    # MACD (Moving Average Convergence Divergence)
    df.ta.macd(append=True)
    # Bollinger Bands
    df.ta.bbands(length=20, append=True)
    # ATR (Average True Range)
    df.ta.atr(length=14, append=True)
    # SMA (Simple Moving Average)
    df.ta.sma(length=50, append=True)
    # EMA (Exponential Moving Average)
    df.ta.ema(length=20, append=True)

    # 4. Rename columns to match schema.sql
    df.rename(columns={
        'close': 'close_price',
        'RSI_14': 'rsi_14',
        'MACD_12_26_9': 'macd',
        'BBL_20_2.0': 'bollinger_low',
        'BBU_20_2.0': 'bollinger_high',
        'ATRr_14': 'atr',
        'SMA_50': 'sma_50',
        'EMA_20': 'ema_20'
    }, inplace=True)

    # Select and reorder columns to match the schema
    # We will add crypto_symbol later when inserting into the DB
    final_columns = [
        'close_price', 'volume', 'rsi_14', 'macd',
        'bollinger_high', 'bollinger_low', 'atr', 'sma_50', 'ema_20'
    ]
    # Filter out any columns that weren't generated (e.g., if data is too short)
    existing_columns = [col for col in final_columns if col in df.columns]

    return df[existing_columns]


if __name__ == '__main__':
    # Example usage:
    crypto_symbol = 'BTC/USDT'
    print(f"Fetching and processing data for {crypto_symbol}...")

    try:
        time_series_df = fetch_and_process_time_series_data(symbol=crypto_symbol, timeframe='1h', limit=200)

        # Display the resulting DataFrame
        print("\n--- Processed Time-Series Data ---")
        print("Shape:", time_series_df.shape)
        print("\nFirst 5 rows:")
        print(time_series_df.head())
        print("\nLast 5 rows:")
        print(time_series_df.tail())
        print("\nColumns:", time_series_df.columns.tolist())

    except Exception as e:
        print(f"An error occurred: {e}")