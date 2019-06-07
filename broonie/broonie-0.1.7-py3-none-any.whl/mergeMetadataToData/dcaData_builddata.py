WARNING
COmpare  replace metadata code with that found in the regressed version
#################################################################
##
## Kirk has a different way to treat the filtering of the data.
## 1) For the Raw data  compute the TOTAL RAW mean counts as
## total_c sum(READS_C,G)
## avg_reads = SUM(total_c)/N
## 
## 2) For the Imputed data from Filer
## total_imp_c = SUM(READS_c,g)
## New_impute_cg = ( 10.0 * avg_reads * READS_c,g ) / total_imp_c
##
## See book causal networks. pg 27
##
## 3) Remove genes with fewer than 5908 cells with scaled reads < 1
## 4) Remove those cells that were not tumor cells

##
## BUILD a new datafrae as follows. Columns CELLS MOUSE SEX DATE VEHICLE gene1 gene2 ....genep
## The gene values should be PRESCALED but not whitened. We can do thatlater
## The MOUSE value can be constructed form the CELL name

# Orig MetaData
##"Sex"   "Treatment"     "TenPC.hvg.ident"       "Node"

# MetaDataWithDate
##"nGene" "nUMI"  "Replicate"     "Treatment"     "Sex"   "Date"  "ID"

## So we have initially 16,600 Genes and 29,538 SingleCells
##
##################################################################

import time as tm
import pandas as pd
import numpy as np
import collections
import matplotlib.pyplot as plt
import math 
import scipy 
from scipy import stats
import sys
import sklearn.preprocessing

import sys

from numpy.random import seed
from numpy.random import randn
from statsmodels.graphics.gofplots import qqplot
import pylab
import scipy.stats as stats
from scipy import linalg


#from __future__ import print_function

#########################################################################

# Change these to suit
# Not all these files are always used

# Input range of cell types classified as TUMORS to INCLUDE
if len(sys.argv) >2:
    lowValue = int(sys.argv[1])
    highValue = int(sys.argv[2])
elif (len(sys.argv) == 2):
    lowValue = int(sys.argv[1])
    highValue = int(sys.argv[1])
else:
    lowValue = 1
    highValue = 10

print("Range of cells to keep is "+str(lowValue)+' to '+str(highValue))
if (highValue > 10):
    print("High Value may be too high should be 10 or less "+str(highValue))

if (lowValue < 1):
    print("Low Value may be too low should be 1 or greater "+str(lowValue))

rootdir = '/projects/sequence_analysis/vol1/prediction_work/CausalInference/CausalNetworking_forKirk/'
rawfilename = rootdir+'rawResults/RawDataMatrix.txt'
metafilenameDate = rootdir+'rawResults/MetaDataMatrixWithDate.txt'

filename = rootdir+'dcaResults/mean.tsv'

t0=tm.time()
rawdata = pd.read_csv(rawfilename,delim_whitespace=True)
data = pd.read_csv(filename,delim_whitespace=True)
print(tm.time()-t0)

##
## Some basic plots of Dayne's imputed data
##

datameans = pd.DataFrame(data.mean(axis=1))
datameans.reset_index(inplace=True)
datameans.columns=['GENE','MEANS']
#datameans.plot(kind='line',x='GENE',y='MEANS',label='Kirk: Imputed data: Column MEANS of imputed scRNAseq data')
#$datameans.xlabel=('Gene')
#plt.ylabel=('Mean')
#plt.savefig('imputedData_GeneMeanCounts.pdf')
#plt.show()

##
## How about the cell mean reads?
##

datacellmeans = pd.DataFrame(data.mean())
datacellmeans.reset_index(inplace=True)
datacellmeans.columns=['CELL','CELLMEANS']
datacellmeans.sort_values(by=['CELL'],inplace=True)
#datacellmeans.plot(kind='line',x='CELL',y='CELLMEANS',label='Column MEANS of imputed scRNAseq data')
#datacellmeans.xlabel=('Cell')
#datacellmeans.ylabel=('CellMean')
#plt.savefig('rawData_CellMeanCounts.pdf')
#plt.show()

######################################################################
## Compute gene MAD() values then keep 5000 top

datamad = pd.DataFrame(data.mad(axis=1))
datamad.reset_index(inplace=True)
datamad.columns=['GENE','MAD']
#datamad.plot(kind='line',x='GENE',y='MAD',label='Kirk: Imputed data: MAD() of imputed scRNAseq data')
#plt.ylabel=('Mean')
#plt.savefig('imputedData_GeneMeanCounts.pdf')
#plt.show()

