"""
This is SeqWORDS algorithm.
SeqWORDS is an unsupervised Chinese words segmentation method.
"""

import decimal
import re
from collections import Counter
from decimal import *
import math
import numpy as np


def preprocessing(corpus):
    reChinese = re.compile('[\u4e00-\u9fa5]+') 
    return reChinese.findall(corpus)

def cut_word(texts, tauL, tauF1, useProbThld1):
    word_ls = []
    for sentence in texts:
        for m in list(range(len(sentence))):
            if m + tauL > len(sentence):
                tLimit = len(sentence)-m
            else:
                tLimit = tauL
            for t in list(range(tLimit)):
                word = sentence[m:m+t+1]
                word_ls.append(word)
    # Counting words appearance frequence.
    word_ls = {k: v for k, v in dict(Counter(word_ls)).items() if len(k)==1 or v >= tauF1}
    # Counting words relative appearance frequence.
    sumfreq = sum(word_ls[x] for x in word_ls)
    for key in word_ls.keys():
        word_ls[key]=word_ls[key]/sumfreq
    # Filter those appearance frequence lower than useProbThld1.
    word_ls = {k: v for k, v in dict(Counter(word_ls)).items() if len(k)==1 or v >= useProbThld1}
    # Normalize appearance frequence again, because of lost some words at latest step.
    sumfreq = sum(word_ls[x] for x in word_ls)
    for key in word_ls.keys():
        word_ls[key]=word_ls[key]/sumfreq
        word_ls[key]=decimal.Decimal(word_ls[key])
    return word_ls


def cut_ftword(texts, tauL, tauF1, useProbThld1):
    ftword_ls = []
    for sentence in texts:
        if 0 + tauL > len(sentence):
            tLimit = len(sentence)-0
        else:
            tLimit = tauL
        for t in list(range(tLimit)):
            ftword = sentence[0:0+t+1]
            ftword_ls.append(ftword)
    
    # Counting ftword appearance frequence and filtering those higher than tauF1.
    ftword_ls = {k: v for k, v in dict(Counter(ftword_ls)).items() if len(k)==1 or v >= tauF1 }
    
    # Counting ftword relative appearance frequence.
    sumfreq = sum(ftword_ls[x] for x in ftword_ls)
    for key in ftword_ls.keys():
        ftword_ls[key]=ftword_ls[key]/sumfreq
    
    # Filter ftword for relative appearance freaquence higher than useProbThld1.
    ftword_ls = {k: v for k, v in dict(Counter(ftword_ls)).items() if len(k)==1 or v >= useProbThld1}
    
    # Doing normalize again.
    sumfreq = sum(ftword_ls[x] for x in ftword_ls)
    for key in ftword_ls.keys():
        ftword_ls[key]=ftword_ls[key]/sumfreq
        ftword_ls[key]=decimal.Decimal(ftword_ls[key])
    return ftword_ls



def cut_wordseq(texts, tauL, tauF2, useProbThld2):
    wordseq_ls = []
    for sentence in texts:
        for m in list(range(len(sentence))):
            if m + tauL > len(sentence):
                t1Limit = len(sentence)-m
            else:
                t1Limit = tauL
            for t1 in list(range(t1Limit)):
                First_word = sentence[m:m+t1+1]
                if m + t1 + 1 + tauL > len(sentence):
                    t2Limit = len(sentence)-(m+t1+1)
                else:
                    t2Limit = tauL
                for t2 in list(range(t2Limit)):
                    Second_word = sentence[m+t1+1 : m+t1+1+t2+1]
                    wordseq_ls.append((First_word,Second_word))
    # Counting wordseq appearance frequence and filtering those higher than tauF2.
    wordseq_ls = {k: v for k, v in dict(Counter(wordseq_ls)).items() if len(k[0])==1 or len(k[1])==1 or v >= tauF2}
    # Counting wordseq condictional probability.
    sum_wordseqfreq = {k[0]:0 for k in wordseq_ls.keys()}
    for wordseq in wordseq_ls.keys():
        sum_wordseqfreq[wordseq[0]] += wordseq_ls[wordseq]
    for key in wordseq_ls.keys():
        wordseq_ls[key] = wordseq_ls[key]/sum_wordseqfreq[key[0]]
    # Filter wordseq has condictional probability higher than useProbThld2.
    wordseq_ls = {k: v for k, v in dict(Counter(wordseq_ls)).items() if len(k[0])==1 or len(k[1])==1 or v >= useProbThld2} 
    # Doing normalize again.
    sum_wordseqfreq = {k[0]:0 for k in wordseq_ls.keys()}
    for wordseq in wordseq_ls.keys():
        sum_wordseqfreq[wordseq[0]] += wordseq_ls[wordseq]
    for key in wordseq_ls.keys():
        wordseq_ls[key] = wordseq_ls[key]/sum_wordseqfreq[key[0]]
        wordseq_ls[key] = decimal.Decimal(wordseq_ls[key])
    return wordseq_ls




