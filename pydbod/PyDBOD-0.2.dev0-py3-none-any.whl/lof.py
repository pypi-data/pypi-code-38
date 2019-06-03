# -*- coding: utf-8 -*-
"""
@author: Miguel Ángel López Robles
"""


import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import DistanceMetric
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor

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
    
# LOF function
def lof(data, k=20):

    nbrs = NearestNeighbors(n_neighbors=k, algorithm='ball_tree').fit(data)
    distances, indices = nbrs.kneighbors(data)

    
    n_points = distances.shape[0]
    reach_d = [ [ max( (distances[i, j], distances[indices[i,j],k-1] ) ) for j in range(k) ] for i in range(n_points) ]
    reach_d = np.array(reach_d)

    ave_reach_d = np.mean(reach_d,axis=1)
    
    meany = 1 / np.array( [ [ ave_reach_d[i] for i in indices[j]] for j in range(n_points)] )
    meany = np.mean(meany,axis=1)
    #print("Mean y in Lx")
    #print(meany)

    lof = ave_reach_d * meany
    #print("lof")
    #print(lof)

    return lof

'''
X = np.array([[-1, -1,-2], [-2, -1,-2], [-3, -2, -2], [1, 1, -2], [2, 1, -2], [3, 2,-2]])
nbrs = NearestNeighbors(n_neighbors=3, algorithm='ball_tree').fit(X)
distances, indices = nbrs.kneighbors(X)

print(X)
print(distances)
print(indices)
lof(X,3)
#dist = DistanceMetric.get_metric('euclidean')
#result = dist.pairwise(X)
#print(result)
'''
###############################
## load a file

#data = load_data("shuttle-c0-vs-c4.dat")
#data = load_data("glass5.dat", sep = ', ')
#data = load_data("ecoli-0-1-3-7_vs_2-6.dat")
data = load_data("yeast5.dat", sep = ', ')
##############################################
# take coef and see it
coef = lof(data[:,:-1], 35)
np.set_printoptions(threshold=np.inf)
print(coef)

print("coeficient > 2")
print(len(coef[coef>2]))

print("Positive examples")
print( len ( data[data[:,-1] == 1] ))
#print(coe[180])
#print(coe[190:200])


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
'''
# fit the model for outlier detection (default)
clf = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
# use fit_predict to compute the predicted labels of the training samples
# (when LOF is used for outlier detection, the estimator has no predict,
# decision_function and score_samples methods).
y_pred = clf.fit_predict(X)
print("predict")
print(y_pred)
n_errors = (y_pred != ground_truth).sum()
X_scores = clf.negative_outlier_factor_
print(clf.threshold_)
print(X_scores)
'''

# use my function
coef = lof(X,20)
print(coef)

my_pred = coef > 1.4 
print(my_pred)
'''
probedata = clf.fit_predict(data)
print(clf.threshold_)
'''

plt.title("Local Outlier Factor (LOF)")
plt.scatter(X[:, 0], X[:, 1], color='k', s=3., label='Data points')
# plot circles with radius proportional to the outlier scores
radius = (coef - coef.min()) / (coef.max() - coef.min())
plt.scatter(X[:, 0], X[:, 1], s=1000 * radius, edgecolors='r',
            facecolors='none', label='Outlier scores')
plt.axis('tight')
plt.xlim((-5, 5))
plt.ylim((-5, 5))
#plt.xlabel("prediction errors: %d" % (n_errors))
legend = plt.legend(loc='upper left')
legend.legendHandles[0]._sizes = [10]
legend.legendHandles[1]._sizes = [20]
plt.show()