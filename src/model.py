import os
import pandas as pd
import numpy as np
import psycopg2
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

def fetch_data_from_db(crypto_symbol='BTC'):
    """
    Fetches and merges time-series and sentiment data from the database.
    """
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("Error: DATABASE_URL environment variable is not set.")
        return pd.DataFrame()

    try:
        conn = psycopg2.connect(db_url)
        # Query to join the two tables
        query = f"""
        SELECT
            t.timestamp, t.close_price, t.volume, t.rsi_14, t.macd,
            t.bollinger_high, t.bollinger_low, t.atr, t.sma_50, t.ema_20,
            s.social_volume, s.social_sentiment_net, s.news_count, s.news_sentiment_avg
        FROM time_series_data t
        JOIN sentiment_features s ON t.timestamp = s.timestamp AND t.crypto_symbol = s.crypto_symbol
        WHERE t.crypto_symbol = '{crypto_symbol}'
        ORDER BY t.timestamp;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Failed to fetch data from database: {e}")
        return pd.DataFrame()

def preprocess_data(df, sequence_length=24, prediction_horizon=1):
    """
    Preprocesses the data for LSTM model training.
    """
    # 1. Handle missing values (simple forward fill)
    df.fillna(method='ffill', inplace=True)
    df.fillna(0, inplace=True) # Fill any remaining NaNs at the beginning

    # 2. Scale features
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df.drop('timestamp', axis=1))

    # 3. Create sequences
    X, y = [], []
    for i in range(len(scaled_data) - sequence_length - prediction_horizon + 1):
        X.append(scaled_data[i:(i + sequence_length)])
        y.append(scaled_data[i + sequence_length + prediction_horizon - 1, 0]) # Predicting 'close_price'

    return np.array(X), np.array(y), scaler

def build_lstm_model(input_shape):
    """
    Builds the LSTM model architecture.
    """
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(units=50, return_sequences=False),
        Dropout(0.2),
        Dense(units=25),
        Dense(units=1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def main():
    """
    Main function to orchestrate the model training pipeline.
    """
    print("--- Starting ML Model Training Pipeline ---")
    print("This script requires a populated database and the DATABASE_URL env var.")

    # 1. Fetch data
    data = fetch_data_from_db('BTC')
    if data.empty:
        print("No data fetched. Aborting training pipeline.")
        return

    print(f"Successfully fetched {len(data)} records from the database.")

    # 2. Preprocess data
    X, y, scaler = preprocess_data(data)
    if len(X) == 0:
        print("Not enough data to create sequences. Need more historical data.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    print(f"Data split into {len(X_train)} training samples and {len(X_test)} testing samples.")

    # 3. Build and train model
    model = build_lstm_model((X_train.shape[1], X_train.shape[2]))
    print("LSTM model built successfully.")

    print("Starting model training (mock run)...")
    # In a real scenario, you would run this:
    # history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), verbose=1)
    # For this script, we'll just print a success message.
    print("Model training would occur here.")

    # 4. Evaluate model
    print("Evaluating model (mock run)...")
    # loss = model.evaluate(X_test, y_test)
    # print(f"Test Loss: {loss}")
    print("Model evaluation would occur here.")

    print("--- ML Model Training Pipeline Finished ---")

if __name__ == '__main__':
    main()