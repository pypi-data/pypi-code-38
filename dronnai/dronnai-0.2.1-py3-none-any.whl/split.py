import torch
import logging
import numpy as np
from spacy.lang import pl
from torchtext.vocab import Vectors
from torch import nn
from sklearn.cluster import MiniBatchKMeans
from tqdm import tqdm
from sklearn.model_selection import train_test_split
import pandas as pd

tqdm.pandas()

def split(data, label_field, text_fileds, train_frac=0.8, dev=False, clust_func=None, vec_func=None, clust_out_frac=0.1):
    """
    data: pd.DataFrame base on which you would like to make a split, should contain whole
    label_field: name of the column with label
    text_fields: names of the columns with text based on which split should be made
    train_frac: fraction of whole dataset which should be assign to trainset
    dev: if test set should be spllited for two seprate datasets
    vec_func: function which can take pd.Series and return np.array which represents text in pd.Series data
    clust_fuc: function which can take 2D numpy array and return numpy array with clusters numbers
    return - separate pd.DataFrames
    """
    if not clust_func:
        clust_func = conf_clustering(int(len(data)/15))
    if not vec_func:
        vec_func = Text2Vec(cache='data')
    
    if isinstance(text_fileds,list):
        vecs = []
        for text_field in text_fileds:
            vecs.append(vec_func(data[text_field]))
        
        vecs = np.concatenate(vecs,axis=1) 
        
    else:
        vecs = vec_func(data[text_field])
      
    clusters = clust_func(vecs)
    unique = np.unique(clusters, return_counts=True)
    
    i = -1
    while True:
        if len(clusters[np.isin(clusters,unique[0][unique[1]==1])]) == 0:
            break
        clusters[np.isin(clusters,unique[0][unique[1]==1])] = i
        i += 1
        
    data['cluster'] = clusters
    test_size = int(len(data)*(1-train_frac))
    clust_out_size = int(test_size*clust_out_frac)
    
    test_clusters = []
    for cluster in clusters:
        if len(data[data['cluster'].isin(test_clusters)]) >= clust_out_size:
            break
        if len(data[data['cluster']==cluster]) > (clust_out_size/3):
            continue
        test_clusters.append(cluster)

    train = data[~data['cluster'].isin(test_clusters)]
    test1 = data[data['cluster'].isin(test_clusters)]
    
    test_size = int((test_size-len(test1))/2)
    train, test2 = train_test_split(train, test_size=test_size, stratify=train['cluster'], random_state=1)
    train, test3 = train_test_split(train, test_size=test_size, stratify=train[label_field], random_state=1)
    test = pd.concat([test1,test2,test3])
    
    train.drop(columns='cluster',inplace=True)
    test.drop(columns='cluster',inplace=True)
    
    if dev:
        dev, test = train_test_split(test, test_size=0.5, stratify=test[label_field], random_state=1)
        return train, dev, test
    else:
        return train, test
    
class Text2Vec:
    """
    Class which help to prepare fixed length vector representation of text
    """
    def __init__(self,name='wiki.pl.vec',cache=None,url='https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.pl.vec',mode='sum'):
        """
        name: name of Embeddings compatible with torchtext Vectors
        cache: where to store embeddings
        mode: what agg func should be used, could be one of "sum", "mean", "max"
        """
        self.tokenizer = pl.Polish()
        self.vec = Vectors(name=name, cache=cache, url=url)
        self.emb = nn.EmbeddingBag(self.vec.vectors.size(0),
                             self.vec.vectors.size(1), mode=mode)
        self.emb.weight.data = self.vec.vectors.data
        
    def emb_bag(self,text):
        tokens = [token.text for token in self.tokenizer(str(text), disable=['parser', 'tagger', 'ner'])]
        idxs = []
        for token in tokens:
            idx = self.vec.stoi.get(token)
            if isinstance(idx, int):
                idxs.append(idx)
        if len(idxs) == 0:
            return torch.zeros(300).numpy()
        else:
            vector = self.emb(torch.Tensor(idxs).long().unsqueeze(0))
            return vector.detach().numpy()[0]
        
    def vectorisation(self,data):
        """
        data: should be pd.Series with text data
        return - np.array of vectorised texts
        """
        return np.stack(data.progress_apply(self.emb_bag).values)
    
    def __call__(self,data):
        return self.vectorisation(data)
        

def conf_clustering(n_clusters,max_iter=50,max_no_improvement=5):
    """
    configurator of clustering function for sklearn's MiniBatchKMeans
    n_clusters: nr of clusters
    max_iter: max algorithm iteratrion (one interation means iteration over whole dataset)
    max_no_improvement: max iteration without any improvement (one interation means iteration over whole dataset)
    return - function for running clustering 
    """
    km = MiniBatchKMeans(n_clusters=n_clusters,
                         max_iter=max_iter,
                         batch_size=n_clusters*5,
                         random_state=1,
                         max_no_improvement=max_no_improvement,
                         verbose=True)
    def clustering(array):
        """
        array: should be 2D numpy array
        """
        clusters = km.fit_predict(array)
        return clusters
    return clustering
    