#
# Construct the data sets given the sizes n,p,k,and w
#
import pandas as pd
import time as tm
from construct_simulated_dataset import SimulatedDataSet

metadata = 'simulatedNew'
n=5000
p=1000
k=10
w=1

simdat = SimulatedDataSet(metadata,n,p,k,w)
simdat.constructDataObjects()
simdat.outputSimulationParams()
simdat.writeObjectsToDisk()

