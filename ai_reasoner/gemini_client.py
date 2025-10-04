import os
import json
import logging
import random
from datetime import datetime

# In a real scenario, you would import the actual client:
# import google.generativeai as genai
from prompt_templates import get_reasoning_prompt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiClient:
    """
    A client for interacting with Google's Gemini AI.
    This version uses mocked data for demonstration purposes.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.is_configured = False
        if "YOUR_GEMINI_API_KEY" not in self.api_key:
            # In a real implementation:
            # genai.configure(api_key=self.api_key)
            # self.model = genai.GenerativeModel('gemini-pro')
            self.is_configured = True
            logging.info("Gemini client configured with a real API key.")
        else:
            logging.warning("Using a placeholder Gemini API key. The client will return mock predictions.")

    def get_ai_reasoning(self, recent_events: list[dict]) -> dict | None:
        """
        Queries the AI with recent event data and returns a structured prediction.

        Args:
            recent_events (list[dict]): A list of events from the main server.

        Returns:
            dict | None: A dictionary containing the AI's prediction, or None on failure.
        """
        prompt = get_reasoning_prompt(recent_events)
        logging.info("Generated AI prompt. Querying the model...")

        if not self.is_configured:
            # --- MOCK RESPONSE ---
            return self._get_mock_response(recent_events)

        # --- REAL API CALL ---
        try:
            # response = self.model.generate_content(prompt)
            # response_text = response.text
            # Remove potential markdown formatting
            # if response_text.startswith("```json"):
            #     response_text = response_text.strip("```json\n").strip("```")
            # prediction = json.loads(response_text)
            # logging.info(f"Received AI prediction: {prediction}")
            # return prediction
            pass # Placeholder for real implementation
        except Exception as e:
            logging.error(f"Failed to get reasoning from Gemini API: {e}")
            return None

        return self._get_mock_response(recent_events) # Fallback for now

    def _get_mock_response(self, recent_events: list[dict]) -> dict:
        """Generates a plausible mock response based on input events."""
        logging.info("Generating mock AI response.")

        # Simple logic for mock response
        score = 0
        for event in recent_events:
            if event.get('impact') == 'high':
                if event.get('sentiment') == 'positive' or event.get('event') == 'exchange_outflow':
                    score += 2
                elif event.get('sentiment') == 'negative' or event.get('event') == 'exchange_inflow':
                    score -= 2
            elif event.get('impact') == 'medium':
                 if event.get('sentiment') == 'positive' or event.get('event') == 'exchange_outflow':
                    score += 1
                 elif event.get('sentiment') == 'negative' or event.get('event') == 'exchange_inflow':
                    score -= 1

        if score > 2:
            prediction = "bullish"
            confidence = 0.85
            comment = "Strong positive signals from whale movements and news sentiment."
        elif score < -2:
            prediction = "bearish"
            confidence = 0.80
            comment = "Negative sentiment combined with whale inflows suggest downward pressure."
        else:
            prediction = "neutral"
            confidence = 0.60
            comment = "Mixed signals provide no clear short-term direction."

        return {
            "prediction": prediction,
            "confidence": confidence,
            "comment": comment
        }

def format_ai_response(prediction_data: dict) -> dict:
    """Formats the AI's prediction into the standard message protocol."""
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "type": "ai_reason",
        "source": "Gemini",
        "sentiment": prediction_data.get("prediction", "neutral"), # Map prediction to sentiment
        "impact": "high" if prediction_data.get("confidence", 0) > 0.75 else "medium",
        "details": {
            "prediction": prediction_data.get("prediction"),
            "confidence": prediction_data.get("confidence"),
            "comment": prediction_data.get("comment"),
        },
        "confidence": prediction_data.get("confidence", 0.5)
    }