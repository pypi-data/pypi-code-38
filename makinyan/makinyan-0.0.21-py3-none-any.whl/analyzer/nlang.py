#!-*-coding:utf-8-*-
import os
import sys
import MeCab
import numpy as np
sys.path.append("../")
import makinyan as mak
from pandas import Series
from sklearn.feature_extraction.text import TfidfVectorizer

__all__ = []
__all__ += ["tf","tfidf"]


def tfidf( mat ):
    """
    TF IDF
    """
    arr = []
    token = MeCab.Tagger("-O wakati")
    for m in mat:
        arr.append( token.parse(m) )

    vecliz = TfidfVectorizer(use_idf=True, token_pattern=u'(?u)\\b\\w+\\b')
    vecs = vecliz.fit_transform( arr )

    return vecs.toarray()


def tf( text ):
    """
    Term frequency
    """
    
    token = MeCab.Tagger("-O wakati")
    node = token.parseToNode(text)
    voc_mat = []
    while node:
        vocab = node.feature.split(",")[6]
        part = node.feature.split(",")[0]
        if part in ["名詞","固有名詞","動詞"]:
            voc_mat.append( vocab )

        node = node.next

    ser = Series( mak.group_hist( voc_mat ) )
    ser = ser.sort_values(ascending=False)

    return dict( ser )
