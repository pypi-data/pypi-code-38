#
# Construct the data sets given the sizes n,p,k,and w
# convert the covariate data to factors and/or indicator columns
# Jan 11:
#    Input argument for input file.
#    Modify list columnEffects to simply grab all THEN check for validity of input effect 
#
# New approach. Here we build a pipeline for imputing the RAW input data.
# We begin initially with the regressed data from BEN and so that data are also required.
# Add a method to return TWO matrices. One with all effects removesd and One with some effects 
# retained by zeroin out betas

# minMAx scaling as a possible alternatrive and allowing us to use Xtilde in the regression

# NOTE: Features are scaled (mean-centered or MinMax) but cells are not

###########################################################################

## Basic inpout file format
## CELL SEX DATE NODEID MOUSE 0610007N19Rik ........

import pandas as pd
import numpy as np
import time as tm
#import math
#import sys,ast
#import matplotlib.pyplot as plt
import collections
import sklearn.preprocessing
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from denseClassCovariateProjectionReductionReaddata import denseClassCovariateProjectionReductionReaddata

##########################################################################
# Basic functions

def constructMetaDataReadMatrix(indata,inColumnsForZ,batchfilename):
    """Determine what the possible set if EFFECTs are in the data set. Also updates
    a list of effects to treat as onehot encoded 
    """
    columnEffects,oneHotList = getKnownGroupEffects(indata,batchfilename)  # What effecs were found in fulldata
    # Which input exclusion effects remain valid  and were any left over ?
    columnsForZ = checkGroupEffectsValidity(inColumnsForZ, columnEffects)
    print('Input: Valid group covs are')
    print(columnsForZ)
    # First just get X the design data with no covariates information
    df_X = indata.drop(columnEffects,axis=1,inplace=False)
    # Need metadata for the final data object 
    indexing = df_X.index.values
    headers = df_X.columns.values
    #Now build the Z matrix  based on the input list.
    df_Z = indata[columnEffects]
    #Encode the Zs in preparation for x projection analysis
    df_Zall = df_Z 
    #print('oneHotList '+str(oneHotList))
    for effect in columnsForZ:
        #print('effect '+effect)
        if(effect in oneHotList):
            df_Zall = pd.merge(df_Zall, convertCovariateStringToOneHotEncoder(indata,effect),left_index=True,right_index=True)
        else:
            df_Zall = pd.merge(df_Zall, convertCovariateStringToFactors(indata,effect),left_index=True,right_index=True)
    df_Z = df_Zall.drop(columnEffects,axis=1,inplace=False)
    return df_X, df_Zall, df_Z, oneHotList
    
    # Special function when choosing MOUSE as a group variable
    # Convert a vector of 1s,2s,3s, etc. so several columns with 0s,1s exclusive
    # basically a set of onehot encoders
    # Just build and name a proper column of data then use sklearn oneHot encoding
    # Aliverti reported using this method doesn't have significant difference

    # TODO allow the USER to choice which effects should be onehot encoded
    
def convertCovariateStringToOneHotEncoder(df_in,effect):
    """We expect Z on entry to be an nx1 dataframe with the values
    In this approach we take the indicated colname and create new indicator 
    """
    # First encode the data
    indexing = df_in.index.values
    name = effect+'-encoded'
    df_Z = pd.DataFrame()
    df_Z = convertCovariateStringToFactors(df_in,effect)
    # Now expand and onehot
    enc = sklearn.preprocessing.OneHotEncoder(categories='auto')
    enc.fit(df_Z)
    onehotlabels = enc.transform(df_Z).toarray()
    data = onehotlabels
    numLabels = data.shape[1]
    newNameMeta = effect+'_ENC'
    newdf = list()
    for i in range(0,numLabels):
        namei = newNameMeta+str(i)
        newdf.append(pd.DataFrame({namei:data[:,i]}))
    df_onehot = pd.concat(newdf,axis=1)
    #df_onehot=pd.DataFrame({'MouseEnc0':data[:,0],'MouseEnc1':data[:,1],'MouseEnc2':data[:,2],'MouseEnc3':data[:,3],'MouseEnc4':data[:,4]})
    df_onehot['CELL']=indexing
    return (df_onehot.set_index('CELL'))

