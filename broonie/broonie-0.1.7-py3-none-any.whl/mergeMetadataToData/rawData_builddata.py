#################################################################
##
## These are the construction of the data from Ben using Zscores.
## So we do not filter by zeros. but we continue to use MAD() thresholding

## BUILD a new datafrae as follows. Columns CELLS MOUSE SEX DATE VEHICLE gene1 gene2 ....genep
## The gene values should be PRESCALED but not whitened. We can do thatlater
## The MOUSE value can be constructed from the CELL name

# MetaDataWithDate
##"nGene" "nUMI"  "Replicate"     "Treatment"     "Sex"   "Date"  "ID"

## 
## also The true Raw data has more cells than Ben's scaled data 
## SO we read in His f*ing daa here to provide a filter. (Damn guys !)

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

rootdir = '/projects/sequence_analysis/vol1/prediction_work/CausalInference/CausalNetworking_forKirk/'
rawfilename = rootdir+'rawResults/RawDataMatrix.txt'
metafilenameDate = rootdir+'rawResults/MetaDataMatrixWithDate.txt'

# Bens raw data 

benrootdir = '/projects/sequence_analysis/vol1/prediction_work/CausalInference/CausalNetworking_forKirk/'
benregressedfilename = rootdir+'regressedResults/ScaleDataMatrix.tsv'

t0=tm.time()
data = pd.read_csv(rawfilename,delim_whitespace=True)
print(tm.time()-t0)

regdata = pd.read_csv(benregressedfilename,delim_whitespace=True)

## Now exclude cells that ben excluded

listrawcolumns = data.columns.values
listregresscolumns = regdata.columns.values
listdiff = list(set(listrawcolumns)-set(listregresscolumns))

data.drop(listdiff,axis=1,inplace=True)

##
## Some basic plots of the raw Zscore imputed data
##

datameans = pd.DataFrame(data.mean(axis=1))
datameans.reset_index(inplace=True)
datameans.columns=['GENE','MEANS']
#datameans.plot(kind='line',x='GENE',y='MEANS',label='Zscore imputed data: Column MEANS of raw scRNAseq data')
#datameans.xlabel=('Gene')
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
#datacellmeans.plot(kind='line',x='CELL',y='CELLMEANS',label='Column MEANS of Zscore imputed scRNAseq data')
#datacellmeans.xlabel=('Cell')
#datacellmeans.ylabel=('CellMean')
#plt.savefig('imputedData_CellMeanCounts.pdf')
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
## CHeck the profile to see how many to keep

datamad = pd.DataFrame(data.mad(axis=1))
datamad.reset_index(inplace=True)
datamad.columns=['GENE','MAD']
datamad.sort_values(by='MAD',ascending=False,axis=0,inplace=True)
#datamad.plot(kind='line',x='GENE',y='MAD',label='Kirk: Imputed data: MAD() of imputed scRNAseq data')
#plt.ylabel=('MAD')
#plt.savefig('imputedData_GeneMADCounts.pdf')
#plt.show()

## Sort data set  and include only the4 Top 5000 MAD values
topGenes = datamad.head(5000)
topGenesList = topGenes['GENE'].tolist()
pd.DataFrame(topGenesList).to_csv('topGenes_MAD.tsv')

# Kirk wants to keep all genes for now

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

#fulllistNames = list(data.loc[topGenesList].columns.values)
fulllistNames = list(data.columns.values)
unique_tumors = set([ x.split('_')[0] for x in fulllistNames ])
#{'MB10', 'MB13', 'MB05', 'MB14', 'MB06', 'MB04', 'MB15', 'MB07', 'MB12', 'MB09'}
allentries_tumors_temp = list([ x.split('_')[0] for x in fulllistNames ])
from collections import Counter
counter = collections.Counter(allentries_tumors_temp)

## 1) Get some base data: Compute total ave read count from the Raw data
## just for comparisons
## We assume missingness is not to0 bad. But it seems we should QC the raw data 
## to get the following values  (?)

## skip the scaling of the reads

#data_new = data.loc[topGenesList]
data_new = data

# Confirm total reads per cell are the same
cellsums = data_new.sum(axis=0)

# What about total reads per gene
genesums = data_new.sum(axis=1)
#genesums.hist(bins=20,range=[0,100000])
#plt.savefig('imputedData_GeneSums_postScale.pdf')
#plt.show()

###############################################################################3
# No exclusons based on zeros

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

############################################################################################
# cell reads for all mice have now been QC'd and scaled. We start filtering away non-vehicle, non-tumor data
# Then build data into the dataframe to apture some batch effects such as Date and Sex

## First Remove all CELLs that are not actually part of a Tumor using the MAP from Kirk
## /proj/kirklab/users/KirkFiles/
## We also only want VEHICLE cells

### This whoe procedure has changed AGAIN

# NODENAMES THAT ARE NOT TUMORS: Remaining terms have the nomenclaturee NODE A, NODE B, etc
# Dec 12. Per kirk. Keep al cell types but exclude the vismodigib mice: onlty keep vehicle

#############################################################################################
# PLACE A DUMMY TERM INTO NOTTUMORS AND RERUN

#notTumors =['Endothelial Cells','Vascular Fibroblasts','Astrocytes','Endothelial','Microglia','Neurons','Oligodendrocytes','Vascular']
notTumors =['TEST']
metadata = pd.read_csv(metafilenameDate,delim_whitespace=True)

# Get list of cells that are NOT tumors
listNotTumorCells_df = metadata.ix[((metadata['ID'].isin(notTumors)))]
listNotTumorCells = list(listNotTumorCells_df.index.values)

#############################################################################################
## Now get list of cells. Keep all of 'em

listNotVehicleCells_df = metadata.ix[ metadata['Treatment'] == 'DUMMY']
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
# Keep only the top5000
# temp = data_new_tumor.T[topGenesList].copy()
# data_new_tumor = temp.T
 
# NO SCALING

data_new_tumor_scaled_T = data_new_tumor.T
data_new_tumor_scaled_T['CELL'] = cellNamesList
data_new_tumor_scaled_T.set_index('CELL',inplace=True)
data_new_tumor_scaled_T.columns = geneNamesList_cell

# Add metadata to the scaled data object (SEX,DATE,MOUSE)

scaledData = data_new_tumor_scaled_T.copy()
newcolumn = metadata.loc[scaledData.index.values][['Treatment','Sex','Date','ID']]

##
## Splitting on spaces wil cause problems. Simply remove spaces and let downstream live with it
##newcolumn.ID = newcolumn.ID.str.split(' ').str.get(1)
newcolumn.ID = [x.replace(' ','') for x in list(newcolumn.ID)]

# Now let's build a column that only has a mouse ID. We can convert to multiple rows of 
# indicator variables at some later time

mouseIndex = [ int(x.split('_')[0][2:]) for x in newcolumn.index ]
newcolumn['MOUSE']=mouseIndex

# Build final dataframe for disk storage
combinedScaledData = pd.merge(newcolumn,scaledData,left_index=True,right_index=True)
combinedScaledData.rename(columns={'Treatment':'TREATMENT','Sex':'SEX','Date':'DATE','ID':'NODEID'},inplace=True)

outfilename = 'mouse_raw_data_allcells_Notscaled.tsv'
combinedScaledData.to_csv(outfilename,header=True,sep=" ",index=True)

print('raw data processing completed')