def DPLikelihoodsBackward(tauL, sentence, ftword_list, word_list, wordseq_list):
    Likelihoods = [decimal.Decimal(0)] * (len(sentence)+1)
    Likelihoods[len(sentence)] = decimal.Decimal(1)
    for m in list(reversed(range(len(sentence)))):
        if m != 0:
            if m + tauL > len(sentence):
                t1Limit = len(sentence)-m
            else:
                t1Limit = tauL
            for t1 in list(range(t1Limit+1))[1:]:
                First_word = sentence[m:m+t1]         
                if m + t1 + tauL > len(sentence):
                    t2Limit = len(sentence)-(m+t1)
                else:
                    t2Limit = tauL

                if t2Limit != 0:
                    for t2 in list(range(t2Limit+1))[1:]:
                        Second_word = sentence[m+t1 : m+t1+t2]
                        if bool(wordseq_list.get((First_word, Second_word))) & bool(word_list.get(First_word)) \
                            & bool(word_list.get(Second_word)):
                            Likelihoods[m] += word_list[First_word] * \
                                              wordseq_list[(First_word, Second_word)] * \
                                              (Likelihoods[m+t1]/word_list[Second_word])
                        else:
                            Likelihoods[m] += decimal.Decimal(0)
                else:
                    for t2 in list(range(t2Limit+1)):
                        if bool(word_list.get(First_word)):
                            Likelihoods[m] += word_list[First_word] * Likelihoods[m+t1]
                        else:
                            Likelihoods[m] += decimal.Decimal(0)
        else:
            if m + tauL > len(sentence):
                t1Limit = len(sentence)-m
            else:
                t1Limit = tauL
            for t1 in list(range(t1Limit+1))[1:]:
                First_word = sentence[m:m+t1]         
                if m + t1 + tauL > len(sentence):
                    t2Limit = len(sentence)-(m+t1)
                else:
                    t2Limit = tauL
                if t2Limit != 0:
                    for t2 in list(range(t2Limit+1))[1:]:
                        Second_word = sentence[m+t1 : m+t1+t2]
                        if bool(wordseq_list.get((First_word, Second_word))) & bool(ftword_list.get(First_word)) \
                            & bool(word_list.get(Second_word)):
                            Likelihoods[m] += ftword_list[First_word] * \
                                              wordseq_list[(First_word, Second_word)] * \
                                              (Likelihoods[m+t1]/word_list[Second_word])
                        else:
                            Likelihoods[m] += decimal.Decimal(0)
                else:
                    for t2 in list(range(t2Limit+1)):
                        if bool(ftword_list.get(First_word)):
                            Likelihoods[m] += ftword_list[First_word] * Likelihoods[m+t1]
                        else:
                            Likelihoods[m] += decimal.Decimal(0)
    return Likelihoods




def DPLikelihoodsForward(tauL, sentence, ftword_list, word_list, wordseq_list):   
    Likelihoods = [decimal.Decimal(0)] * (len(sentence)+1)
    Likelihoods[0] = decimal.Decimal(1)
    #print(sentence)
    for m in list(range(len(sentence)+1))[1:]:
        if m - tauL <= 0:
            t2Limit = m
        else:
            t2Limit = tauL
        for t2 in list(range(t2Limit)):
            Second_word = sentence[m-t2-1:m]
            if m - t2 - tauL <= 0:
                t1Limit = m - (t2 +1)
            else:
                t1Limit = tauL
            if t1Limit != 0:
                for t1 in list(range(t1Limit+1))[1:]:
                    First_word = sentence[m-t2-1-t1:m-t2-1]
                    if m-t2-1-t1 == 0:
                        if bool(wordseq_list.get((First_word, Second_word))) & bool(ftword_list.get(First_word)) \
                        & bool(word_list.get(Second_word)) :
                            Likelihoods[m] += Likelihoods[m-t2-1] * wordseq_list[(First_word, Second_word)]
                    else:
                        if bool(wordseq_list.get((First_word, Second_word))) \
                        & bool(word_list.get(First_word)) & bool(word_list.get(Second_word)):
                            Likelihoods[m] += Likelihoods[m-t2-1] * wordseq_list[(First_word, Second_word)]
            else:
                for t1 in list(range(t1Limit+1)):
                    First_word = sentence[m-t2-1-t1:m-t2-1]
                    if bool(ftword_list.get(Second_word)):
                        Likelihoods[m] += Likelihoods[m-t2-1] * ftword_list[Second_word]
    return Likelihoods




