import asyncio
import json
import logging
import websockets
import random
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BinanceWSClient:
    """
    A WebSocket client for streaming live data from Binance.
    This is a placeholder and will generate mock data.
    """
    def __init__(self, symbols: list[str], on_message_callback):
        self._symbols = [s.lower() for s in symbols]
        self._callback = on_message_callback
        self._base_url = "wss://stream.binance.com:9443/ws"
        self.running = False

    async def _run_mock(self):
        """Generates mock data instead of connecting to the real WebSocket."""
        logging.warning("WebSocket is in mock mode. Generating fake data.")
        base_prices = {"btcusdt": 70000, "ethusdt": 3500}

        while self.running:
            try:
                for symbol in self._symbols:
                    price = base_prices[symbol] * (1 + random.uniform(-0.005, 0.005))
                    volume = random.uniform(1, 10)

                    # Occasionally create a spike
                    if random.random() < 0.05:
                        price *= (1 + random.choice([-0.02, 0.02]))
                        volume *= 4

                    mock_data = {
                        "e": "kline",           # Event type
                        "E": int(time.time() * 1000), # Event time
                        "s": symbol.upper(),    # Symbol
                        "k": {
                            "t": int(time.time() * 1000) - 60000, # Kline start time
                            "T": int(time.time() * 1000),       # Kline close time
                            "s": symbol.upper(),
                            "i": "1m",              # Interval
                            "o": f"{price * 0.99:.2f}", # Open price
                            "c": f"{price:.2f}",        # Close price
                            "h": f"{price * 1.01:.2f}", # High price
                            "l": f"{price * 0.98:.2f}", # Low price
                            "v": f"{volume:.4f}",       # Base asset volume
                            "n": random.randint(50, 200), # Number of trades
                            "q": f"{price * volume:.2f}", # Quote asset volume
                        }
                    }
                    await self._callback(mock_data)
                await asyncio.sleep(2) # Send data every 2 seconds
            except Exception as e:
                logging.error(f"Error in mock data generation loop: {e}")
                await asyncio.sleep(5)

    async def start(self):
        """Starts the WebSocket connection (or the mock data generator)."""
        self.running = True
        # In a real implementation, you would use the commented-out block below.
        await self._run_mock()

        # --- REAL IMPLEMENTATION ---
        # stream_names = [f"{symbol}@kline_1m" for symbol in self._symbols]
        # url = f"{self._base_url}/{'/'.join(stream_names)}"
        # logging.info(f"Connecting to Binance WebSocket: {url}")
        #
        # while self.running:
        #     try:
        #         async with websockets.connect(url) as ws:
        #             logging.info("Successfully connected to Binance WebSocket.")
        #             while self.running:
        #                 message = await ws.recv()
        #                 data = json.loads(message)
        #                 await self._callback(data)
        #     except websockets.exceptions.ConnectionClosed:
        #         logging.warning("WebSocket connection closed. Reconnecting in 5 seconds...")
        #         await asyncio.sleep(5)
        #     except Exception as e:
        #         logging.error(f"An error occurred with the WebSocket: {e}")
        #         await asyncio.sleep(10)
        # --- END REAL IMPLEMENTATION ---

    def stop(self):
        """Stops the client."""
        self.running = False
        logging.info("WebSocket client stopping.")