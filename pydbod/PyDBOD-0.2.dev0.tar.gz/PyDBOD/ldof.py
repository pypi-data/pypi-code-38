# -*- coding: utf-8 -*-
"""
@author: Miguel Ángel López Robles
"""


import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import DistanceMetric
import matplotlib.pyplot as plt


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


# LDOF function
def ldof(data, n=10, k=20):

    nbrs = NearestNeighbors(n_neighbors=k, algorithm='ball_tree').fit(data)
    distances, indices = nbrs.kneighbors(data)

    #calculate KNN distace of x_p,excluding x_p
    d_xp = np.average(distances[:,1:],axis =1)
    

    #calculate KNN inner distance of x_p
    #we have calculated the k-nerarest distance of the element
    #but we don't know if they are reciprocal neighbors. For this
    #reason we have to recalculate distances between de set N_p

    inner_distances = [nbrs.kneighbors(data[i])[0] for i in indices]

    inner_distances = np.array(inner_distances)

    #remove self distances ( i != i)
    inner_distances = inner_distances[:,:,1:]

    

    D_xp = [ np.sum(elemt) for elemt in inner_distances]
    D_xp = np.array(D_xp)
    D_xp = D_xp / ( k*(k-1))
    #print(D_xp)
    #print(D_xp.shape)

    # calculate the LDOF coeficients
    ldof = d_xp / D_xp
    
    print(ldof>1.4)
    return ldof




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

'''
for i in range(2,10):
    if True in ldof(X,k=i):
        print("hola")
        print(i)
'''
# take coef and see it
coef = ldof(X,k=7)

# plot the result

plt.title("Local Distance-Based Outlier Factor (LDOF)")
plt.scatter(X[:, 0], X[:, 1], color='k', s=3., label='Data points')
# plot circles with radius proportional to the outlier scores
radius = (coef- coef.min()) / (coef.max() - coef.min())
plt.scatter(X[:, 0], X[:, 1], s=1000 * radius, edgecolors='r',
            facecolors='none', label='Outlier scores')
plt.axis('tight')
plt.xlim((-5, 5))
plt.ylim((-5, 5))
#plt.xlabel("prediction errors:")
legend = plt.legend(loc='upper left')
legend.legendHandles[0]._sizes = [10]
legend.legendHandles[1]._sizes = [20]
plt.show()


#######
#### test with data set
#######
#data = load_data("ecoli-0-1-3-7_vs_2-6.dat")

data = load_data("shuttle-c0-vs-c4.dat")

'''
for i in range(2,10):
    if True in ldof(data[:,:-1],k=i):
        print("hola")
        print(i)
'''