def updateDictionary1(texts, tauL, ftword_list, word_list, wordseq_list):
    ny = {}
    for sentence in texts:
        Likelihoods = DPLikelihoodsBackward(tauL, sentence, ftword_list, word_list, wordseq_list)
        #print(Likelihoods[0])
        Expectations1 = DPExpectations1(tauL, sentence, word_list, wordseq_list, Likelihoods) 
        for key, value in Expectations1:
            ny[key] = ny.get(key, 0) + value
    sum_y_ny = sum(ny.values())
    for key in ny.keys():
        ny[key] =  ny[key]/sum_y_ny 
    return ny




def DPExpectations1(tauL, sentence, word_list, wordseq_list, Likelihoods):
    ny = DPCache1(tauL)
    for m in list(reversed(range(len(sentence)))):
        if m + tauL > len(sentence):
            t1Limit = len(sentence)-m
        else:
            t1Limit = tauL
        cut_and_rho = []
        for t1 in list(range(t1Limit+1))[1:]:
            First_word = sentence[m:m+t1]
            if m + t1 + tauL > len(sentence):
                t2Limit = len(sentence)-(m+t1)
            else:
                t2Limit = tauL
            rho = Decimal(0)
            if t2Limit != 0:
                for t2 in list(range(t2Limit+1))[1:]:
                    Second_word = sentence[m+t1 : m+t1+t2]
                    if bool(word_list.get(First_word)) & bool(word_list.get(Second_word)) & bool(wordseq_list.get((First_word, Second_word))):
                        candidate_wordseq = (First_word, Second_word)
                        rho += (word_list[First_word] * wordseq_list[candidate_wordseq] * Likelihoods[m+t1] \
                                / word_list[Second_word]) \
                                / Likelihoods[m]
            else:
                if bool(word_list.get(First_word)):
                    rho += word_list[First_word]/Likelihoods[m]
            cut_and_rho.append( (First_word,t1,rho) ) 
        ny.push(cut_and_rho)
    return(ny.top())




class DPCache1:
   
    def __init__(self, tauL):
        self.tauL = tauL
        self.cache = {}
        self.cache_top = []

    def push(self, cut_and_rho):
        for cuttings in cut_and_rho:
            # cuttings = (First_word, t1, rho)
            if not bool(self.cache.get(cuttings[0])):
                self.cache[cuttings[0]] = LimitStack(self.tauL,0)
        for word in self.cache:
            push_value = 0
            for cuttings in cut_and_rho:
                if cuttings[0] == word:
                    push_value += cuttings[2] * (1 + self.cache[word].get(cuttings[1]-1))
                else:
                    push_value += cuttings[2] * self.cache[word].get(cuttings[1]-1)
            self.cache[word].push(push_value)
    
    def top(self):
        for word in self.cache.keys():
            self.cache_top.append((word, self.cache[word].top()))
        return self.cache_top
   


class LimitStack:
    
    def __init__(self, size, initial_value):
        self.size = size
        self.initial_value = initial_value
        self.stack = [self.initial_value] * self.size
        self.head = self.size -1
        
    def push(self, element):
        if self.head + 1 >= self.size:
            self.head = 0
        else:
            self.head += 1
        self.stack[self.head] = element
    
    def get(self, idx):
        if idx >= self.size:
            idx = self.size - 1
        if self.head - idx < 0:
            pos = self.size + self.head - idx
        else:
            pos = self.head - idx
        return self.stack[pos]
    
    def top(self):
        return self.get(0)





def updateDictionaryft(texts, tauL, ftword_list, word_list, wordseq_list):
    ny = {}
    for sentence in texts:
        Likelihoods = DPLikelihoodsBackward(tauL, sentence, ftword_list, word_list, wordseq_list)
        Expectationsft = DPExpectationsft(tauL, sentence, ftword_list, word_list, wordseq_list, Likelihoods)
        for key, value in Expectationsft:
            ny[key] = ny.get(key,0) + value
    sum_y_ny = sum(ny.values())
    for key in ny.keys():
        ny[key] =  ny[key]/sum_y_ny
    return ny