def convertCovariateStringToFactors(df,colname):
    """Convert Covariate factors to encoded integers
    Returns a new dataframe of one column
    """
    indexing = df.index.values
    newcolumnName = str(colname)+str('-encoded')
    le = sklearn.preprocessing.LabelEncoder()
    le.fit(df[colname].tolist())
    newCovariate = le.transform(df[colname].tolist())
    df_new = pd.DataFrame()
    df_new[newcolumnName] = newCovariate.tolist()
    df_new['CELL']=indexing 
    return (df_new.set_index('CELL'))

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

def checkGroupEffectsValidity(columnsForZ, columnEffects):
    """On input user request removal of columnsForZ
    Here we confimr if they all exist in the current data set. If not
    reduce columnsForZ to include only valid effects. Print out a message
    NOTE: always convert to and return uppercase for comparisons and subsequent analysis
    """
    upperColumnsForZ =list()
    for effect in columnsForZ:
        #upperColumnsForZ.append(effect.upper())
        upperColumnsForZ.append(effect)
    newList = list(set(upperColumnsForZ) & set(columnEffects))
    if ( newList.sort() != upperColumnsForZ.sort()):
        print('Input group list has been reduced based on preestablished possible effects')
        print('Size on data effects is '+str(len(columnsForZ))+' new removal list is of size '+str(len(newList)))
        print('New removal list is '+str(newList))
    return (newList)

def flatten(x):
    if isinstance(x, collections.Iterable):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

###############################################################################
# Start the class

