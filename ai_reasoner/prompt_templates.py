def get_reasoning_prompt(recent_events: list[dict]) -> str:
    """
    Generates a structured prompt for the AI based on recent market events.

    Args:
        recent_events (list[dict]): A list of recent event reports from the main server.

    Returns:
        str: A formatted prompt string for the Gemini AI.
    """

    prompt_header = """
You are an expert crypto market analyst AI. Your task is to analyze a collection of recent market signals and provide a concise, actionable prediction for the short-term trend of Bitcoin (BTC).

Based on the following data points, please generate a JSON object that summarizes your findings.
The JSON object must have the following structure:
{
  "prediction": "bullish|bearish|neutral",
  "confidence": <a float between 0.0 and 1.0>,
  "comment": "<A brief, one-sentence explanation for your prediction. Mention the key drivers.>"
}

Here is the data:
"""

    event_summaries = []
    if not recent_events:
        event_summaries.append("- No significant events detected recently.")
    else:
        for event in recent_events:
            summary = f"- Type: {event.get('type')}, Source: {event.get('source')}, Impact: {event.get('impact')}"
            if event.get('type') == 'news':
                summary += f", Sentiment: {event.get('sentiment')}, Title: {event.get('details', {}).get('title')}"
            elif event.get('type') == 'social':
                summary += f", Sentiment: {event.get('sentiment')}, Details: {event.get('details')}"
            elif event.get('type') == 'whale':
                 summary += f", Event: {event.get('event')}, Amount: {event.get('details', {}).get('amount_btc')} BTC"
            elif event.get('type') == 'market':
                summary += f", Event: {event.get('event')}, Details: {event.get('details', {}).get('comment')}"
            event_summaries.append(summary)

    prompt_body = "\n".join(event_summaries)

    prompt_footer = """
Please provide only the JSON object in your response, with no other text before or after it.
The "comment" should be concise and directly reference the data provided (e.g., "Strong whale outflows and positive news suggest upward momentum.").
"""

    return prompt_header + prompt_body + prompt_footer