# check till here
# delete all timer
def DPExpectationsft(tauL, sentence, ftword_list, word_list, wordseq_list, Likelihoods):
    nys = []
    for m in [0]:
        if m + tauL > len(sentence):
            t1Limit = len(sentence)-m
        else:
            t1Limit = tauL
        for t1 in list(range(t1Limit+1))[1:]:
            First_word = sentence[m:m+t1]
            thetaft = Decimal(0)
            if bool(ftword_list.get(First_word)):
                if m + t1 + tauL > len(sentence):
                    t2Limit = len(sentence)-(m+t1)
                else:
                    t2Limit = tauL

                if t2Limit != 0:
                    for t2 in list(range(t2Limit+1))[1:]:
                        Second_word = sentence[m+t1 : m+t1+t2]
                        if bool(wordseq_list.get((First_word,Second_word))) & bool(ftword_list.get(First_word)) & bool(word_list.get(Second_word)):
                            thetaft += (ftword_list[First_word] *\
                                            wordseq_list[(First_word, Second_word)] *\
                                            (Likelihoods[m+t1]/word_list[Second_word]))                            
                else:
                    for t2 in list(range(t2Limit+1)):
                        thetaft += ftword_list[First_word]
                nys.append((First_word, thetaft))
    return nys





def updateDictionary2(texts, tauL, ftword_list, word_list, wordseq_list):
    nxy = {}
    for sentence in texts:
        Likelihoods = DPLikelihoodsBackward(tauL, sentence, ftword_list, word_list, wordseq_list)
        Expectations2= DPExpectations2(tauL, sentence, ftword_list, word_list, wordseq_list, Likelihoods) 
        for key, value in Expectations2:
            nxy[key] = nxy.get(key, 0) + value
    sum_y_nxy = {k[0]:0 for k in nxy.keys()}
    smooth_list = []
    for wordseq in nxy.keys():
        sum_y_nxy[wordseq[0]] += nxy[wordseq]
    for wordseq in sum_y_nxy.keys():
        if sum_y_nxy[wordseq] > Decimal(0):
            smooth_list.append(sum_y_nxy[wordseq])
    for wordseq in sum_y_nxy.keys():
        if sum_y_nxy[wordseq] <= Decimal(0):
            sum_y_nxy[wordseq] = min(smooth_list)
    for key in nxy.keys():
        nxy[key] =  nxy[key]/sum_y_nxy[key[0]] 
    return nxy




def DPExpectations2(tauL, sentence, ftword_list, word_list, wordseq_list, Likelihoods):
    nxy = DPCache2(tauL)
    for m in list(reversed(range(len(sentence)))):
        cut_and_rho = []
        if m + tauL > len(sentence):
            t1Limit = len(sentence)-m
        else:
            t1Limit = tauL
        if m == 0:
            for t1 in list(range(t1Limit+1))[1:]:
                First_word = sentence[m:m+t1]
                if m + t1 + tauL > len(sentence):
                    t2Limit = len(sentence)-(m+t1)
                else:
                    t2Limit = tauL
                if t2Limit != 0:
                    for t2 in list(range(t2Limit+1))[1:]:
                        Second_word = sentence[m+t1 : m+t1+t2]
                        if bool(ftword_list.get(First_word)) & bool(word_list.get(Second_word)) & bool(wordseq_list.get((First_word, Second_word))):
                            candidate_wordseq = (First_word, Second_word)
                            rho = (ftword_list[First_word] * wordseq_list[candidate_wordseq] * Likelihoods[m+t1] / word_list[Second_word])/Likelihoods[m]
                            cut_and_rho.append(((First_word, Second_word), t1, t2, rho))
        else:
            for t1 in list(range(t1Limit+1))[1:]:
                First_word = sentence[m:m+t1]
                if m + t1 + tauL > len(sentence):
                    t2Limit = len(sentence)-(m+t1)
                else:
                    t2Limit = tauL
                if t2Limit != 0:
                    for t2 in list(range(t2Limit+1))[1:]:
                        Second_word = sentence[m+t1 : m+t1+t2]
                        if bool(word_list.get(First_word)) & bool(word_list.get(Second_word)) & bool(wordseq_list.get((First_word, Second_word))):
                            candidate_wordseq = (First_word, Second_word)
                            rho = (word_list[First_word] * wordseq_list[candidate_wordseq] * Likelihoods[m+t1] / word_list[Second_word])/Likelihoods[m]
                            cut_and_rho.append(((First_word, Second_word), t1, t2, rho))
        nxy.push(cut_and_rho)
    return(nxy.top())




