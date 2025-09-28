import os
import pandas as pd
from .db_handler import connect_to_db

def load_historical_data(file_path):
    """
    Loads historical data from a CSV file into the historical_prices table.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' was not found.")
        return

    print(f"Reading data from '{file_path}'...")
    try:
        df = pd.read_csv(file_path)
        # Basic data validation
        required_columns = {'Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume_(BTC)'}
        if not required_columns.issubset(df.columns):
            print(f"CSV file must contain the following columns: {required_columns}")
            return

        # Convert unix timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s', utc=True)
        # Rename volume column to match schema
        df.rename(columns={'Volume_(BTC)': 'volume'}, inplace=True)

        print(f"Found {len(df)} records to load.")

    except Exception as e:
        print(f"Failed to read or process CSV file: {e}")
        return

    conn = connect_to_db()
    if not conn:
        print("Could not connect to the database. Aborting data load.")
        return

    print("Inserting data into the historical_prices table... This may take a while.")
    try:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute(
                    """
                    INSERT INTO historical_prices (timestamp, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (timestamp) DO NOTHING;
                    """,
                    (row['Timestamp'], row['Open'], row['High'], row['Low'], row['Close'], row['volume'])
                )
        conn.commit()
        print("Historical data loaded successfully.")
    except Exception as e:
        print(f"An error occurred during data insertion: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == '__main__':
    # The path to the CSV file is relative to the project root
    csv_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bitcoin_history.csv')
    load_historical_data(csv_file_path)