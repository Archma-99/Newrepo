from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def get_sentiment_score(text):
    """
    Analyzes the sentiment of a given text and returns the compound score.
    The compound score is a metric that calculates the sum of all the lexicon ratings,
    which have been normalized between -1 (most extreme negative) and +1 (most extreme positive).
    """
    analyzer = SentimentIntensityAnalyzer()
    sentiment_dict = analyzer.polarity_scores(text)
    return sentiment_dict['compound']

if __name__ == '__main__':
    # Example usage
    text1 = "Crypto market is booming and showing incredible growth!"
    text2 = "There is a lot of fear and uncertainty in the market right now."

    print(f"Sentiment for '{text1}': {get_sentiment_score(text1)}")
    print(f"Sentiment for '{text2}': {get_sentiment_score(text2)}")