class projectGroupDataClass(object):
    """ From the single-cell data reads. Perform a group-efforts projection using the OG method.
    Construct Xtilde and Z (covariates) Xtilde is standardized by default. Xtilde and Z are stored to disk and also 
    maybe returned using a class getter.

    Perform a group effects reduction of the sc data: 
    Supply a file of effects contained in your data set OR 
    by default anticipates covariates with the following names:
    ['TREATMENT','MOUSE','SEX','DATE','NODEID']
    On completion an Xtilde and associated Z matrix are written out
    On input:
    K = size of subspace for reduction 
    inputList = _ delimited list of covariates to EXCLUDE e.g., MOUSE_SEX_DATE
    infilename =  unscaled READs matrix including covariates
    outXtildemeta = metadata for building newfiles names for :
    outfilebase = outXtildemeta+str(K)
    Xtilde: outfilebase_Xtilde_Order.tsv'
    Z     : outfilebase_Z_Order.tsv'
    batchfilename point to a file that contains n rows and 1 column with relevant batch effect names:
    The list doesn't need to be exclusive. You do not need to remove all effects. Moreover, 
    For future version one can recover effect contributions as well

    Attributes
    ----------
    self.k = subspace from which projection will occur 
    self.inputList: UNDERSCORE delimited list of effects to project away. E.g., MOUSE_SEX_DATE
    self.batchfilename (opt) file that contains n rows and 2 column with relevant batch effect names
            col 1 effect name: col two either ONEHOT or CAT for type of inclusion
    self.scale = True/False. Standardize the Data prior to projection (default is True)
    self.outXtildemeta = String descriptor. Used to construct output filenames:
            outfilereconstructdata = outXtildemeta+'_reconstruct'+self.inReconstructList+'_'+str(K)
            self.outputZReconstructfile = outfilereconstructdata+'_Z_ZscoreOrder.tsv'
            self.outputXReconstructfile = outfilereconstructdata+'_Xtilde_ZscoreOrder.tsv'
    self.reconstructData (True/False). Declares building an additional Xtilde matrix keeping select effects
            in the matrix by zeroing out their betas
    self.inReconstructList: UNDERSCORE delimited list of effect to reintroduce if self.reconstruct Data=True
    self.origScaling True is mean-centered,std=1 scaling. False is MinMax scaling
    """
    def reportParameters(self):
        print('Infilename is '+self.infilename)
        print('Output metadata '+self.outXtildemeta)
        print('K subspace is '+str(self.k))
        print('exclude covariates list is '+self.inputList)
        print('Scale features is '+str(self.scale))
        if (self.reconstructData):
            print('A second Xtilde matrix will be created retaining the effects of:')
            print(self.inReconstructList)

    def __init__(self, k, infilename, inputList, outXtildemeta, batchfilename=False, scale=True, origScaling=True):
        self.k = k
        self.inputList = inputList
        self.infilename = infilename
        self.outXtildemeta = outXtildemeta
        self.batchfilename = batchfilename
        self.fulldata = pd.DataFrame()
        self.df_Xtilde = pd.DataFrame()
        self.df_XtildeZero = pd.DataFrame()
        self.df_Zall = pd.DataFrame()
        self.outputXfile = 'notSet'
        self.outputZfile= 'notSet'
        self.scale = scale if scale==False else True 
        self.reconstructData = False
        self.origScaling = origScaling if origScaling==False else True
        self.listOneHot = ['MOUSE'] # A default
        self.outputXReconstructfile = 'notset'
        self.outputZReconstructfile = 'notset'

    def setOrigScaling(self,inOrigScale):
        self.origScaling = inOrigScale if inOrigScale==False else True

    def reportScaling(self):
        print('Scaling Original type is '+str(self.origScaling))
   
    def fetchK(self):
        return(self.k)

    def returnSVDdata(self):
        return self.U,self.d,self.VT,self.effectCorrection

    def mapZtoBetas(self, inReconstructList,df_Z):
        """Given the input compound tab_delimited string, determine the beta indexing for removal
        This is tricky since some Zs are oneHot encoded giving rise to 
        multiple Betas. df_Zall already has all Z names in the headings
        and in order so use that. If the reconstructed inList doesn't exist
        set betas to -1 and reset self.reconstructData = False
        """
        #print('in MAP '+str(inReconstructList))
        covlist = inReconstructList.split('_')
        inColumnsForZ=list()
        for word in covlist:
            print('word '+word)
            inColumnsForZ.append(word)
        headers = df_Z.columns.values
        print(str(headers))
        print(str(inColumnsForZ))
        allindices = [i for i, s in enumerate(headers) if 'encoded' or 'ENC' in s]
        rawindices = [i for i, s in enumerate(headers) if ('encoded' in s) and (s.split('-')[0] in inColumnsForZ)]
        rawindices.append([i for i, s in enumerate(headers) if ('ENC' in s) and (s.split('_')[0] in inColumnsForZ)])
        #print('before reduction '+str(rawindices))
        minIndex = np.min(allindices)
        indices = [i-minIndex for i in flatten(rawindices)]
        indices.sort()
        print('sorted indices not including intercept term')
        return (indices)

    def reconstructList(self, inReconstructList):
        self.inReconstructList = inReconstructList
        self.reconstructData = True

    def fetchXtilde(self):
        return self.df_Xtilde
        
    def fetchZ(self):
        return self.df_Zall

    def fetchReconstructedXtilde(self):
        return self.df_XtildeZero

    def getXtildeFilename(self):
        return self.outputXfile
    
    def getZFilename(self):
        return self.outputZfile

    def getReconstructedXtilde(self):
        return self.outputXReconstructfile 

        ##########################################################
        # Start the work
        #
        # Specify as (for example) python denseProjectGroupData_MouseTumor.py 12 "DATE_MOUSE"
        # columnsForZ = ['MOUSE','SEX','DATE','NODEID']
        # Using a loop strcture to better control for column metadata
        # Example python projectGroupDataProcedure_MouseTumor.py 1000 'MOUSE_SEX_DATE'
        # inputList='SEX_DATE_MOUSE'
    
    def runProjection(self):
        K = self.k
        inputList = self.inputList
        infilename = self.infilename
        outXtildemeta = self.outXtildemeta
        covlist = inputList.split('_')
        inColumnsForZ=list()
        for word in covlist:
            inColumnsForZ.append(word)
        print('in K is '+str(K))
        print('Input: Unchecked group covs are')
        print(inColumnsForZ)
        print('Input: filename is '+infilename)
        print('Input: output Xtilde filename is '+outXtildemeta)
        if (self.reconstructData):
            print('Will also construct secondary Xtilde matrix zeroing out betas for')
            print(self.inReconstructList)
        # Metadata for the projection methods
        #metadata='mouseTumor_regressed'
        #runtype='EIGEN'
        metadata='mouseTumor_Zscoreregressed'
        runtype='ZSCORE' # Perform projectionn using Zscore ranked eigenvalues else uses eigenvalue magnetudes 
        # build outputfilename metadata
        outfilebase = outXtildemeta+str(K)
        outfilebase_meta=''
        outfilemetadata = outfilebase
        self.outputXfile = outfilemetadata+'_Xtilde_ZscoreOrder.tsv'
        self.outputZfile = outfilemetadata+'_Z_ZscoreOrder.tsv'
        if (self.reconstructData):
            outfilereconstructdata = outXtildemeta+'reconstruct'+self.inReconstructList+'_'+str(K)
            self.outputZReconstructfile = outfilereconstructdata+'_Z_ZscoreOrder.tsv'
            self.outputXReconstructfile = outfilereconstructdata+'_Xtilde_ZscoreOrder.tsv'
            print('Reconstructed X is '+self.outputXReconstructfile)
        self.fulldata = pd.read_table(infilename,delim_whitespace=True, index_col=0,header=0,low_memory=False)
        #########################################################
        # Build proper formatted data objects. Remove all Zs from fulldata and add to df_Z
        df_X, df_Zall, df_Z, self.listOneHot = constructMetaDataReadMatrix(self.fulldata,inColumnsForZ,self.batchfilename)
        self.df_Zall = df_Zall
        df_Zall.to_csv(self.outputZfile,sep=' ')
        betasToZero = list()
        ########################################################
        # Figure out from the reconstruction list which betas to zero 
        # Perform projection analysis. First standardize the data
        indexing = df_X.index.values
        headers = df_X.columns.values
        if (self.reconstructData):
            betasToZero = self.mapZtoBetas(self.inReconstructList,df_Z)
            print('Beta indexing for zeros '+str(betasToZero))
        # Scale features not cells
        if (self.scale and self.origScaling):
            sklearn.preprocessing.scale(df_X, axis=0, with_mean=True, with_std=True, copy=False)
        if (self.scale and not self.origScaling):
           print('Guess scaling: MinMax')
           scaler = MinMaxScaler(feature_range=(0.0,1.0)) # Might also want 0.1,0.9 instead
           df_X = pd.DataFrame(scaler.fit_transform(df_X))
        X = df_X.values
        Z = df_Z.values
        simdat = denseClassCovariateProjectionReductionReaddata(K,metadata)
        simdat.setXandYdata(X,Z)
        #NOTE X was be floating point ofr double prec
        if (self.reconstructData):
            simdat.specifyBetasToZero(betasToZero)
            VT,S,Szero = simdat.computeUandS_ZscoredEigenvaluesReturnReconstructed( betasToZero )
            print('Project using a Zscore-eigenvalue rank regression: Keep a reconstructed matrix')
        if (not self.reconstructData):
            if (runtype =='ZSCORE'):
                VT,S = simdat.computeUandS_ZscoredEigenvalues()
                print('Project using a Zscore-eigenvalue rank regression')
            else:
                VT,S = simdat.computeUandS()
                print('Project using eigenvalue rank')
        #
        self.U,self.d,self.VT,self.effectCorrection = simdat.returnSVDdata()
        #
        Xtilde = np.matmul(S,VT)
        df_Xtilde = pd.DataFrame(Xtilde)
        # Always scale the output result
        if (not self.origScaling):
            print('Guess scaling: MinMax')
            scaler = MinMaxScaler(feature_range=(0.0,1.0)) # Might also want 0.1,0.9 instead
            df_Xtilde = pd.DataFrame(scaler.fit_transform(df_Xtilde))
        else:
            sklearn.preprocessing.scale(df_Xtilde, axis=0, with_mean=True, with_std=True, copy=False)
        df_Xtilde['CELL']=indexing
        df_Xtilde.set_index('CELL',inplace=True)
        df_Xtilde.columns = headers
        print('write out new X with new metadata file')
        df_Xtilde.to_csv(self.outputXfile,sep=' ')
        self.df_Xtilde = df_Xtilde
        if (self.reconstructData):
            XtildeZero = np.matmul(Szero,VT)
            df_XtildeZero = pd.DataFrame(XtildeZero)
            if (not self.origScaling):
                print('Guess scaling: MinMax XtildeZero')
                scaler = MinMaxScaler(feature_range=(0.0,1.0)) # Might also want 0.1,0.9 instead
                df_XtildeZero = pd.DataFrame(scaler.fit_transform(df_XtildeZero))
            else:
                sklearn.preprocessing.scale(df_XtildeZero, axis=0, with_mean=True, with_std=True, copy=False)
            df_XtildeZero['CELL']=indexing
            df_XtildeZero.set_index('CELL',inplace=True)
            df_XtildeZero.columns = headers
            print('write out new reconstructed (some betas zeroed) X with new metadata file')
            df_XtildeZero.to_csv(self.outputXReconstructfile,sep=' ')
            self.df_XtildeZero = df_XtildeZero
        print('procedure completed')
