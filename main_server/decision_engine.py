import json
import logging
from business_rules.engine import run_all
from .utils.database import Database, Event
from .alert_manager import AlertManager
from datetime import datetime
import ast

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Analyzes events using a rule engine and triggers alerts.
    """
    def __init__(self, config: dict, db: Database, alert_manager: AlertManager):
        self.config = config
        self.db = db
        self.alert_manager = alert_manager
        self.rules = self._load_rules()
        self.last_alert_times = {} # Throttle alerts per rule

    def _load_rules(self):
        """Loads rules from the specified JSON file."""
        try:
            with open(self.config['ALERT_RULES_FILE'], 'r') as f:
                logger.info("Successfully loaded alert rules.")
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load or parse rules file: {e}")
            return []

    async def process_new_event(self, new_event: dict):
        """
        The main entry point for processing a newly received event.
        It re-evaluates the market state against all rules.
        """
        logger.info(f"Processing new event: Type='{new_event.get('type')}', Source='{new_event.get('source')}'")

        # 1. Get all recent events from the DB to build a full context
        recent_events = self.db.get_recent_events(self.config.get("EVENT_EXPIRATION_SECONDS", 3600))

        # 2. Define the facts/variables for the rules engine based on context
        rule_facts = self._define_rule_facts(recent_events)

        # 3. Define the action to be taken if a rule passes
        def trigger_alert(rule_name, level, message):
            # Throttle alerts to avoid spam (e.g., one alert per rule per 5 minutes)
            now = datetime.utcnow()
            last_alert_time = self.last_alert_times.get(rule_name)
            if last_alert_time and (now - last_alert_time).total_seconds() < 300:
                logger.info(f"Throttling alert for rule '{rule_name}'.")
                return

            # Format the message with dynamic fact values
            formatted_message = message.format(**rule_facts)
            self.alert_manager.send_alert(formatted_message, level)
            self.last_alert_times[rule_name] = now

        actions = [{
            'name': 'trigger_alert',
            'params': [{'fieldType': 'string', 'name': 'rule_name'},
                       {'fieldType': 'string', 'name': 'level'},
                       {'fieldType': 'string', 'name': 'message'}]
        }]

        # 4. Run the rules engine
        run_all(rule_set=self.rules,
                defined_variables=RuleVariables(rule_facts),
                defined_actions=RuleActions(trigger_alert),
                stop_on_first_trigger=False)

    def _define_rule_facts(self, events: list[Event]) -> dict:
        """Aggregates recent events to create facts for the rules engine."""
        facts = {
            "whale_inflow_btc": 0,
            "whale_outflow_btc": 0,
            "recent_sentiment_score": 0.0,
            "ai_prediction_confidence": 0.0,
            "ai_prediction_trend": "neutral",
            "ai_prediction_comment": "",
            "market_volatility_pct": 0.0,
        }

        sentiment_scores = []

        for event in events:
            details = ast.literal_eval(event.details) if isinstance(event.details, str) else event.details

            if event.event_type == 'whale':
                if details.get('event') == 'exchange_inflow':
                    facts['whale_inflow_btc'] += details.get('amount_btc', 0)
                elif details.get('event') == 'exchange_outflow':
                    facts['whale_outflow_btc'] += details.get('amount_btc', 0)

            elif event.event_type in ['news', 'social']:
                polarity = 0
                if event.sentiment == 'positive' or event.sentiment == 'bullish':
                    polarity = event.confidence
                elif event.sentiment == 'negative' or event.sentiment == 'bearish':
                    polarity = -event.confidence
                sentiment_scores.append(polarity)

            elif event.event_type == 'ai_reason':
                if event.confidence > facts['ai_prediction_confidence']: # Take the most confident prediction
                    facts['ai_prediction_confidence'] = event.confidence
                    facts['ai_prediction_trend'] = details.get('prediction')
                    facts['ai_prediction_comment'] = details.get('comment')

            elif event.event_type == 'market' and details.get('event') == 'volatility_spike':
                vol_pct = details.get('price_change_percent', 0) * 100
                if vol_pct > facts['market_volatility_pct']:
                    facts['market_volatility_pct'] = vol_pct

        if sentiment_scores:
            facts['recent_sentiment_score'] = sum(sentiment_scores) / len(sentiment_scores)

        # Add formatted versions for alert messages
        facts['whale_inflow_btc_formatted'] = f"{facts['whale_inflow_btc']:,}"
        facts['whale_outflow_btc_formatted'] = f"{facts['whale_outflow_btc']:,}"
        facts['recent_sentiment_score_formatted'] = f"{facts['recent_sentiment_score']:.2f}"
        facts['ai_prediction_confidence_formatted'] = f"{facts['ai_prediction_confidence']:.0%}"
        facts['market_volatility_pct_formatted'] = f"{facts['market_volatility_pct']:.2f}%"

        logger.info(f"Defined rule facts: {facts}")
        return facts

# Helper classes for the business-rules library
class RuleVariables:
    def __init__(self, facts):
        self.facts = facts
    def __getattr__(self, name):
        return self.facts.get(name)

class RuleActions:
    def __init__(self, trigger_alert_func):
        self.trigger_alert = trigger_alert_func