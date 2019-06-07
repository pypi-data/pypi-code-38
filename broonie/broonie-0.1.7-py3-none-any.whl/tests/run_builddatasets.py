#
# Construct the data sets given the sizes n,p,k,and w
#
import pandas as pd
import time as tm
from broonie.generate_neighbor_matrix import generateNeighborMatrixClass
from broonie.construct_simulated_dataset import construct_simulated_dataset

metadata = 'SinglevectorsimulatedNew'
n=5000
p=200
k=10
w=2

simdat = construct_simulated_dataset(metadata,n,p,k,w)
simdat.constructDataObjects()
simdat.outputSimulationParams()
simdat.writeObjectsToDisk()

