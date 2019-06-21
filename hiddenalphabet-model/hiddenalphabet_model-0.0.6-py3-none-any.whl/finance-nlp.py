#!/usr/bin/env python
# coding: utf-8

# In[5]:


import re
import nltk
from nltk.stem import WordNetLemmatizer
import pandas as pd
import numpy as np
import ast
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
lemmatizer = WordNetLemmatizer()


# In[71]:


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


# In[72]:



# this whole cell will be automated when pip installed using os library. will modify when deploying to Pypi


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


# In[73]:


ci_lexicon = create_ci_lexicon('vader_lexicon.csv')
lexicon = dict(zip(pd.read_csv('vader_lexicon.csv', 
                               encoding='cp437', 
                               header=None)[[0, 1]].values.T[0], 
                   pd.read_csv('vader_lexicon.csv', 
                               encoding='cp437', 
                               header=None)[[0, 1]].values.T[1]))


# In[74]:


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


# In[126]:


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
        
    


# In[127]:


t = """Turning to the wholesale channel, revenue was down 4% related to the shift in timing of shipments
as we said last quarter. As stated earlier, our brand is performing well at both Neiman Marcus and Nordstrom
as well as across our specialty retail and third-party e-commerce partners globally"""


# In[128]:


get_ipython().run_cell_magic('time', '', 'analyzer = Sentiment()\nprint(analyzer.score(t))')


# In[96]:


import pandas as pd
df = pd.read_csv('trading-tweets.csv')


# In[97]:


df.shape


# In[98]:


model = Sentiment()


# In[99]:


#Function for applying our sentiment analyis to every row in a dataframe
def vectorized_sentiment(text):
    try:
        return model.score(text)
    except:
        return 0

df['scores'] = df.text.apply(vectorized_sentiment)


# In[100]:


bitcoin = df[(df.text.str.lower().str.contains('btc') | df.text.str.lower().str.contains('bitcoin'))]


# In[101]:


bitcoin = bitcoin[bitcoin.scores.apply(lambda x: x['score']) != 0]


# In[102]:


bitcoin.shape


# In[103]:


bitcoin.time = pd.to_datetime(bitcoin.time)


# In[104]:


df = bitcoin.copy()


# In[105]:


import seaborn as sns
import matplotlib.pyplot as plt


# In[106]:


df['sentiment_score'] = df.scores.apply(lambda x: x['score'])
df['lower_bound'] = df.scores.apply(lambda x: x['confidence_interval'][0])
df['upper_bound'] = df.scores.apply(lambda x: x['confidence_interval'][1])


# In[107]:


grouped = df.groupby(df.time.dt.date).mean()


# In[108]:


real_time_correlation = btc


# In[109]:


grouped.head()

z = pd.Series((pd.read_csv('BTC-USD.csv').Close.values - pd.read_csv('BTC-USD.csv').Close.values.mean()) / pd.read_csv('BTC-USD.csv').Close.values.mean()).values

#sns.lineplot(x=grouped.index, y=grouped.lower_bound, color='red')
#sns.lineplot(x=grouped.index, y=grouped.upper_bound, color='green')
#sns.lineplot(x=grouped.index, y=z)
plt.ylim(-.1, .5)
plt.fill_between(grouped.index, y1=grouped.lower_bound, y2=grouped.upper_bound, color='gray', alpha=.25)
sns.lineplot(x=grouped.index, y=grouped.sentiment_score, color='blue')
sns.lineplot(x=grouped.index, y=btc, color='yellow')
plt.title('Bitcoin sentiment from June 3rd - June 13th', fontsize=15);


# In[110]:


real_time_correlation = np.corrcoef(grouped.sentiment_score, btc)[1][0]
print('Real Time Correlation: ', real_time_correlation)


# In[111]:


#sns.lineplot(x=grouped.index, y=grouped.lower_bound, color='red')
#sns.lineplot(x=grouped.index, y=grouped.upper_bound, color='green')
#sns.lineplot(x=grouped.index, y=z)
plt.ylim(-.1, .5)
plt.fill_between(grouped.index, y1=grouped.lower_bound, y2=grouped.upper_bound, color='gray', alpha=.25)
sns.lineplot(x=grouped.index, y=grouped.sentiment_score, color='blue')
sns.lineplot(x=grouped.index, y=n, color='yellow')
plt.title('Bitcoin sentiment from June 3rd - June 13th', fontsize=15);


# In[112]:


one_day_delay_correlation = np.corrcoef(grouped.sentiment_score, one_day_delay)[1][0]
print('Sentiment correlation with prices from a day before: ', one_day_delay_correlation)


# In[125]:


vader_correlation_with_delay = np.corrcoef(grouped.scores_vader, one_day_delay)[1][0]
print("Vader's Score: ", vader_correlation_with_delay, "\nOur Score: ", one_day_delay_correlation)


# In[45]:


n = btc


# In[46]:


n = np.delete(n, 0)


# In[47]:


n = np.append(n, 0.03551014)


# In[51]:


one_day_delay = n


# In[48]:


n


# In[69]:


grouped


# In[117]:


df.sentiment_score.describe()


# In[36]:


btc = pd.Series((pd.read_csv('BTC-USD.csv').Close.values - pd.read_csv('BTC-USD.csv').Close.values.mean()) / pd.read_csv('BTC-USD.csv').Close.values.mean()).values


# In[37]:


btc2 = btc*3


# In[68]:


Sentiment().score('i really love cats')


# In[120]:


sid = SentimentIntensityAnalyzer()


# In[121]:


model = Sentiment()
def vectorized_sentiment(text):
    try:
        return sid.polarity_scores(text)['compound']
    except:
        return 0

df['scores_vader'] = df.text.apply(vectorized_sentiment)


# In[122]:


df


# In[123]:


grouped = df.groupby(df.time.dt.date).mean()


# In[124]:


grouped['combined'] = (grouped.scores_vader + grouped.sentiment_score) / 2


# In[118]:


grouped


# In[58]:


np.corrcoef(grouped.combined, z)


# In[60]:


vocab = {}

def loop_words(lst_of_words):
    
    for word in lst_of_words:
        try:
            vocab[word] += 1
            
        except:
            vocab[word] = 1
    
df.text.str.lower().str.split().apply(loop_words)


# In[61]:


word_counts = pd.DataFrame({'words':list(vocab.keys()), 'counts': list(vocab.values())}).sort_values('counts', ascending=False)


# In[ ]:




