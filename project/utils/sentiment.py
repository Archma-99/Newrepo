from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def get_sentiment_score(text):
    """
    Analyzes the sentiment of a given text and returns the compound score.
    The compound score is a metric that calculates the sum of all the lexicon ratings,
    which have been normalized between -1 (most extreme negative) and +1 (most extreme positive).
    """
    if not text:
        return 0.0

    analyzer = SentimentIntensityAnalyzer()
    sentiment_dict = analyzer.polarity_scores(text)
    return sentiment_dict['compound']

if __name__ == '__main__':
    # Example usage
    text1 = "Bitcoin hits new all-time high, market is euphoric!"
    text2 = "Regulatory crackdown causes widespread panic and sell-offs."

    print(f"Sentiment for '{text1}': {get_sentiment_score(text1)}")
    print(f"Sentiment for '{text2}': {get_sentiment_score(text2)}")