## Sort data set  and include only the4 Top 5000 MAD values
datamad.sort_values(by='MAD',ascending=False,axis=0,inplace=True)
topGenes = datamad.head(5000)
topGenesList = topGenes['GENE'].tolist()
data.loc[topGenesList]

######################################################################
## Get list of TUMOR names for future use and proportions
## Filter-keep only Vehicle cells

def tumor_within_cellName(tumorname,cellname):
    return tumorname in cellname

def computeSizeFactor_cellname(cellname, counterObject):
    name = cellname.split('_')[0]
    numbcells = float(counterObject[name])
    total = float(sum(counterObject.values()))
    return numbcells/total

fulllistNames = list(data.loc[topGenesList].columns.values)
unique_tumors = set([ x.split('_')[0] for x in fulllistNames ])
#{'MB10', 'MB13', 'MB05', 'MB14', 'MB06', 'MB04', 'MB15', 'MB07', 'MB12', 'MB09'}
allentries_tumors_temp = list([ x.split('_')[0] for x in fulllistNames ])
from collections import Counter
counter = collections.Counter(allentries_tumors_temp)

## 1) Get some base data: Compute total ave read count from the Raw data
## just for comparisons
## We assume missingness is not to0 bad. But it seems we should QC the raw data 
## to get the following values  (?)

total_reads = float(rawdata.values.sum())
num_reads = float(rawdata.values.size)
ave_total_reads = total_reads / num_reads

##
## 2) Scale the reads of the imputed data set
## 

total_impute_c = pd.DataFrame(data.loc[topGenesList].mean(axis=0))
total_impute_c.columns=['TOTALC']

# Compute a Series: New_Impute_cg = impute_cg * (10*ave_total_reads) / total_imput_c
#cellmeans = pd.DataFrame(df_R.mean(axis=1) These all sum(genes) to a value of about 21019 per cell

total_correction_factor = 10.0 * ave_total_reads / total_impute_c['TOTALC']
data_new = data.loc[topGenesList].mul(total_correction_factor,axis=1)

# Confirm total reads per cell are the same
cellsums = data_new.sum(axis=0) # Values of 21019

# What about total reads per gene
genesums = data_new.sum(axis=1)
#genesums.hist(bins=20,range=[0,100000])
#plt.savefig('imputedData_GeneSums_postScale.pdf')
#plt.show()

###############################################################################3
## We want to remove genes that have fewer than 100 cells that are non-zero
## But what constitutes non-zero is somewhat arbitrary. We assume in the unscaled imputed 
## data that approx <= 10-3 is zero. However kirk think we should choose >= 1 as the scaled criteria 

# Keep only those that are nominal zeros (<1)
# Then do the counting. Any with more than 29538 - 100 = 29438 gets eliminated

x = data_new[ data_new < 1 ]
counts_thresh = x.count(axis=1).to_frame()     

cells_20percent =  data.shape[1] - int(0.20 *data.shape[1])

removeBoolean = counts_thresh[ counts_thresh > cells_20percent ] # approx 20%
removeBoolean.dropna(inplace=True)
listToRemove = removeBoolean.index.values
data_new.drop(listToRemove,inplace=True)

## Post QC Plot information
# Per gene
datameans = pd.DataFrame(data_new.mean(axis=1))
datameans.reset_index(inplace=True)
datameans.columns=['GENE','VARIANCE']
#datameans.plot(kind='line',x='GENE',y='VARIANCE',label='Imputed data: Column Scaled-MEANS of imputed scRNAseq data')
#datameans.xlabel=('Gene')
#datameans.ylabel=('Scaled-MEANS')
#plt.savefig('imputedData_GeneMeanCounts_removeMissingness.pdf')
#plt.show()

# Per Cell
datacellmeans = pd.DataFrame(data_new.mean())
datacellmeans.reset_index(inplace=True)
datacellmeans.columns=['CELL','CELLMEANS']
datacellmeans.sort_values(by=['CELL'],inplace=True)
#datacellmeans.plot(kind='line',x='CELL',y='CELLMEANS',label='Column MEANS of imputed scRNAseq data')
#datacellmeans.xlabel=('Cell')
#datacellmeans.ylabel=('CellMean')
#plt.savefig('rawData_CellMeanCounts_removeMissingness.pdf')
#plt.show()

## Gene must be > 0 for more than 100 cell2. Where zero is defined by
## scaledzero = 10-3 * (10*ave_total_reads) / total_imput_c

############################################################################################
# cell reads for al lmice have now been QC'd and scaled. We start filtering away non-vehicle, non-tumor data
# Then build data into the dataframe to apture some batch effects such as Date and Sex

## First Remove all CELLs that are not actually part of a Tumor using the MAP from Kirk
## /proj/kirklab/users/KirkFiles/
## We also only want VEHICLE cells

