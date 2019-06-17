import os
import re

import contractions
from nltk import pos_tag
from string import digits
from nltk.tokenize import word_tokenize
from nltk.stem  import WordNetLemmatizer

from archtype_user_identification.twitter_preprocess import get_tweet_by_handle, stopwords

os.environ["TF_CPP_MIN_LOG_LEVEL"]="3"

lemmatizer = WordNetLemmatizer()
stop_word = list(set(stopwords.words('english')))
stop_word = list(filter(lambda x : x!=str('not'),stop_word))

def noun_phrase(token):
  '''To extract important grammatical token from text'''

  key = pos_tag(token)
  data=[]
  for tag in key:
    if tag[1] == 'NN':
      data.append(tag[0])
  
  if len(data) == 0:
    return token
  
  return list(data)


def text_processing(text):
    
    #removing everything except letter and space
    temp = re.sub(r"[^A-Za-z ]+",r"",text)
    #lower case
    temp = temp.lower()
    #remove unnecessary spaces
    temp = " ".join(temp.split())
    #word tokenize
    temp = word_tokenize(temp)
    # remove stop words
    temp = [ item for item in temp if item not in stop_word]
    #lemmatize
    temp = [lemmatizer.lemmatize(item) for item in temp]
    
    return temp


def find_token(text):
    '''
    This function convert text, i.e string, into token
    after doing all required pre-processing

    argument: text -> input string to find token
    returns the token

    input: text of type string
    output: strings in list
    
    '''
    preprocess_text = text_processing(text)
    noun_phrase_token = noun_phrase(preprocess_text)
    
    return noun_phrase_token

