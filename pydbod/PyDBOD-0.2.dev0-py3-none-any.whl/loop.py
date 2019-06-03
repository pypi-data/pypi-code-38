# -*- coding: utf-8 -*-
"""
@author: Miguel Ángel López Robles
"""


import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import DistanceMetric
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from scipy.special import erf
# function to load a data file 
def load_data(data_file, sep = ','):
    f = open(data_file,'r')
    lines = f.readlines()
    result = []
    for line in lines:
        line = line.split(sep)
        if '@' not in line[0]:
            if line[len(line)-1] == 'negative\n':
                line[len(line)-1] = '0'
            else:
                line[len(line)-1] = '1'
            result.append(np.array(line,dtype=np.float))
    
    result = np.array(result)
    #print("result")
    #print(result)
    return result
    
# LoOP function
def loop(data, k=20, lamda=3):

    nbrs = NearestNeighbors(n_neighbors=k, algorithm='ball_tree').fit(data)
    distances, indices = nbrs.kneighbors(data)

    
    n_points = distances.shape[0]




    #calculate the standar distances 
    standar_distances = np.sqrt( np.sum( np.power(distances,2), axis=1 ) / n_points )

    #calculate the probabilistic distances
    p_distances = lamda * standar_distances
    #print("distancias probabilisticas")
    #print(p_distances)

    #calculate the probabilistic Local Outlier Factor
    plof = p_distances /  [ np.sum([p_distances[j] for j in indices[i] ]) for i in indices]
    #we eliminate the -1 because we assume that the data is distributed from 0

    print("plof")
    print(plof)
    #calculate de normalized probabilistic local outlier factor
    nplof = lamda * np.sqrt( np.mean( np.power( plof, 2) ) )

    #apply the Gaussian Error Function to obtain the Local Outlier Probability
    
    loop = np.maximum(0, erf( plof / ( nplof * np.sqrt(2) ) ) )
    print(loop)

    

    return loop




########################
### test with data generated
##################
np.random.seed(42)

# Generate train data
X_inliers = 0.3 * np.random.randn(100, 2)
X_inliers = np.r_[X_inliers + 2, X_inliers - 2]

# Generate some outliers
X_outliers = np.random.uniform(low=-4, high=4, size=(20, 2))
X = np.r_[X_inliers, X_outliers]

n_outliers = len(X_outliers)
ground_truth = np.ones(len(X), dtype=int)
ground_truth[-n_outliers:] = -1


# use my function
coef = loop(X,k=20,lamda=2)
#print(coef)


'''
probedata = clf.fit_predict(data)
print(clf.threshold_)
'''

plt.title("Local Outlier Factor (LOF)")
plt.scatter(X[:, 0], X[:, 1], color='k', s=3., label='Data points')
# plot circles with radius proportional to the outlier scores
radius = (coef - coef.min()) / (coef.max() - coef.min())
plt.scatter(X[:, 0], X[:, 1], s=1000 * coef, edgecolors='r',
            facecolors='none', label='Outlier scores')
plt.axis('tight')
plt.xlim((-5, 5))
plt.ylim((-5, 5))
#plt.xlabel("prediction errors: %d" % (n_errors))
legend = plt.legend(loc='upper left')
legend.legendHandles[0]._sizes = [10]
legend.legendHandles[1]._sizes = [20]
plt.show()