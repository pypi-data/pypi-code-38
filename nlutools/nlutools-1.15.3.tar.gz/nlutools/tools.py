from rpc_client import *
from config import *
from utils import *
from online_bert_client import bert_vector

import subprocess


# Segment
def cut(sentence,pos=True,cut_all=False,mode='fast'):
    try:
        if mode in ['fast','accurate'] and pos in [True,False] and cut_all in [True,False]:
            data={'text':sentence,'mode':mode,'pos':pos,'cut_all':cut_all}
            serverName='segmentor'
            return doTask(serverName,data)
        else:
            raiseException('Advise:check parameters,make sure value of mode is fast or default , value of pos is true,false or default as well')
    except Exception as e:
            raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%(serverName,supportConf[serverName],e))

# Word2Vector
def getW2VFile(version_key,localpath):
    try:
        if not version_key or not version_key.strip():
            cat = subprocess.Popen(['hadoop', 'fs', '-cat', mapConf['w2v_hdfs_version_file']], stdout=subprocess.PIPE)
            for line in cat.stdout:
                version_key=bytes.decode(line).strip()
                break;
        if version_key and version_key.strip():
            try:
                subprocess.call(['hadoop','fs','-get',mapConf['w2v_hdfs_dir']+version_key.lower(),localpath])
            except Exception as e:
                raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%('w2v',supportConf['w2v'],e))
    except Exception as e:
            raise Exception('Advise: please install hadoop client before use getW2VFile')

def getWordVec(word):
    try:
        if isinstance(word,str):
            word = [word]
        data = {'words':word}
        serverName='w2v'
        return doTask(serverName,data)
    except Exception as e:
        raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%(serverName,supportConf[serverName],e))

def getMostSimiWords(word,topn=10):
    try:
        data = {'words':word,'topn':topn}
        serverName='w2v'
        return doTask(serverName,data)
    except Exception as e:
        raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%(serverName,supportConf[serverName],e))

def getCharacterVec(character):
    pass

# Sentence2Vector
def getSentenceVec(sentences):
    try:
        if isinstance(sentences,list):
            data = {'senlist':sentences}
            serverName='sentencevec'
            return doTask(serverName,data)
        return None
    except Exception as e:
        raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%(serverName,supportConf[serverName],e))
    
# LanguageModel

# EmotionParser
def predictEmotion(sentences, prob=False):
    try:
        if sentences:
            data = {'text':sentences,'prob':prob}
            serverName='sentiment'
            return doTask(serverName,data)
        return None
    except Exception as e:
        raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%(serverName,supportConf[serverName],e))

# SentenceSpliter
def getSubSentences(sentence,mode=0):
    try:
        if mode == 0 or mode == 1:
            data={'sentence':sentence,'mode':mode}
            serverName='sentence_spliter'
            return doTask(serverName,data)
        else:
            raiseException('Advise: make sure value of mode is 0 or 1')
    except Exception as e:
        raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%(serverName,supportConf[serverName],e))

#EntityParser

#SentenceTypeParser

bertVector = bert_vector()
def getBertSentenceVec(texts,mode):
    try:
        bertVector.buildConnection()
        result = bertVector.parse(texts,mode)
        bertVector.close(mode)
        return result
    except Exception as e:
        raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%('sentence vector',supportConf['bert_service'],e))


def getKeywords(content,topk,with_weight):
    try:
        data = {'content':content,'topk':topk,'with_weight':with_weight}
        serverName='keywords'
        return doTask(serverName,data)
    except Exception as e:
        raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%(serverName,supportConf[serverName],e))

def getSentenceSimi(text1,text2,precision):
    try:
        data = {'text1':text1,'text2':text2,'precision':precision}
        serverName='sentencesim'
        return doTask(serverName,data)
    except Exception as e:
        raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%(serverName,supportConf[serverName],e))

def getVOB(content,mode):
    try:
        data = {'content':content,'mode':mode}
        serverName='verbobject'
        return doTask(serverName,data)
    except Exception as e:
        raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%(serverName,supportConf[serverName],e))

def getSentenceRationality(text,with_word_prob):
    try:
        data = {'text':text,'word_prob':with_word_prob}
        serverName='rationality'
        return doTask(serverName,data)
    except Exception as e:
        raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%(serverName,supportConf[serverName],e))

def doEntityTask(text,m):
    try:
        serverName='entity'
        return doCustomTask(serverName,text,m)
    except Exception as e:
        raiseException('%s exception \nplease contact supporter %s for this exception ! \n%s'%(serverName,supportConf[serverName],e))
    
