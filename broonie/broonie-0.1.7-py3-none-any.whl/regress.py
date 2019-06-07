# Feb 15. Change OLS to a weighted LS.
import time as tm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import scipy
from scipy import stats
import sys
import sklearn.preprocessing
from sklearn.preprocessing import MinMaxScaler
from scipy import stats
import scipy.stats as stats
from scipy.optimize import nnls
from scipy import linalg
from sklearn.linear_model import LinearRegression
from sklearn.externals.joblib import Parallel, delayed
#################################################################
#
# The R matrix on INPUT is expected to contain the covariates as well.
# The R matrix is usually wither the original RAW R data OR the df_new_R
# data object form running this Class a prior iteration. The best choice is TBD
# Then the final imputted R wil contain the same covariates
# The format of the NN matrices from the preceding Clustering class is
# CELL NN1 NN2 .... NNk+1
# The values can either be the indexing OR the distances depending on the file you are reading 
# Feb 15. Change OLS to a weighted LS.
# NOTE: WLS yield BLUE if weights are inverse variances

# CHECK if the reshape(-1,numGenes is correct)

# TODO read batchfilename as an option for covariate correction

# Might consider usingh KNeighborsRegressor directly !
import time as tm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math 
import scipy 
from scipy import stats
import sys
import sklearn.preprocessing
from sklearn.preprocessing import MinMaxScaler
from scipy import stats
import scipy.stats as stats
from scipy import linalg
from sklearn.linear_model import LinearRegression
from sklearn.externals.joblib import Parallel, delayed

#########################################################################
# Keep the known covariates of input R

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

def buildCellIndexMap(NNindex):
    """Build a dataframe with integer IDs as index and cell names as values
    One would prefer to have grabbed the IDs from the indices file but NOT!
    """
    cellNames=NNindex.index.values
    #cellIDs=NNindex['CELLTARGET'].values
    # Because of NN behavior this previous step doesn't always work
    # SO just give them integer values assuming input order is retained
    dataMap = pd.DataFrame(cellNames)
    ##dataMap.index = cellIDs
    dataMap.columns=['CELL']
    return (dataMap)

def aggregateNNLS(Xdata,Ydata):
    """Must loop over all features for the given icell
    """
    numObservations = Ydata.shape[1]
    w = np.zeros(numObservations)
    rnorm = np.zeros(numObservations)
    for i in range(0,numObservations):
        Y = Ydata[:,i]
        wtemp,rnormtemp = nnls(Xdata.reshape(-1,1),Y.flatten())
        w[i]=wtemp
        rnorm[i]=rnormtemp
    return(w,rnorm)

def singleNNLS(Y,X):
    """Must loop over all features for the given icell
    """
    print(str(Y))
    w,rnorm = nnls(X.reshape(-1,1),Y)
    return w


########################################################
class regressDataClass(object):
    """Using Regression,predict EVERY cell read from the input (unscaled) reads
    using the top k nearest neighbors are identified in the input INDICES object.
    For the regression we INCLUDE the target cell meaning that we actually regress k+1 terms
    On return is an unscaled new R matrix (nxp) and includes all the covariates and S which is a 
    scaled version of R.
    R is returns as reads with per-cell counts normalized
    S is returned with per-cell counts normalized, features scaled to N(0,1). and then log(read+1)

    Attributes
    ----------
    self.kNN = Sp[ecify number of nearest neighbors (Excluding self term) ( so k not k+1)
            I.e., same value as passed to the generateCluster methods
    self.batchfilename (opt) file that contains n rows and 2 column withs relevant batch effect names
            col 1 effect name: col two either ONEHOT or CAT for type of inclusion. Same file as used for project
    self.rawfilename. The input read data from which regression will proceeed. Values must be >=0 as the total 
            cell counts is determined from the file ands used for X in the OLS
    self.xtildeNeighborIndicesFilename. Input neighbor matrix (n by k+1)
    self.xtildeNeighborIndicesFilename. Input neighbor distance matrix (n by k+1) (not used at this time)
    self.outputRfilename. Output imputed R matrix
    self.outputSfilename. Output scaled version of imputed R
    self.origScaling = True feature scale as mean-centered, std=1 else MinMax (0,1)
    self.logScaledResults True perform log(R+1) transform on the data
    """

    def __init__(self, kNN, inrawfilename, indexfilename, distancefilename, outputRfilename, outputSfilename, batchfilename=False, origScaling=True, cellScaledResults=False, logScaledResults=False, keepEffects=True, origRegress=False):
        self.kNN = kNN
        self.rawfilename = inrawfilename
        self.xtildeNeighborIndicesFilename = indexfilename
        self.xtildeNeighborDistancesFilename = distancefilename
        self.df_new_R = pd.DataFrame()
        self.df_new_S = pd.DataFrame()
        self.df_Rraw = pd.DataFrame()
        self.df_Regress_Pvalues = pd.DataFrame()
        self.outputRfilename = outputRfilename
        self.outputSfilename = outputSfilename
        self.batchfilename = batchfilename
        self.origScaling = origScaling if origScaling==False else True
        self.cellScaledResults = cellScaledResults if cellScaledResults==False else True
        self.logScaledResults = logScaledResults if logScaledResults==False else True
        self.keepEffects = keepEffects 
        self.origRegress = origRegress if origRegress==True else False

    def setOrigScaling(self,inOrigScale):
        self.origScaling = inOrigScale if inOrigScale==False else True

    def reportScaling(self):
        print('Scaling Original type is '+str(self.origScaling))
        print('LogScaledResults is '+str(self.logScaledResults))

    def getRmatrix(self):
        return (self.df_new_R)

    def getSmatrix(self):
        return (self.df_new_S)

    def reportParameters(self):
        print('Regress Data set')
        print('Input reads matrix '+self.rawfilename)
        print('Type of impute regression to use: origVersion ? :'+str(self.origRegress))
        print('Input Indices '+self.xtildeNeighborIndicesFilename)
        print('Input distances '+self.xtildeNeighborDistancesFilename)
        print('Output R filename '+self.outputRfilename)
        print('Output S filename '+self.outputSfilename)
     
    def regressCellValues(self, df_R, NNindex, cellIndexMap, datacelltotals):
        debug = False
        wlsStyleRegression=True
        #
        if (wlsStyleRegression):
            print('Perform regression with sample weighting and zero-zero point registration')
        timein = tm.time()
        RT = pd.DataFrame()  # TRansposed to allow efficient per-cell updates to be columns
        RTPvalues = pd.DataFrame() # Carry down P-values for double checking        
        icountCells=0
        numGenes = df_R.shape[1]
        #print('Truncated REGRESS list for testing')
        additionalMultiplier = 10.0 # 10*current max weight: Kirk wanted an additional weight applied to zero point
        numNNs = NNindex.shape[1] # NOTE this INCLUDES the target cell
        for icell in df_R.index.values:
            #print('icel is '+icell)
            NNlist = NNindex.loc[icell].tolist()[0:] # return integer IDs: Also keep the first entry which is redundant to cell name
            NNlistNames = cellIndexMap.loc[NNlist].values.flatten() # Cells for performing regressin
            if (len(NNlist) != len(NNlistNames)):
                print('mismatch: NNlist and NNListNames')
                print('cell maps')
                print(str(cellIndexMap))
                cellIndexMap.to_csv('cellMapIndex.tsv')
                print('detailed output')
                for ival in NNlist:
                    print('ival '+str(ival))
                    print('cell val '+str(cellIndexMap.loc[ival])+'XXX')
            NNlistReadData = df_R.loc[NNlistNames] # Get the actual current reads
            icellTotal = datacelltotals.loc[icell].values # For predicting new R for the target cell/gene pair
            Xdata = datacelltotals.loc[NNlistNames].values.flatten()
            Ydata = NNlistReadData.values
            newGeneValues = list()
            model = LinearRegression(n_jobs=8)
            icellTotal = datacelltotals.loc[icell].values
            if (wlsStyleRegression):
                Xdata = np.insert(Xdata, 0, 0.0)
                Yzeros = np.zeros(shape=(numGenes,1))  # Introduce a "fake" cell with total=0 and read=0 for each gene
                Ydata = np.insert(Ydata, 0, Yzeros.reshape(1,-1),axis=0) 
                sample_weights = [np.sqrt(x) for x in Xdata]  # Large valued Xs have better Ys
                sample_weights[0] = additionalMultiplier * np.max(sample_weights)
                model.fit(Xdata.reshape(-1,1), Ydata, sample_weights) 
            else:
                Xdata = np.insert(Xdata, 0, 0.0)
                Yzeros = np.zeros(shape=(numGenes,1)) 
                Ydata = np.insert(Ydata, 0, Yzeros.reshape(1,-1),axis=0)
                model.fit(Xdata.reshape(-1,1), Ydata)
            #
            # Could predict all K+1 cells at ones and update the input R matrix
            # What if any of the reads are negative ?
            YdataPredict = model.predict(icellTotal.reshape(-1,1)) # Expect only one column of data
            #print('predict '+str(YdataPredict))
            ydatamin = YdataPredict.min()
            if (ydatamin < 0.0):
                print('Negative fit new WLS with new weights found for '+str(YdataPredict.shape))
                zeroout_indices = np.argwhere(YdataPredict < 0.0)
                YdataPredict[ YdataPredict < 0.0] = 0.0
                #YdataPredict[zeroout_indices]=0.0
                #print(str(zeroout_indices))
                print('applied a builtin floor to cell fit '+str(zeroout_indices.shape)+' '+str(icell))
            # Some values can be < 0 probably because the cluster neighbors are poorly chosen
            # Should we set a floor of zero?
            RT[icell]=YdataPredict.flatten()
            RT.index = df_R.columns.values
        print('completed regressions '+str(tm.time()-timein))
        return (RT.T)

# NOTE NNLS is NOT parallel 
# ALSO NNLS cannot automatically handle regressing one X column onto many Y observations
# So to get this to work we must write our own parallel code to process all obs for a given cell total

    def regressCellValuesNNLS(self, df_R, NNindex, cellIndexMap, datacelltotals):
        """Here we DO NOT weight the regression terms. We DO NOT add the (0,0) point.
        We simply run the NNLS using defauilt minimization parameters
        """
        debug = False
        #
        timein = tm.time()
        RT = pd.DataFrame()  # Transposed to allow efficient per-cell updates to be columns
        RTPvalues = pd.DataFrame() # Carry down P-values for double checking        
        icountCells=0
        numGenes = df_R.shape[1]
        #print('Truncated REGRESS list for testing')
        numNNs = NNindex.shape[1] # NOTE this INCLUDES the target cell
        for icell in df_R.index.values:
            #print('icel is '+icell)
            NNlist = NNindex.loc[icell].tolist()[0:] # return integer IDs: Also keep the first entry which is redundant to cell name
            NNlistNames = cellIndexMap.loc[NNlist].values.flatten() # Cells for performing regressin
            if (len(NNlist) != len(NNlistNames)):
                print('NNLS mismatch: NNlist and NNListNames')
                print('cell maps')
                print(str(cellIndexMap))
                cellIndexMap.to_csv('cellMapIndex.tsv')
                print('detailed output')
                for ival in NNlist:
                    print('ival '+str(ival))
                    print('cell val '+str(cellIndexMap.loc[ival])+'XXX')
            NNlistReadData = df_R.loc[NNlistNames] # Get the actual current reads
            icellTotal = datacelltotals.loc[icell,'CELLTOTAL'] # For predicting new R for the target cell/gene pair
            Xdata = datacelltotals.loc[NNlistNames].values.flatten()
            Ydata = NNlistReadData.values
            newGeneValues = list()
            #Xdata = np.insert(Xdata, 0, 0.0)
            #Yzeros = np.zeros(shape=(numGenes,1)) 
            #Ydata = np.insert(Ydata, 0, Yzeros.reshape(1,-1),axis=0)
            w,rnorm = aggregateNNLS(Xdata.reshape(-1,1),Ydata)
            ###w,rnorm = nnls(Xdata.reshape(-1,1),Ydata))
            #
            # Could predict all K+1 cells at ones and update the input R matrix
            # What if any of the reads are negative ?
            YdataPredict = np.dot(icellTotal,w) # Expect only one column of data
            #print('predict '+str(YdataPredict))
            ydatamin = YdataPredict.min()
            if (ydatamin < 0.0):
                print('Negative fit NNLS found for '+str(YdataPredict.shape))
                zeroout_indices = np.argwhere(YdataPredict < 0.0)
                YdataPredict[ YdataPredict < 0.0] = 0.0
                #YdataPredict[zeroout_indices]=0.0
                #print(str(zeroout_indices))
                print('NNLS applied a builtin floor to cell fit: should never happen '+str(zeroout_indices.shape)+' '+str(icell))
            # Some values can be < 0 probably because the cluster neighbors are poorly chosen
            # Should we set a floor of zero?
            RT[icell]=YdataPredict.flatten()
            RT.index = df_R.columns.values
        print('completed NNLS regressions '+str(tm.time()-timein))
        return (RT.T)

    def writeNewR(self):
        self.df_new_R.to_csv(self.outputRfilename,sep=' ')
        print('wrote out new R matrix '+self.outputRfilename)
        print('keepEffect is '+str(self.keepEffects))

    def writeNewS(self):
        self.df_new_S.to_csv(self.outputSfilename,sep=' ')
        print('wrote out new S matrix '+self.outputSfilename)
        print('keepEffect is '+str(self.keepEffects))
 
    def getOutputRfilename(self):
        return (self.outputRfilename)

    def getOutputSfilename(self):
        return (self.outputSfilename)

# Another rwqs change from the drs giving rise to even uglier code

    def scaleResults(self, df_R, batchfile,origScaling,logScaledResults,cellScale):
        """ For the impute R (which includes group effects) scale 
        data for read counts, and then studentize the features to N(0,1)
        (value+1)*median-all-cell-read / call total read
        The post averaged cell totals is approx 2100 for a factor of 1
        """
        scaleBounds = pd.DataFrame()
        covs,oneHotTerms = getKnownGroupEffects(df_R,batchfile)
        print(str(df_R.columns))
        print(str(covs))
    
        df_R_X_i=df_R.drop(covs,axis=1,inplace=False)
        df_new_R = df_R[covs] # Hold back until the end
        df_R_X = df_R_X_i.astype(float) # Copy false or not doesn't update inplace
        factor=1.0
        total_reads = float(df_R_X.values.sum())
        num_reads = float(df_R_X.values.size)
        ave_total_reads = total_reads / num_reads
        # Sometimes the data come in as ints
        print('convert data type to float: use a mean method:')
        total_mean_c = pd.DataFrame(df_R_X.mean(axis=1)) # or do we want median values
        total_mean_c.columns=['TOTALC']
        total_correction_factor = factor * ave_total_reads / total_mean_c['TOTALC']
        if (cellScale):
            print('Initial Guess: Will also scale cel total counts')
        ###############################################
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
        df_new.index = df_R_X.index.values
        df_new.columns = df_R_X.columns.values

    # Add effects back into the data object

        finalS = pd.merge(df_new_R,df_new,left_index=True,right_index=True)
        df_new_S = finalS
        print('Scale the post-regress R function')
        print(str(df_new_S.shape))
        print('---------------')
        return(df_new_S)

    def scaleResultsPrevious(self,df_R,):
        """ For the impute R (which includes group effects) scale 
        data for read counts, and then studentize the features to N(0,1)
        (value+1)*median-all-cell-read / call total read
        The post averaged cell totals is approx 2100 for a factor of 1
        Perhaps do not wish to always take the log(v+1) of the new imputed results
        """
        factor = 10000.0
        # First ave number of reads per cell (or do we want median values?)
        total_reads = float(df_R.values.sum())
        num_reads = float(df_R.values.size)
        ave_total_reads = total_reads / num_reads
        # Alternative method use the median
        ## total_sum_c = pd.DataFrame(df_R.sum(axis=1))
        ## median_total_reads = total_sum_c.median()
        #
        ## total_median_c = pd.DataFrame(df_R.median(axis=1)) # or do we want median values
        ## total_median_c.columns=['TOTALC']
        total_mean_c = pd.DataFrame(df_R.mean(axis=1)) # or do we want median values
        total_mean_c.columns=['TOTALC']
        # Ave number of reads per cells divided by cell reads
        total_correction_factor = factor * ave_total_reads / total_mean_c['TOTALC']
        # If we feature scale after the cell scale, we might get cell totals of < 0
        if (self.origScaling):
           print('Mean center scaling')
           df_new_S = pd.DataFrame(sklearn.preprocessing.scale(df_R, with_mean=True, with_std=True, copy=True,axis=0).tolist())
        else:
           print('Regresss S Guess scaling: MinMax')
           scaler = MinMaxScaler(feature_range=(0.0,1.0)) # Might also want 0.1,0.9 instead
           df_new_S = pd.DataFrame(scaler.fit_transform(df_R))
        df_new_S.index = df_R.index.values
        df_new_S.columns = df_R.columns.values
        ##if (self.logScaledResults):
        ##    df_scale_R = np.log((df_R+1.0).mul(total_correction_factor,axis=0))
        ##else:
        ##    df_scale_R = df_R.mul(total_correction_factor,axis=0) # Scale cells to have same total reads
        # standardize FEATURES not cells
        print(str(df_new_S.shape))
        #print(str(df_new_R)) 
        print('---------------')
        return(df_new_S)

    def runProcess(self):

        #keepEffects=True

        print(' read matrix '+self.rawfilename)
        print(' Index neighbors '+self.xtildeNeighborIndicesFilename)
        print(' Distance neighbors '+self.xtildeNeighborDistancesFilename)
        t0=tm.time()
        RinData = pd.read_csv(self.rawfilename,delim_whitespace=True,index_col=0, header=0)
        NNindex = pd.read_csv(self.xtildeNeighborIndicesFilename,delim_whitespace=True,index_col=0,header=0)
        NNdistance = pd.read_csv(self.xtildeNeighborDistancesFilename,delim_whitespace=True,index_col=0,header=0)
        print(tm.time()-t0)
        # Fetch covariates to carry around separately
        columnEffects,oneHotList = getKnownGroupEffects(RinData,self.batchfilename)  # oneHotList not used at this time
        df_Z = RinData[columnEffects]
        df_Z.index = RinData.index.values
        df_R = RinData.drop(columnEffects,axis=1,inplace=False)
        ##df_R.set_index('CELL',inplace=True)
        # Total reads per CELL
        datacelltotals = pd.DataFrame(df_R.sum(axis=1))
        datacelltotals.reset_index(inplace=True)
        datacelltotals.columns=['CELL','CELLTOTAL']
        datacelltotals.set_index('CELL',inplace=True)
        # Integer cell ID to cell name
        cellIndexMap = buildCellIndexMap(NNindex)
        # Build regression
        print('Call regression')
        # Can this result in negative values for R?
        if (self.origRegress):
            df_new_R = self.regressCellValues(df_R, NNindex,cellIndexMap,datacelltotals)  # All Z columns have been removed
        else:
            df_new_R = self.regressCellValuesNNLS(df_R, NNindex,cellIndexMap,datacelltotals)
        print('min value of regressed R is '+str(df_new_R.values.min()))
        # Build the properly formatted output matrix including Z covariates
        numRcells = df_R.shape[0]
        numNNcells = NNindex.shape[0]
        if (numRcells != numNNcells):
            print('Cell rank of input R data and input K data are not equal. The resulting data object will take intersection')
            print('Need to investigate: should ABORT')
            print('R and NN cell ranks are '+str(numRcells)+' '+str(numNNcells))
            #sys.exit()
        print('R and NN cell ranks are '+str(numRcells)+' '+str(numNNcells))
        # Compute a feature scaled and log transformed version log the R matrix (called S)
        df_new_S = self.scaleResults(df_new_R, False, self.origScaling, self.logScaledResults, self.cellScaledResults)

        # To maintain computation using the so-called original sin model we need to muck
        # around with kepeping or not the effects: df_Z
        # Add effects back into the data object

        if (self.keepEffects):
            finalR = pd.merge(df_Z,df_new_R,left_index=True,right_index=True)
            finalS = pd.merge(df_Z,df_new_S,left_index=True,right_index=True)
        else:
            finalR = df_new_R
            finalS = df_new_S 
        self.df_new_R = finalR 
        self.df_new_S = finalS

        #print('Write to disk the new R matrix which is the imputed data and the S matrix which scales R as follows')
        #print('S = log( (R+1)*cellCorrectionFactor)')
        #self.writeNewR()
        #self.writeNewS()
        return ()
