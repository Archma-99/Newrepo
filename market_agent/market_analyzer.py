import logging
from collections import deque
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MarketAnalyzer:
    """
    Analyzes market data streams to detect significant events like volatility or volume spikes.
    """
    def __init__(self, config: dict, report_callback):
        self.report = report_callback
        self.volatility_threshold = config.get("VOLATILITY_THRESHOLD", 0.01) # e.g., 1% change
        self.volume_spike_factor = config.get("VOLUME_SPIKE_FACTOR", 3.0) # e.g., 3x the average

        self.last_prices = {}
        self.volume_history = {} # { "BTCUSDT": deque([vol1, vol2,...], maxlen=20) }
        self.last_event_time = {} # To avoid spamming alerts

    def _update_volume_history(self, symbol, volume):
        """Updates the recent volume history for a symbol."""
        if symbol not in self.volume_history:
            self.volume_history[symbol] = deque(maxlen=20) # Store last 20 volumes
        self.volume_history[symbol].append(volume)

    def _get_avg_volume(self, symbol):
        """Calculates the average volume from the history."""
        history = self.volume_history.get(symbol)
        if not history:
            return 0
        return sum(history) / len(history)

    async def process_kline_data(self, data: dict):
        """
        Processes a single kline data point from the WebSocket stream.
        """
        try:
            kline = data.get('k', {})
            symbol = kline.get('s')
            close_price = float(kline.get('c'))
            volume = float(kline.get('v'))
            event_time = int(data.get('E')) / 1000 # Event time in seconds

            if not all([symbol, close_price, volume]):
                return

            self._check_volatility(symbol, close_price, event_time)
            self._check_volume_spike(symbol, volume, event_time)

            # Update state
            self.last_prices[symbol] = close_price
            self._update_volume_history(symbol, volume)

        except (KeyError, ValueError, TypeError) as e:
            logging.error(f"Error processing kline data: {e} - Data: {data}")

    def _check_volatility(self, symbol, current_price, event_time):
        """Checks for a significant price change."""
        last_price = self.last_prices.get(symbol)
        if last_price is None:
            return # Not enough data yet

        price_change_pct = abs((current_price - last_price) / last_price)

        if price_change_pct >= self.volatility_threshold:
            # Throttle alerts to once every 60 seconds per symbol
            if event_time - self.last_event_time.get(f"{symbol}_volatility", 0) < 60:
                return

            self.last_event_time[f"{symbol}_volatility"] = event_time

            change_str = f"{'+' if current_price > last_price else ''}{price_change_pct:.2%}"
            report = self._create_report(
                symbol, "volatility_spike", "high",
                f"Price changed by {change_str} in 1 minute.",
                {"price_change_percent": price_change_pct, "current_price": current_price}
            )
            asyncio.create_task(self.report(report))


    def _check_volume_spike(self, symbol, current_volume, event_time):
        """Checks for a significant volume spike."""
        avg_volume = self._get_avg_volume(symbol)
        if avg_volume == 0:
            return # Not enough data yet

        if current_volume > avg_volume * self.volume_spike_factor:
            # Throttle alerts
            if event_time - self.last_event_time.get(f"{symbol}_volume", 0) < 120:
                return

            self.last_event_time[f"{symbol}_volume"] = event_time

            factor = current_volume / avg_volume
            report = self._create_report(
                symbol, "volume_spike", "medium",
                f"Volume spiked {factor:.1f}x above average.",
                {"current_volume": current_volume, "average_volume": avg_volume}
            )
            asyncio.create_task(self.report(report))

    def _create_report(self, symbol, event, impact, comment, details_extra):
        """Creates a standardized JSON report."""
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": "market",
            "source": "Binance",
            "event": event,
            "impact": impact,
            "details": {
                "symbol": symbol,
                "comment": comment,
                **details_extra
            },
            "confidence": 0.90
        }
        logging.info(f"Generated market event report: {report}")
        return report

# Need to import asyncio to use create_task
import asyncio