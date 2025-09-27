-- Database schema for the Multi-Modal Crypto Prediction System

-- Table for quantitative features from time-series data
CREATE TABLE time_series_data (
    id SERIAL PRIMARY KEY,
    crypto_symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE UNIQUE NOT NULL,
    close_price NUMERIC NOT NULL,
    volume NUMERIC NOT NULL,
    rsi_14 NUMERIC,
    macd NUMERIC,
    bollinger_high NUMERIC,
    bollinger_low NUMERIC,
    atr NUMERIC,
    sma_50 NUMERIC,
    ema_20 NUMERIC
);

-- Table for qualitative features from unstructured data
CREATE TABLE sentiment_features (
    id SERIAL PRIMARY KEY,
    crypto_symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE UNIQUE NOT NULL,
    social_volume INT,
    social_sentiment_net NUMERIC,
    news_count INT,
    news_sentiment_avg NUMERIC,
    CONSTRAINT fk_time_series
        FOREIGN KEY(timestamp, crypto_symbol)
        REFERENCES time_series_data(timestamp, crypto_symbol)
        ON DELETE CASCADE
);

-- Create a composite index on time_series_data for faster lookups
CREATE INDEX idx_ts_crypto_timestamp ON time_series_data(crypto_symbol, timestamp DESC);

-- Create a composite index on sentiment_features for faster lookups
CREATE INDEX idx_sf_crypto_timestamp ON sentiment_features(crypto_symbol, timestamp DESC);