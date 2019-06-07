# READ IN THE XTILDE data # Classify the CELLS based on nearest neighbors algorithm.
# On input we expect a matrix of dim (nxp)
# n is num cells, p is num genes. We anticipate the input
# matrix (X) has been processed for group effects standardized to N(0,1)
#
# We cluster Xtilde but fit regression based on the current values of R
#
# NOTE: distances/indices are relative to the particular rows. BUT, since the row is in the training
# set it gets returned as a nearest neighbor. SO we want to set k = k+1 and ten exclude the 
# redundant terms

# generateNeighborMatrixClass.py

# takes about 15,000 secs to proces the clustering
# Maybe we should use a smaller training set to do the predictions
# May want to explore training on a subset of cells to minimize time

# Example input variables
#k=10
#inputfilename='100_MOUSEDATESEXTREATMENT_Xtilde_ZscoreOrder.tsv'
#outputIndices = 'dfIndices.tsv'
#outputDistances = 'dfDistances.tsv'

import pandas as pd
import numpy as np
#import math
#import matplotlib.pyplot as plt
#import sklearn.preprocessing
#from sklearn import preprocessing
#from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import sys
import time as tm
from sklearn.model_selection import train_test_split
from sklearn.externals.joblib import Parallel, delayed

########################################################
def constructHeaderNames(kp1):
    headers=list()
    headers.append('CELL')
    #headers.append('CELLTARGET') # NOT TRUE based on NN bahavior
    for i in range(0,kp1):
       headers.append('NN'+str(i))
    return(headers)

########################################################

class generateNeighborMatrixClass(object):
    """Compute the K matrix. K is an (n*k) matrix (cells by neighbors
    We want indices and distance matrices. These matrices will be passed to
    a regression code for imputation
    Num neighbors: k+1: Because we also include the TARGET cell in the fit of k neighbors 
    output index file: 'dfIndices.tsv' 
    output distance file 'dfDistances.tsv'

    Attributes
    k = Number of nearest neighbors to fit
    infilename = filename for the Xtilde file returned from projectGroupDataClass
    outputIndeciesFilename = output indices filename
    outputDistancesFilename = output distances filename
    outputIndices = outputs object (not used by the pipeline) 
    outputDistances = outputs object (not used by the pipeline) 
    njobs = number of local threads to launch (16 or less is a good choice)
    """

    def __init__(self, k, infilename, outindex, outdistance, njobs=None):
        self.k = k
        self.inputfilename = infilename
        self.outputIndicesFilename = outindex
        self.outputDistancesFilename = outdistance
        self.outputIndices = pd.DataFrame()
        self.outputDistances = pd.DataFrame()
        self.njobs = njobs

    def reportIndices(self):
        return (self.outputIndices)
    def reportDistances(self):
        return (self.outputDistances)

    def reportParameters(self):
        print('input k neighbors '+str(self.k))
        print('input Xtilde '+self.inputfilename)
        print('output indexing '+self.outputIndicesFilename)
        print('output distances '+self.outputDistancesFilename)

    def writeClusterInformation(self):
        self.outputIndices.to_csv(self.outputIndicesFilename,sep=' ')
        self.outputDistances.to_csv(self.outputDistancesFilename,sep=' ')
        print('Writing of index/distance data is completed')

    def getIndexFilename(self):
        return self.outputIndicesFilename

    def getDistanceFilename(self):
       return self.outputDistancesFilename

    def runProcess(self):
        k=self.k
        inputfilename = self.inputfilename
        
        df_X = pd.read_table(inputfilename,delim_whitespace=True, index_col=0,header=0,low_memory=False)
        cellsIndex = df_X.index.values

        print('Input data dimensions is '+ str(df_X.shape))
        
        ########################################################
        # Prepare data for the KNN. Specify training and test sets
        # And standarized based on parameters from the training set ( is that contamination?)
        
        #train_set,test_set = train_test_split(df_X,test_size=0.8,random_state=42)
        full_set = df_X.values
        
        # The following standardizes but also converts to NUMPY
        # Not required as Xtilde was already scaled
        #scaler = StandardScaler()  
        #scaler.fit(full_set)
        #full_set = scaler.transform(full_set)
        
        #######################################################
        # Choice of algorithm: algorithm='brute' not good for large data sets
        # Returns distances,indices of rank nxk
        # k+1 because we want k neighbors besides the target point not including it
        # Takes about 5 hours using the whole set on a single core
        
        cluster_set=full_set
        #cluster_set = train_set

        print('Cluster: n_jobs is set to '+str(self.njobs))
        print('Dims of data set to be cluster fit '+str(cluster_set.shape))
        t0 = tm.time()
        #nbrs = NearestNeighbors(n_neighbors=k+1, algorithm='ball_tree',n_jobs=self.njobs).fit(cluster_set)
        #### Does contain the target index when set is FULL maybe not if it is not full
        print('Cluster using the DF data objects')

        nbrs = NearestNeighbors(n_neighbors=k+1, algorithm='ball_tree',n_jobs=self.njobs).fit(cluster_set)
        distances, indices = nbrs.kneighbors(full_set)
        # nbrs.kneighbors_graph(full_set).toarray()
        print('Time to process the clustering is '+str(tm.time()-t0))
        
        # NOTE: is you request the neighbors for a point in the training set that point will be returned even though it overlaps
        # print(neigh.kneighbors([[1., 1., 1.]])) 
        
        # NOTE I have demonstrated that sometimes the order is not what we want. Viz., the target is 
        # NOT always first. Here are a few lines from a indices file:
        #   these are snippets from a text file. NOTE the duplicated rows The first 2549 should be 2839
        # 2840 MB05_CTTCGCGCTAAA 2838 2824 3029 2867 2791 2722 2421 2716 2685 2671 2775
        # 2841 MB05_TGCTAACAGCGA 2549 2839 3035 2757 2872 2781 2898 2771 2525 2599 2728
        # 2550 MB05_GCCTAAATGCAC 2548 3049 2937 2599 2525 2771 2872 2898 2479 2757 3035
        # 2551 MB05_AGTGGTGGCGAA 2549 2839 3035 2757 2872 2781 2898 2771 2525 2599 2728
        # 2552 MB05_CCCAGGGGAACG 2550 2249 2379 2658 2285 2539 2400 2474 2373 2168 2357
        #
        # Construct header line
        headers = constructHeaderNames(k+1)
        df_indices = pd.DataFrame(indices)
        df_indices['CELL'] = cellsIndex[df_indices.index.values] # Assumes implied order is the cell order plus 
        df_indices.set_index('CELL',inplace=True)
        df_indices.columns=headers[1:]
        
        df_distances = pd.DataFrame(distances)
        df_distances['CELL'] = cellsIndex[df_distances.index.values]
        df_distances.set_index('CELL',inplace=True)
        df_distances.columns=headers[1:]

        self.outputIndices = df_indices
        self.outputDistances = df_distances

        ########################################################
        print('clustering procedure completed')
