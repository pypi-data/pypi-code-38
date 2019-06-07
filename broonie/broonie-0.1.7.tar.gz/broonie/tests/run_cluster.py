#
# Construct the data sets given the sizes n,p,k,and w
#
import time as tm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from broonie.generate_neighbor_matrix import generateNeighborMatrixClass
from sklearn.externals.joblib import Parallel, delayed



#############################################################################
# inputfilename='60_MOUSEDATESEXTREATMENT_Xtilde_ZscoreOrder.tsv'
# No group effects are included in this file
# To get the parallelism working launch as a slurm job with 16 cores per node, and 1 node
# ask for 16 GB per core

knn = 10
njobs = 16
xfilename = './DATA/outputXtilde_0_60_Xtilde_ZscoreOrder.tsv'
inputXfilename = xfilename
outputIndices = 'dfIndices-test.tsv'
outputDistances = 'dfDistances-test.tsv'
print('Run clustering ' + inputXfilename)
y = generateNeighborMatrixClass(knn,inputXfilename,outputIndices,outputDistances,njobs)
y.reportParameters()
y.runProcess()
y.writeClusterInformation() # Write out the K and distance matrices
yindexfilename = y.getIndexFilename()
ydistancefilename = y.getDistanceFilename()

#################################### Third run the regression
print('clustering complete')

