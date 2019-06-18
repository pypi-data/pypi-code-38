import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

def get_sentiment_from_text(text):
    return sia.polarity_scores(text)['compound']
