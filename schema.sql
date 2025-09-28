-- Drop existing tables to ensure a clean slate
DROP TABLE IF EXISTS historical_prices, live_prices, onchain_data, news_feed, social_sentiment, predictions CASCADE;

-- Table for historical price data loaded from the CSV file
CREATE TABLE historical_prices (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL UNIQUE,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume NUMERIC
);

-- Table for live market data from the Binance API
CREATE TABLE live_prices (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    exchange TEXT NOT NULL,
    pair TEXT NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume NUMERIC,
    UNIQUE(exchange, pair, timestamp)
);

-- Table for on-chain data from Etherscan and other sources
CREATE TABLE onchain_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    source TEXT NOT NULL, -- e.g., 'Etherscan', 'Binance'
    metric TEXT NOT NULL, -- e.g., 'eth_supply', 'btc_inflow'
    value NUMERIC,
    UNIQUE(source, metric, timestamp)
);

-- Table for news articles from RSS feeds
CREATE TABLE news_feed (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    source TEXT NOT NULL, -- e.g., 'BBC', 'CNBC'
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    sentiment_score NUMERIC
);

-- Table for social media sentiment
CREATE TABLE social_sentiment (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    platform TEXT NOT NULL, -- e.g., 'Reddit', 'Twitter'
    content TEXT,
    sentiment_score NUMERIC,
    url TEXT UNIQUE
);

-- Table for model predictions
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    model_name TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    predicted_price NUMERIC,
    confidence NUMERIC,
    signal TEXT
);