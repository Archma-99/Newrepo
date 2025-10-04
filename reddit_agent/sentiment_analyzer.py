import logging
from textblob import TextBlob
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_reddit_sentiment(posts: list[dict]) -> dict | None:
    """
    Analyzes the overall sentiment from a list of Reddit posts.

    Args:
        posts (list[dict]): A list of posts from the scraper.

    Returns:
        dict | None: An aggregated sentiment report or None if no posts are provided.
    """
    if not posts:
        return None

    total_polarity = 0
    total_mentions = 0
    positive_posts = 0
    negative_posts = 0
    neutral_posts = 0

    for post in posts:
        # Simple check for Bitcoin mentions
        if "bitcoin" in post['title'].lower() or "btc" in post['title'].lower():
            total_mentions += 1

        # Analyze sentiment of the title
        analysis = TextBlob(post['title'])
        total_polarity += analysis.sentiment.polarity

        if analysis.sentiment.polarity > 0.1:
            positive_posts += 1
        elif analysis.sentiment.polarity < -0.1:
            negative_posts += 1
        else:
            neutral_posts += 1

    avg_polarity = total_polarity / len(posts) if posts else 0

    # Determine overall sentiment and impact
    if avg_polarity > 0.15:
        sentiment = "bullish"
        impact = "medium" if total_mentions > 5 else "low"
    elif avg_polarity < -0.15:
        sentiment = "bearish"
        impact = "medium" if total_mentions > 5 else "low"
    else:
        sentiment = "neutral"
        impact = "low"

    # Increase impact if there's a strong consensus
    if (positive_posts > len(posts) * 0.7) or (negative_posts > len(posts) * 0.7):
        impact = "high"

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "type": "social",
        "source": "reddit",
        "sentiment": sentiment,
        "impact": impact,
        "details": {
            "total_posts_analyzed": len(posts),
            "btc_mentions": total_mentions,
            "avg_polarity": round(avg_polarity, 3),
            "positive_posts": positive_posts,
            "negative_posts": negative_posts,
        },
        "confidence": round(abs(avg_polarity), 2)
    }

    logging.info(f"Reddit sentiment analysis complete: {sentiment} (Polarity: {avg_polarity:.2f})")
    return report