class DPCache2:


    def __init__(self, tauL):
        self.tauL = tauL
        self.cache = {}
        self.cache_top = []


    def push(self, cut_and_rho):
        for cuttings in cut_and_rho:
            # cuttings = ((First_word, Second_word), t1, t2, rho)
            if not bool(self.cache.get(cuttings[0])):
                self.cache[cuttings[0]] = LimitStack(self.tauL*2,0)
        for wordseq in self.cache:
            push_value = 0
            for cuttings in cut_and_rho:
                if cuttings[0] == wordseq:
                    push_value += cuttings[3] * (1 + self.cache[wordseq].get(cuttings[1]+cuttings[2]-1))
                else:
                    push_value += cuttings[3] * self.cache[wordseq].get(cuttings[1]+cuttings[2]-1)
            self.cache[wordseq].push(push_value)
    

    def top(self):
        for wordseq in self.cache.keys():
            self.cache_top.append((wordseq, self.cache[wordseq].top()))
        return self.cache_top

def pruneDictionaryft(ftword_list, useProbThld1): 
    smooth_list = [] 
    # Filter theta higher than useProbThld1.
    ftword_list = {k: v for k, v in dict(Counter(ftword_list)).items() if len(k) == 1 or v >= useProbThld1}
    # Smoothing theta.
    for key in ftword_list.keys():
        if ftword_list[key] > Decimal(useProbThld1):
            smooth_list.append(ftword_list[key])
    for key in ftword_list.keys():
        if ftword_list[key] <= Decimal(useProbThld1):
            ftword_list[key] = min(smooth_list)
    # Doing normalize again.
    sum_y_ny = sum(ftword_list.values())
    for key in ftword_list.keys():
        ftword_list[key]=ftword_list[key]/sum_y_ny
    return ftword_list




def pruneDictionary1(word_list, useProbThld1):
    smooth_list = []
    # Filter theta higher than useProbThld1.
    word_list = {k: v for k, v in dict(Counter(word_list)).items() if len(k)==1 or v >= useProbThld1}
    # Smoothing theta.
    for key in word_list.keys():
        if word_list[key] > Decimal(useProbThld1):
            smooth_list.append(word_list[key])
    for key in word_list.keys():
        if word_list[key] <= Decimal(useProbThld1):
            word_list[key] = min(smooth_list)
    # Doing normalize.
    sum_y_ny = sum(word_list.values())
    for key in word_list.keys():
        word_list[key]=word_list[key]/sum_y_ny
    return word_list



def pruneDictionary2(wordseq_liist, useProbThld2):
    wordseq_list = {k: v for k, v in dict(Counter(wordseq_liist)).items() if v >= useProbThld2 or len(k[0])==1 or len(k[1])==1 } 
    sum_wordseqfreq = {k[0]:0 for k in wordseq_list.keys()}
    result = {}
    # Smooth alpha, making min alpha be useProbThld2.
    for wordseq in wordseq_list.keys():
        if wordseq_list[wordseq] <= Decimal(useProbThld2):
            wordseq_list[wordseq] = Decimal(useProbThld2)
    for wordseq in wordseq_list.keys():
        sum_wordseqfreq[wordseq[0]] += wordseq_list[wordseq]
    for wordseq in wordseq_list.keys():
        result[wordseq] = wordseq_list[wordseq]/sum_wordseqfreq[wordseq[0]]
    return result



