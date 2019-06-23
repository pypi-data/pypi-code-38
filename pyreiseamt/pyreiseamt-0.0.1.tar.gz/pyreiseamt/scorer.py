#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Load Modules
import pickle
import os
import re
import string

# Load Sentiment Dictionary and Stopwords
script_path = os.path.abspath(__file__)
script_folder = os.path.split(script_path)[0]

with open(os.path.join(script_folder, "sentiment_dict.obj"), "rb") as f:
    sentiment_dict = pickle.load(f)

with open(os.path.join(script_folder, "stopwords.obj"), "rb") as f:
    stopwords = pickle.load(f)
    

# Prepare Text
def _prepare_text(text):
    text = text.lower()
    text = re.sub("[" + string.punctuation + "]", " ", text)
    text = re.sub("\s+", " ", text)
    text = text.strip()
    return(text)
    
# Sentiment Score a Text
def score_text(text):
    text = _prepare_text(text)
    tokens = re.split("\s+", text)
    sentiment_scores = list()
    for token in tokens:
        try:
            score = sentiment_dict[token]
        except Exception:
            score = None
        sentiment_scores.append(score)
    sentiment_scores = [x for x in sentiment_scores if x is not None]
    if len(sentiment_scores) > 0:
        sentiment_sum = sum(sentiment_scores)
        sentiment_len = len(sentiment_scores)
        sentiment_mean = sentiment_sum / sentiment_len
    else:
        sentiment_mean = None
    return(sentiment_mean)