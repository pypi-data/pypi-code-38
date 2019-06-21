#!/usr/bin/env python
# coding: utf-8

# In[2]:


import re
import nltk
from nltk.stem import WordNetLemmatizer
import pandas as pd
import numpy as np
import ast
import numpy as np


# In[3]:


#Here are a list of words that, when preceding, require us to inverse our score. 
#"I like Apple" has a score of 1.5, but "I don't like Apple" would have a score of -1.5 because of the negation
negate =     ["aint", "arent", "cannot", "cant", "couldnt", "darent", "didnt", "doesnt",
     "ain't", "aren't", "can't", "couldn't", "daren't", "didn't", "doesn't",
     "dont", "hadnt", "hasnt", "havent", "isnt", "mightnt", "mustnt", "neither",
     "don't", "hadn't", "hasn't", "haven't", "isn't", "mightn't", "mustn't",
     "neednt", "needn't", "never", "none", "nope", "nor", "not", "nothing", "nowhere",
     "oughtnt", "shant", "shouldnt", "uhuh", "wasnt", "werent",
     "oughtn't", "shan't", "shouldn't", "uh-uh", "wasn't", "weren't",
     "without", "wont", "wouldnt", "won't", "wouldn't", "rarely", "seldom", "despite"]

boosters =     ['absolutely', 'astonishingly', 'amazingly', 'greatly', 'completely', 'considerably', 'decidedly', 'deeply', 'effing',
     'enormously', 'exceedingly', 'supremely', 'strikingly', 'vastly', 'notably', 'surpassingly', 'terrifically',
     'immensely', 
     'entirely', 'especially', 'exceptionally', 'extremely', 'fabulously', 'flipping', 'flippin', 'fricking', 'frickin',
     'frigging', 'friggin', 'fully', 'fucking', 'greatly', 'hella', 'highly', 'hugely', 'incredibly', 'intensely', 'majorly',
     'more', 'most', 'particularly', 'purely', 'quite', 'really', 'remarkably', 'so', 'surprisingly', 'substantially',
     'thoroughly', 'totally', 'tremendously', 'uber', 'unbelievably', 'unusually', 'utterly', 'very']

decreasers = ['almost', 'barely', 'scarcily', 'lacking', 'hardly', 'kind of', 'kinda', 'less', 'little', 'marginally', 'occasionally', 'partly', 'sort of',
'sorta', 'hardly', 'slightly', 'carelessly', 'somewhat', 'in part', 'relatively', 'not entirely', 'not fully',]


# In[4]:


def create_ci_lexicon(lexicon_file):
    
    """
    Takes in an inital lexicon with information on how the final values was derived.
    Outputs confidence score for each individual word.
    """
    
    df = pd.read_csv(lexicon_file, encoding='cp437', header=None)
    
    def descriptive(x):
        return np.std(ast.literal_eval(x))
    
    df['std_dev'] = df[3].str.strip("'").apply(descriptive)
    
    basis = df.std_dev.mean() + 1.5 * df.std_dev.std()
    
    def normalize_conf(x):
        return (x - basis) / basis
    
    df['norm_conf'] = df.std_dev.apply(normalize_conf)
    
    return dict(zip(df[[0, 'norm_conf']][0].values, (1 - (df.norm_conf.rank() / df.norm_conf.rank().max()))))


# In[5]:


ci_lexicon = create_ci_lexicon('vader_lexicon.csv')
lexicon = dict(zip(pd.read_csv('vader_lexicon.csv', 
                               encoding='cp437', 
                               header=None)[[0, 1]].values.T[0], 
                   pd.read_csv('vader_lexicon.csv', 
                               encoding='cp437', 
                               header=None)[[0, 1]].values.T[1]))


# In[6]:


class PreprocessText(object):
    """
    Sentiment relevant text properties. 
    """

    def __init__(self, text):

        self.text = text
        self.clean_text = self._clean_text()

    def _clean_text(self):

        wordz = self.text.split()

        lemmatizer = WordNetLemmatizer()
        words = []
        for word in wordz:
            words.append(lemmatizer.lemmatize(word))

        return words


# In[7]:


class Sentiment(object):
    """
    Sentiment Analyzer
    """


    def __init__(self):

        self.lexicon = lexicon
        self.negate = negate
        self.ci_lexicon = ci_lexicon
        self.boosters = boosters
        self.decreasers = decreasers
            
    def score(self, text):
        """Calculate sentiment score for text"""
        words = PreprocessText(text).clean_text
        sentiments = []
        confidences = []
        for item in words:
            sentiments, confidences = self.sentiment_polarity(item, sentiments, confidences, words)
        score_interval = self.final_calculation(sentiments, confidences)
        
        return {'score': score_interval[0], 'confidence_interval': score_interval[1]}
        
    def sentiment_polarity(self, item, sentiments, confidences, words):
        """Checks the average sentiment score by querying our lexicon"""
        item_lowercase = item.lower()
        if item_lowercase in self.lexicon:
            weight = self.lexicon[item_lowercase] / 5 
            final_weight = self.modifiers(words, item, weight)
            confidence_score = self.ci_lexicon[item_lowercase]
            confidence_calc = self.confidence_calc(final_weight, confidence_score)
            sentiments.append(final_weight)
            confidences.append(confidence_calc)
        return sentiments, confidences
    
    
    def final_calculation(self, sentiments, confidences):
        """Applies all final calculations to get the final sentiment score"""
        
        if len(sentiments) == 0:
            final_calc = 0
            return final_calc, (0, 0)
        else:
            final_calc = sum(sentiments) / len(sentiments)
        
        count = 0
        upper = 0
        lower = 0
        for interv in confidences:
            upper += interv[1]
            lower += interv[0]
            count += 1
        
        return final_calc, (lower/count, upper/count)
    
    def modifiers(self, words, item, weight):
        """Checks to see if there is a negation word in the words
        I love apples = .72
        I don't love apples = -.72"""
        neg_coef = 1
        boost_coef = 1
        dec_coef = 1
        lexicon_index = words.index(item)
        preceding_word = words[lexicon_index - 1]
        if preceding_word in self.negate:
            neg_coef = -1
        if preceding_word in self.boosters:
            boost_coef = 1.25
        if preceding_word in self.decreasers:
            dec_coef = .8
        final_weight = weight * neg_coef * boost_coef * dec_coef
        return final_weight
    
    
    def confidence_calc(self, final_weight, confidence_score): 
        
        if final_weight >= 0:
            upper = final_weight + (1 - confidence_score) * final_weight
            lower = final_weight - (1 - confidence_score) * final_weight
        else: 
            lower = final_weight + (1 - confidence_score) * final_weight
            upper = final_weight - (1 - confidence_score) * final_weight
        return (lower, upper)
        
    


# In[ ]:




