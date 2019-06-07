##
## Read in the input file including covariates. Then scale or otherwise proces
## the data such as by using seurat methods. In this current case, however, we
## will simply grab the "regressed" data from Ben and read it. Then we will dump out
## some statistices on the per-cell and per-gene normalizations

###########################################################################

## Basic input file format
## CELL SEX DATE NODEID MOUSE 0610007N19Rik ........

import pandas as pd
import numpy as np
import sys,ast
import matplotlib.pyplot as plt
import sklearn.preprocessing
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler

# Bens input data filename 
# /projects/sequence_analysis/vol1/prediction_work/CausalInference/CausalNetworking_forKirk/PCAProjectionImputationPipeline/MouseTumor_allMice_allGenes/mouse_allPhenotypes_regressed_data_allCells_Notscaled.tsv

##########################################################################

#def getKnownGroupEffects(fulldata):
#    """ Check the input file for KNOWN possible group effects
#    Exclude those that may not exist such as TREATMENT. Make no
#    assumptions about order or sorting. Return list in arbitrary 
#    order. Independent of list provided by the user
#    """
#    currentPossibleColumnEffects = ['TREATMENT','MOUSE','SEX','DATE','NODEID']
#    allColumns = fulldata.columns.values
#    # Grab only those fulldata columns that exist inb currentPossible
#    foundColumns = list(set(allColumns) & set(currentPossibleColumnEffects))
#    print('Number of groupeffect columns in data is '+str(foundColumns))
#    print('They are: '+str(foundColumns))
#    return (foundColumns)


def getKnownGroupEffects(fulldata,batchfilename):
    """ Check the input file for KNOWN possible group effects
    Exclude those that may not exist such as TREATMENT. Make no
    assumptions about order or sorting. Return list in arbitrary 
    order. Independent of list provided by the user
    """
    foundColumns = list()
    listOneHotEncoded = list()
    if (batchfilename == False):
        print('Using prechosen batch effect names')
        currentPossibleColumnEffects = ['TREATMENT','MOUSE','SEX','DATE','NODEID']
        allColumns = fulldata.columns.values
        listOneHotEncoded = ['MOUSE'] # By default for use with our data testing
        # Grab only those fulldata columns that exist inb currentPossible
        foundColumns = list(set(allColumns) & set(currentPossibleColumnEffects))
    else:
        foundColumnsCombined = list()
        with open(batchfilename) as f:
            tempColumns = f.read().splitlines()
            for effect in tempColumns:
                #foundColumnsCombined.append(effect.upper())
                foundColumnsCombined.append(effect)
            for ipair in foundColumnsCombined:
                #print('effect is '+ipair)
                name,typeEnc = ipair.strip().split(' ')
                foundColumns.append(name)
                if (typeEnc=='ONEHOT'):
                    listOneHotEncoded.append(name)
    print('Number of Possible batch effects found/specified is '+str(len(foundColumns)))
    print('Number of groupeffect columns in data is '+str(foundColumns))
    #print('They have been converted to UPPER CASE: '+str(foundColumns))
    return (foundColumns,listOneHotEncoded)

def scaleResults(df_R,batchfile,origScaling,logScaledResults,cellScale):
    """ For the impute R (which includes group effects) scale 
    data for read counts, and then studentize the features to N(0,1)
    (value+1)*mean-all-cell-read / call total read
    The post averaged cell totals is approx 2100 for a factor of 1
    """
    scaleBounds = pd.DataFrame()
    covs,oneHotTerms = getKnownGroupEffects(df_R,batchfile)
    print(str(df_R.columns))
    print(str(covs))

    df_R_X_i=df_R.drop(covs,axis=1,inplace=False)
    df_new_R = df_R[covs] # Hold back until the end
    df_R_X = df_R_X_i.astype(float) # Copy false or not doesn't update inplace
    #

    factor = 10000.0

    # First ave number of reads per cell (or do we want median values kirk think median?)
    total_reads = float(df_R_X.values.sum())
    num_reads = float(df_R_X.values.size)
    ave_total_reads = total_reads / num_reads
    # Alternative method use the median
    ## total_sum_c = pd.DataFrame(df_R.sum(axis=1))
    ## median_total_reads = total_sum_c.median()
    ##total_median_c = pd.DataFrame(df_R.median(axis=1)) # or do we want median values
    ##total_median_c.columns=['TOTALC']

    # Sometimes the data come in as ints
    print('convert data type to float: use a mean method:')
    ##total_median_c = pd.DataFrame(df_R_X.median(axis=1)) # or do we want median values
    total_mean_c = pd.DataFrame(df_R_X.mean(axis=1)) # or do we want median values
    ##total_median_c.columns=['TOTALC']
    total_mean_c.columns=['TOTALC']
    # Ave number of reads per cells divided by cell reads
    total_correction_factor = factor * ave_total_reads / total_mean_c['TOTALC']
    # total_correction_factor.set_index('CELL')
    if (cellScale):
        print('Initial Guess: Will also scale cel total counts')
    ## Now we must also dump cell scaling info to disk
    ## diab le scaling cells

    ###############################################
    # Dump total correction data for subsequent de-scaling
    df_correction = pd.DataFrame(total_correction_factor)
    df_correction.columns = ['TOTALCORRECTION']
    df_correction.index = df_R_X.index

    if (cellScale):
        print('Preprocess cell scaling')
        if (logScaledResults):
            print('c+1 log scaling of counts')
            df_scale_new = np.log2((df_R_X+1.0).mul(total_correction_factor,axis=0))
        else:
            df_scale_new = df_R_X.mul(total_correction_factor,axis=0) # Scale cells to have same total reads
    else:
        df_scale_new = df_R_X

    # Lastly scale the features 
    # Getting lost when axis=1 and axis=0. Setting zero here gets us COLUMN scaling
    # Compute Max and Min values then store to disk for inverse scaling of final result
    ################################################
    # Dump min/max or mean/std FEATURE attributes to disk for subsequent inverse scaling
    if (origScaling):
        scaleBounds = pd.merge(df_scale_new.mean().to_frame(),df_new_scale.std().to_frame(),left_index=True,right_index=True)
        scaleBounds.columns = ['MEAN','STD']
    else:
        scaleBounds = pd.merge(df_scale_new.min().to_frame(),df_scale_new.max().to_frame(),left_index=True,right_index=True)
        scaleBounds.columns = ['MIN','MAX']
    ################################################
    if (origScaling):
        df_new = pd.DataFrame(sklearn.preprocessing.scale(df_scale_new, with_mean=True, with_std=True, copy=True,axis=0).tolist())
    else:
        print('Guess scaling: MinMax')
        scaler = MinMaxScaler(feature_range=(0.0,1.0)) # Might also want 0.1,0.9 instead
        df_new = pd.DataFrame(scaler.fit_transform(df_scale_new))

    # Now scale the cells
    #
    df_new.index = df_R_X.index.values
    df_new.columns = df_R_X.columns.values
    #
    ## diab le scaling cells
    ##if (logScaledResults):
    ##    df_scale_new = np.log((df_new+1.0).mul(total_correction_factor,axis=0))
    ##else:
    ##    df_scale_new = df_new.mul(total_correction_factor,axis=0) # Scale cells to have same total reads
    #df_scale_new = df_new

    # Add effects back into the data object

    finalR = pd.merge(df_new_R,df_new,left_index=True,right_index=True)
    df_new_R = finalR
    print('Scale the guess function')
    print(str(df_new_R.shape))
    print('---------------')
    return(df_new_R,scaleBounds,df_correction)

###############################################################################
# Set some globals

# May want to skip the first OG after initial guess construction

performSubsequentOG = True
batchfile=False

# Start the class

class constructInitialGuess(object):

    def reportParameters(self):
        print('Infilename is '+self.inputfilename)
        print('Output metadata '+self.outputInitialGuessfilename)

    def __init__(self, rawinfilename, initialGuessoutputfilename,batchfile=False,origScaling=True,logScaledResults=False,cellScaledResults=False):
        self.inputfilename = rawinfilename 
        self.batchfile = batchfile
        self.outputInitialGuessfilename = initialGuessoutputfilename
        self.origScaling = origScaling
        self.logScaledResults = logScaledResults if logScaledResults==False else True
        self.scaleBounds = pd.DataFrame()
        self.cellScaledResults = cellScaledResults if cellScaledResults==False else True
        self.totalCorrection = pd.DataFrame()
        self.outputBoundsfilename = 'scaleBounds.tsv'
        self.outputTotalCorrection = 'totalCorrection.tsv'
        self.preregressedfilename = '/projects/sequence_analysis/vol1/prediction_work/CausalInference/CausalNetworking_forKirk/PCAProjectionImputationPipeline/MouseTumor_allMice_allGenes/mouse_allPhenotypes_regressed_data_allCells_Notscaled.tsv'
        self.init = pd.DataFrame()

    def setOrigScaling(self,inOrigScale):
        if (inOrigScale==True):
            self.origScaling = True
        else:
            self.origScaling = False

    def reportScaling(self):
        print('origScaling is '+str(self.origScaling))
        print('Log scaling ? '+str(self.logScaledResults))
        print('Cell scaling ? '+str(self.cellScaledResults))

    def fetchScaleBounds(self):
        """Returns a dataframe of either MIN/MAX or MEAN/STD of the prestandardized features
        """
        return (self.scaleBounds)

    def fetchTotalCorrection(self):
        return (self.totalCorrection)

    def fetchInitialGuessMatrix(self):
        return (self.init)

    def getOutputFilename(self):
        return self.outputInitialGuessfilename
    
    def getBoundsFilename(self):
        return self.outputBoundsfilename

    def getTotalCorrectionFilename(self):
        if (self.cellScaledResults):
            return self.outputTotalCorrection
        else:
            return 'empty'

    def fetchInitialGuess(self):
        """Simply return Ben's Seurat imputed data set
        But read the data, and rescale it to MinMax (0,1) and rename to initialGuess.tsv
        """
        inputList = self.inputfilename
        inputpreregressedList = self.preregressedfilename
        regressdata  = pd.read_table(inputpreregressedList,delim_whitespace=True, index_col=0,header=0,low_memory=False)
        df_R,self.scaleBounds,self.totalCorrection = scaleResults(regressdata,self.batchfile,self.origScaling,self.logScaledResults,self.cellScaledResults)
        df_R.to_csv(self.outputInitialGuessfilename,sep=' ')
        print('Select Bens Seurat data file: Writing scale bounds '+self.getBoundsFilename())
        self.scaleBounds.to_csv(self.getBoundsFilename(),sep=' ')
        if (self.cellScaledResults):
            self.totalCorrection.to_csv(self.getTotalCorrectionFilename(),sep=' ')
        self.init = df_R
        print('Completed initial FETCH guess')

    def runInitialGuess(self):
        """
        Take input Reads matrix and scale it to mean cel counts AND ~N(0,1). No logs applied
        """
        inputList = self.inputfilename
        inputpreregressedList = self.preregressedfilename
        rawdata = pd.read_table(inputList,delim_whitespace=True,index_col=0,header=0,low_memory=False)
        df_R,self.scaleBounds,self.totalCorrection = scaleResults(rawdata,self.batchfile,self.origScaling,self.logScaledResults,self.cellScaledResults)
        self.init = df_R
        print('Writing guess to filename '+self.outputInitialGuessfilename)
        df_R.to_csv(self.outputInitialGuessfilename,sep=' ') 
        print('Writing scale bounds '+self.getBoundsFilename())
        self.scaleBounds.to_csv(self.getBoundsFilename(),sep=' ')
        if (self.cellScaledResults):
            print('Writing totalCorrection '+self.getTotalCorrectionFilename())
            self.totalCorrection.to_csv(self.getTotalCorrectionFilename(),sep=' ')
        print('Completed initial COMPUTE guess')
