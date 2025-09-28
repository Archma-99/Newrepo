DROP TABLE IF EXISTS prices, news, social_posts, onchain, predictions, system_logs CASCADE;

-- 1. Market prices (BTC/USDT etc.)
CREATE TABLE prices (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    exchange TEXT NOT NULL,            -- e.g., Binance, Coinbase
    pair TEXT NOT NULL,                -- e.g., BTC/USDT
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume NUMERIC,
    UNIQUE(exchange, pair, timestamp)
);

-- 2. News articles
CREATE TABLE news (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    source TEXT NOT NULL,              -- e.g., CNBC, CryptoNews
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    content TEXT,
    sentiment_score NUMERIC            -- -1 (negative) to +1 (positive)
);

-- 3. Social media posts (Twitter/Reddit)
CREATE TABLE social_posts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    platform TEXT NOT NULL,            -- Twitter, Reddit
    author TEXT,
    content TEXT,
    sentiment_score NUMERIC,
    url TEXT UNIQUE
);

-- 4. On-chain data
CREATE TABLE onchain (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    metric TEXT NOT NULL,              -- active_addresses, hashrate, tx_volume
    value NUMERIC,
    UNIQUE(metric, timestamp)
);

-- 5. Predictions
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    model_name TEXT NOT NULL,          -- e.g., LSTM, Transformer, Ensemble
    timeframe TEXT NOT NULL,           -- 1min, 5min, 1h, 1d
    predicted_price NUMERIC,
    confidence NUMERIC,                -- 0-1
    signal TEXT                        -- Buy, Sell, Hold
);

-- 6. System logs (optional, for debugging)
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level TEXT NOT NULL,               -- INFO, WARNING, ERROR
    message TEXT
);