# NODENAMES THAT ARE NOT TUMORS: Remaining terms have the nomenclaturee NODE A, NODE B, etc
notTumors =['VascularFibroblasts','Astrocytes','Endothelial','Microglia','Neurons','Oligodendrocytes','Vascular']

metadata = pd.read_csv(metafilenameDate,delim_whitespace=True)

# Get list of cells that are NOT tumors
listNotTumorCells_df = metadata.ix[((metadata['ID'].isin(notTumors)))]
listNotTumorCells = list(listNotTumorCells_df.index.values)

## Now get list of cells from metadatawithdate that are NOT Vehicle for exclusion
listNotVehicleCells_df = metadata.ix[ metadata['Treatment'] != 'Vehicle']
listNotVehicleCdells = list(listNotVehicleCells_df.index.values)

# Union unique of exclude lists
excludeList = set(listNotTumorCells+listNotVehicleCdells)
data_new_tumor = data_new.copy()
data_new_tumor.drop(excludeList,axis=1,inplace=True)

cellNames = data_new_tumor.iloc[1].to_frame()
cellNamesList = cellNames.index.tolist()
geneNames = data_new_tumor.iloc[:,1].to_frame()
geneNamesList = geneNames.index.tolist()
geneNamesList_cell = geneNamesList

# get data from numpy and convert to df

data_new_tumor_scaled_T = pd.DataFrame(sklearn.preprocessing.scale(data_new_tumor.T, with_mean=True, with_std=True, copy=True).tolist())
data_new_tumor_scaled_T['CELL'] = cellNamesList
data_new_tumor_scaled_T.set_index('CELL',inplace=True)
data_new_tumor_scaled_T.columns = geneNamesList_cell

# Add metadata to the scaled data object (SEX,DATE,MOUSE)

scaledData = data_new_tumor_scaled_T.copy()
newcolumn = metadatadate.loc[scaledData.index.values][['Sex','Date','ID']]
##newcolumn.ID = newcolumn.ID.str.split(' ').str.get(1)
newcolumn.ID = [x.replace(' ','') for x in list(newcolumn.ID)]

# Now let's build a column that only has a mouse ID. We can convert to multiple rows of 
# indicator variables at some later time

mouseIndex = [ int(x.split('_')[0][2:]) for x in newcolumn.index ]
newcolumn['MOUSE']=mouseIndex

# Build final dataframe for disk storage
combinedScaledData = pd.merge(newcolumn,scaledData,left_index=True,right_index=True)
combinedScaledData.rename(columns={'Sex':'SEX','Date':'DATE','ID':'NODEID'},inplace=True)

outfilename = 'mouse_data_vehicle_tumor_scaled.tsv'
combinedScaledData.to_csv(outfilename,header=True,sep=" ",index=True)
################################################################
# might as well build the whitened data set too

X = data_new_tumor_scaled_T.values
Carray = data_new_tumor_scaled_T.cov().values
D,V = linalg.eigh(Carray)
indices = D.argsort()[::-1]
D,V = D[indices], V[:,indices]
Dhalf = np.sqrt(D)
DhalfInv = 1.0/Dhalf
DmatrixHalfInv = np.diag(DhalfInv)
CarrayInvHalf = V @ DmatrixHalfInv @ V.T
whiteX3 =  X @ CarrayInvHalf
newCovar = np.cov(whiteX3,rowvar=False)

##
## Must create a new DataFrame by hand
##
newDF = pd.DataFrame(whiteX3)
newDF.columns = geneNamesList
newDF['CELL']=data_new_tumor_scaled_T.index.values
newDF.set_index('CELL',inplace=True)

##
## Now add the metadata again
##
# Add metadata to the scaled data object (SEX,DATE,MOUSE)

newcolumn = metadatadate.loc[newDF.index.values][['Sex','Date','ID']]
# Fix the seemingly stupid choice for Node ID values
##newcolumn.ID = newcolumn.ID.str.split(' ').str.get(1)
newcolumn.ID = [x.replace(' ','') for x in list(newcolumn.ID)]

# Now let's build a column that only has a mouse ID. We can convert to multiple rows of 
# indicator variables at some later time

mouseIndex = [ int(x.split('_')[0][2:]) for x in newcolumn.index ]
newcolumn['MOUSE']=mouseIndex

# Build final dataframe for disk storage
combinedWhiteData = pd.merge(newcolumn,newDF,left_index=True,right_index=True)
combinedWhiteData.rename(columns={'Sex':'SEX','Date':'DATE','ID':'NODEID'},inplace=True)

outfilename = 'mouse_data_vehicle_tumor_scaled_whitened.tsv'
combinedWhiteData.to_csv(outfilename,header=True,sep=" ",index=True)