def MLSegmentation(texts, connectThld, tauL, ftword_list, wordseq_list):
    result_texts = []
    for sentence in texts:
        m = 0
        seg = []
        boundary = []
        while m < len(sentence):
            candidate = []
            Aft = ("",0)
            Asq = (("",""),0)
            if m == 0:
                if m + tauL > len(sentence):
                    tLimit = len(sentence)-m
                else:
                    tLimit = tauL
                for t in list(range(tLimit)):
                    ftword = sentence[m:m+t+1]
                    if bool(ftword_list.get(ftword)):
                        candidate.append(ftword)
                for word in candidate:
                    if ftword_list[word] > Aft[1]:
                        Aft = (word, ftword_list[word])
                    elif ftword_list[word] == Aft[1] and len(word) > len(Aft[0]):
                        Aft = (word, ftword_list[word])
                #print("Aft",Aft)
                seg.append(len(Aft[0]))
                boundary.append([len(Aft[0]), 1] )
                m += len(Aft[0])
                
            else:
                First_word = sentence[m-seg[-1]:m]
                if m + tauL > len(sentence):
                    tLimit = len(sentence)-m
                else:
                    tLimit = tauL
                for t in list(range(tLimit)):
                    Second_word = sentence[m:m+t+1]
                    if bool(wordseq_list.get((First_word, Second_word))):
                        candidate.append( (First_word, Second_word) )
                for wordseq in candidate:
                    if wordseq_list[wordseq] > Asq[1]:
                        Asq = (wordseq, wordseq_list[wordseq])
                    elif wordseq_list[wordseq] == Asq[1] and len(wordseq[1]) > len(Asq[0][1]):
                        Asq = (wordseq, wordseq_list[wordseq])
                seg.append(len(Asq[0][1]))
                if Asq[1] >= connectThld:
                    boundary[-1][1] = 0
                boundary.append( [len(Asq[0][1])+boundary[-1][0], 1])
                m += len(Asq[0][1])
        result_texts.append(segmentation(sentence, boundary))
    return result_texts
    


def segmentation(sentence, boundary):
    idx = 0
    for i in boundary:
        if i[1] == 1:
            sentence=sentence[:i[0]+idx]+"|"+sentence[i[0]+idx:]
            idx+=1
    return sentence

class WDMtwseq(object):
    
    def __init__(self, corpus, 
                 tauL = 10, tauF = 3, 
                 iter_time_total = 10, convergeThld = 0.1, 
                 useProbThld1 = 10e-10, useProbThld2 = 10e-8, 
                 segmenThld = 0.1):
        self.corpus = corpus
        self.tauL = tauL
        self.tauF1 = tauF
        self.tauF2 = tauF
        self.iter_time_total = iter_time_total
        self.convergeThld = Decimal(convergeThld)
        self.useProbThld1 = Decimal(useProbThld1)
        self.useProbThld2 = Decimal(useProbThld2)
        self.segmenThld = Decimal(segmenThld)
    
    
    def run(self):
        texts = preprocessing(self.corpus)
        self.texts = texts
        self.word_list    =    cut_word(texts, self.tauL, self.tauF1, self.useProbThld1)
        self.ftword_list  =  cut_ftword(texts, self.tauL, self.tauF1, self.useProbThld1)
        self.wordseq_list = cut_wordseq(texts, self.tauL, self.tauF2, self.useProbThld2)
        total_iter_time = self.iter_time_total
        iter_time_now = 1
        convergence = False
        last_Likelihoods = 0
        while iter_time_now <= total_iter_time and convergence == False :
            new_word_list    = updateDictionary1 (self.texts, self.tauL, self.ftword_list, self.word_list, self.wordseq_list)
            new_ftword_list  = updateDictionaryft(self.texts, self.tauL, self.ftword_list, self.word_list, self.wordseq_list)
            new_wordseq_list = updateDictionary2 (self.texts, self.tauL, self.ftword_list, self.word_list, self.wordseq_list)
            new_word_list    = pruneDictionary1 (   new_word_list, self.useProbThld1)
            new_ftword_list  = pruneDictionaryft( new_ftword_list, self.useProbThld1)
            new_wordseq_list = pruneDictionary2 (new_wordseq_list, self.useProbThld2)
            now_Likelihoods  = 0
            for sentence in self.texts:
                FL  = DPLikelihoodsForward(self.tauL, sentence, new_ftword_list, new_word_list, new_wordseq_list)
                FL1 = math.log(FL[-1])
                now_Likelihoods += FL1
            Likelihoods_ratio = last_Likelihoods/now_Likelihoods
            if bool(iter_time_now != 1) and bool( abs(1 - Likelihoods_ratio) <= self.convergeThld ):
                convergence  = True
            last_Likelihoods = now_Likelihoods
            self.word_list = new_word_list
            self.ftword_list = new_ftword_list
            self.wordseq_list = new_wordseq_list
            iter_time_now += 1
       

    def cut(self, connectThld):
        return MLSegmentation(self.texts, connectThld, self.tauL, self.ftword_list, self.wordseq_list)
        # Finally, return a segmented corpus.