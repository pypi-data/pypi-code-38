import re
import argparse

import nltk
import numpy as np
from pprint import pprint
from nltk.corpus import stopwords



nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('brown')


stopword_tw = ['get', 'got', 'hey', 'hmm', 'hoo', 'let', 'ooo', 'par',
    'yer', 'didn', 'one', 'com', 'new', 'like', 'great',
    'make', 'top', 'awesome', 'best', 'good', 'wow', 'yes',
    'say', 'yay', 'would', 'thanks', 'thank', 'use',
    'should', 'could','best','really','see','want','nice',
    'while','know', 'trump', 'nyfw', 'iphone', 'hurricane',
    'rt', 'per', 'espn', 'soundcloud', 'ten', 'count', 
    'advance', 'newsletter','thedish', 'nycwff', 'thefword',
    'irma', 'fave', 'beer', 'stefan', 'aiga',
    'aigatogether', 'aigadesignconf', 'aigadg', 'aigagala',
    'ddc', 'tbt', 'whitneybiennial', 'calder', 'wknd',
    'pipilottirist', 'live', 'watch', 'check', 'video',
    'clip', 'today', 'tonight', 'week', 'year', 'month',
    'time', 'last', 'night', 'morning', 'yesterday',
    'tomorrow', 'day', 'first', 'love', 'nyc', 'city',
    'york', 'new', 'happy', 'need', 'look', 'back', 'right',
    'win', 'chance', 'enter', 'ever','pst','wha','yep', 'via',
    'app', 'twitter', 'streaming', 'stream', 'ask', 'amp',
    'beautiful', 'best', 'amazing', 'good', 'perfect', 'cute',
    'simple', 'love']

stop_list = set(stopwords.words('english') + stopword_tw)


def twitter_preprocess(messages):
    '''
        function pre-process all the tweets like removing emoticons, '@' symbols etc

        input: twitter post
        output: pre-processed twitter post
    '''
    new_tweet = []
    emoji_pattern = re.compile("["
                            u"\U0001F600-\U0001F64F"  # emoticons
                            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                            u"\U0001F680-\U0001F6FF"  # transport & map symbols
                            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            u"\U00002702-\U000027B0"
                            u"\U000024C2-\U0001F251"
                            "]+", flags=re.UNICODE)
    
    for tweet in messages:
        tweet = re.sub(r"^https://t.co/[A-Za-z0-9]*\s"," ",tweet)
        tweet = re.sub(r"\s+https://t.co/[a-zA-Z0-9]*\s", " ", tweet)
        tweet = re.sub(r"\s+https://t.co/[a-zA-Z0-9]*$", " ", tweet)# to substitute url's with a whitespace at the beginning, in between and at the end of a sentence
        
        tweet = re.sub("\.\.+"," ",tweet)    # to substitute more than one '.' between words with a space
        tweet = re.sub("-$","",tweet)        # to remove '-' at the end of a sentence
        tweet = re.sub(r"^ +","",tweet)      # to remove one or more whitespace at the beginning of a sentence
        tweet = re.sub(r"  +"," ",tweet)     # to substitute one or more whitespace with a single space
        tweet = emoji_pattern.sub(r'', tweet)
        tweet = re.sub(r"(?:#|\@|https?\:\/\/|www\.)\S+","",tweet)
        
        new_tweet.append(tweet)
    
    return new_tweet


def get_tweet(screen_name, count=200, include_rts=False):
    '''
    Function returns the latest maximum 200 post in twitter without retweet
    '''  
    try:
        pprint('getting tweet from {}'.format(screen_name))

        stuff = api.user_timeline(screen_name = screen_name, count=count, include_rts=include_rts)
        total_tweet = []

        for tweet in stuff:
            total_tweet.append(tweet.text)

        return ''.join(twitter_preprocess(total_tweet))
    
    except:
        return np.nan

def get_tweet_by_handle(handle_name):
    '''
    This function return the pre-processed twitter post.

    arguments:
    ---------
    handle_name: twitter handle of a user

    input: twitter_handle
    output: pre-processed tweets
    '''
    
    return get_tweet(screen_name=handle_name)