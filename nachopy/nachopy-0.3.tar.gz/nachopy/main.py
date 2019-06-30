import random
from nachopy.Script import *
from nltk import sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string
import copy
from nachopy.words_of_wisdom import *
from nltk.corpus import stopwords

# from words_of_wisdom import *

lemmer = WordNetLemmatizer()
def LemNormalize(line):
    text = line.translate(str.maketrans(dict.fromkeys(string.punctuation)))
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [w for w in tokens if not w in set(stopwords.words('english'))]
    tokens = [lemmer.lemmatize(token) for token in tokens]
    return tokens
def respond(user_response,lines):
    lines_c = copy.copy(lines)
    lines_c.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize)
    tfidf = TfidfVec.fit_transform(lines_c)

    vals = cosine_similarity(tfidf[-1],tfidf)
    idx = vals.argsort()[0][-2]

    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]

    if req_tfidf == 0:
        return 'What do you mean?'
    else:
        return lines[idx]
class nacho():


    def __init__(self):
        self.sentences = sent_tokenize(script())
    def nacho_chat(self):
        say = ''
        print('Nacho: I am Nacho, the luchador.')
        while say != 'quit':
            say = input('You: ')
            if say == 'quit':
                print('Nacho: Go, Go away!')
            else:
                print('Nacho: ',respond(say.lower(),self.sentences))
