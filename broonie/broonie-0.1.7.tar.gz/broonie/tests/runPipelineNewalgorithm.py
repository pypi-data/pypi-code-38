
# Construct the data sets given the sizes n,p,k,and w
#
import time as tm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from projectGroupDataClass import projectGroupDataClass
from generateNeighborMatrixClass import generateNeighborMatrixClass
from regressDataClass import regressDataClass
from constructInitialGuess import constructInitialGuess
import sys
from sklearn.externals.joblib import Parallel, delayed

#############################################################################
# Define functions for convergence testing
# X matrices include all effects: So we want to remove them all (again)

maxDiffElemsThreshold = 0.1
maxFrobeniusThreshold = 0.01
maxIterations = 12

##iterationMode = 'raw'
##iterationMode = 'incremental'

def dropAllEffects(df_X):
    currentPossibleColumnEffects = ['TREATMENT','MOUSE','SEX','DATE','NODEID']
    allColumns = df_X.columns.values
    foundColumns = list(set(allColumns) & set(currentPossibleColumnEffects))
    print('Number of check convergence: group effect columns in data is '+str(foundColumns))
    print('They are: '+str(foundColumns))
    return(df_X.drop(foundColumns,axis=1,inplace=False))

def checkConvergence(df_inX, df_inXold):
    """It has happened that the two input matrices have different row orders
    So we must address that here
    We do not anticipate checking Xtilde matrices. Rather R or S. Thus we must
    account for the possible covariates
    """
    print('in 1 '+str(df_inX.shape))
    print('in 2 '+str(df_inXold.shape))
    index1 = df_inX.index.values
    index2 = df_inXold.index.values
    if (index1.shape[0] != index2.shape[0]):
        print('different numbers of cells in the checkConvrgence: Abort')
        print(str(df_inX.shape))
        print(str(df_inXold.shape))
        sys.exit()
    combined = list(set(index1).intersection(index2))

    # first do they contain the same elements?

    converged = False
    df_X = dropAllEffects(df_inX.loc[combined]) 
    df_Xold = dropAllEffects(df_inXold.loc[combined])
    maxDiffElems =  (df_X-df_Xold).values.max()
    print('Max element '+str(maxDiffElems))
    if (maxDiffElems <= maxDiffElemsThreshold):
        print('X coverged on a maximum per-element threshold '+str(maxDiffElems))
        converged=True
    print('Max diff elem '+str(maxDiffElems))
    # Compute the frobenious norm  based convergence criteria
    print('try froben norm ')
    frac = np.linalg.norm(df_X-df_Xold) / np.linalg.norm(df_X)
    print('Convergence frac is '+str(frac))
    if (frac <= maxFrobeniusThreshold):
        print('X coverged on a frobenius threshold '+str(frac))
        converged=True
    print('Frobenious norm '+str(frac))
    return (converged)

def filterAmendedHeaders(allheaders):
    """ Remove any entry containing "encoded" or "ENC"
    These are hard-coded terms in the PROJECT methods. Beware
    """
    rawindices = [i for i in allheaders if not ('encoded' in i or 'ENC' in i)]
    return (rawindices)


def processMetaData(df_Z):
    allheaders = df_Z.columns.values 
    origheaders = filterAmendedHeaders(allheaders)
    return (allheaders,origheaders)

print('Begin imputation')

# Number of parallel jobs for the cluster code
# Presumably threadbased. So don.t go too big. 8 or 16 at the most
# at njobs=1 the jobs takes at ~15,000 secs and at njobs=16 total time is 1,903 sec.
njobs = 16 
# Specify subspace for group effect reduction
k = 60
# Specify number of NNs for regression (actually we use knn+1 becasue we include the target cell
knn = 10

# Initial Read data (R naught)

# RAW DATA
rawfilename='/projects/sequence_analysis/vol1/prediction_work/CausalInference/CausalNetworking_forKirk/PCAProjectionImputationPipeline/MouseTumor_allMice_allGenes_Rawdata/mouse_raw_data_allcells_Notscaled.tsv'

# Group effects to exclude at every iteration
inlist='MOUSE_DATE_SEX_TREATMENT'

# Fetch an initial guess. In this example we simply take the RAW data and also Read Ben's associzated "regressed" data.
# Bens data is the seurat processed scaling of the Raw data. Moving forward, we may want to process initial guesses differently

outfilename = 'initialGuess.tsv'
initialGuess = constructInitialGuess(rawfilename,outfilename,batchfile=False,origScaling=False,logScaledResults=False)
initialGuess.setOrigScaling(False)
initialGuess.reportScaling()
initialGuess.runInitialGuess()
initialGuessFilename = initialGuess.getOutputFilename() # return Ben's seurat regressed data set as initial guess
print('output bounds filename is '+initialGuess.getBoundsFilename())
scaleBounds = initialGuess.fetchScaleBounds()


# Initialize the iterative procedure 
inputfilename = initialGuessFilename

istart = 0 
converged=False

# Here we only do the projection once
outtildemeta='outputXtilde_New'
print('Run New projection')
x = projectGroupDataClass(k,inputfilename,inlist,outtildemeta,scale=True,origScaling=False) # regress studentizes already
x.reportParameters()
x.runProjection()
xtilde = x.fetchXtilde() # Keep this for testing convergence

xfilename = x.getXtildeFilename()
inputregressionfilename = xfilename
inputXfilename = xfilename

#####################################################

Sold = None
Scurrent = xtilde 

while istart < maxIterations:
    #
    # if scaling by cells and features neede then do it here> Not required for initialGuess data
    print('Start the next new iteration'+str(istart))
###################################################### check convergence
# Note rows might be differently ordered
# Need to double check the test
# Check convergece of the R matrix ( One could also use the S matrix)
    if (Sold is not None):
        converged = checkConvergence(Scurrent, Sold)
    print('Convergence testing status is '+str(converged))
    if (converged):
        print('S has converged')
        break
##################################### Second. reclustering
# inputfilename='60_MOUSEDATESEXTREATMENT_Xtilde_ZscoreOrder.tsv'
# No group effects are included in this file

    outputIndices = 'dfIndices-'+str(istart)+'.tsv'
    outputDistances = 'dfDistances-'+str(istart)+'.tsv'
    print('Run clustering ' + inputXfilename)
    y = generateNeighborMatrixClass(knn,inputXfilename,outputIndices,outputDistances,njobs)
    y.reportParameters()
    y.runProcess()
    y.writeClusterInformation() # Write out the K and distance matrices
    yindexfilename = y.getIndexFilename()
    ydistancefilename = y.getDistanceFilename()
    kindices = y.reportIndices()
#################################### Third run the regression
    print('Run regressions')
    inputrawfilename = rawfilename
    zindexfilename = yindexfilename
    zdistancefilename = ydistancefilename
    outputRfilename ='newRoutput-'+str(istart)+'.tsv'
    outputSfilename ='newSoutput-'+str(istart)+'.tsv'
    Sold = Scurrent
    print(inputrawfilename)
    print(yindexfilename)
    print(ydistancefilename)
    #
    #use the oldS instead of raw R inputrawfilename
    #Inputfilename SHOULD not contain negative terms
    z = regressDataClass(knn,inputregressionfilename,yindexfilename,ydistancefilename,outputRfilename,outputSfilename,origScaling=False,logScaledResults=False)
    z.reportParameters()
    z.reportScaling()
    z.runProcess()
    z.writeNewR()
    z.writeNewS()
    #inputrawfilename = z.getOutputRfilename() # This still contains effects like the rawR
    #############################################################
    #
    xtildeprevious = xtilde # Hold for next convergence test
    # This approach results in osscilation of the Max elements
    Scurrent = z.getSmatrix()
    #Rcurrent = z.getRmatrix()

    #inputRmatrix = z.getRawRmatrix()

    inputregressionfilename = z.getOutputSfilename() # For regressing
    #inputregressionfilename = z.getOutputRfilename() # As another option
    inputXfilename = z.getOutputSfilename()# For clustering

    #if (iterationMode == 'raw'):
    #    inputregressionfilename = rawfilename
    #else:
    #    print('Iteration will impute always versus RAW R')
    #    inputregressionfilename = z.getOutputRfilename()
    #
    istart += 1

# If not converged proceed with gernating the final R. We could consider using this
# as an initial guess for the next run

if (converged):
    print('#################################  Iteration has converged')

#####################################
# Construct the final unscaled matrix with (linear) effects reintroiduced.
currentXtilde = Scurrent
cellIndex = currentXtilde.index.values
features = currentXtilde.columns.values

#####################################
# Get effects metadata
# NOTE we read the Z matric that contains BOTH the original effects data AND the filtered/encoded data
df_Zall = x.fetchZ()
allheaders,origheaders = processMetaData(df_Zall)

actualHeaders =  currentXtilde.columns.values # May not contain ANY effect terms but will have lots of features
intersectList = list(set(allheaders) & set(actualHeaders))
currentXtildeDropEffects = currentXtilde.drop(intersectList,axis=1)   # Generally we would expect no effects to be found

##################################### Fold Effects back into solution
# Must fuss around with including or not the covariates
# Do we keep df_new_S or df_new_R?

U,d,VT,effectCorrection = x.returnSVDdata()
df_new_S_temp = currentXtildeDropEffects + np.matmul(effectCorrection,VT)
df_orig_Z = df_Zall[origheaders]
 
##################################### Inverse scale the solution
# Xpreminmax = y(max-min)+min
# THIS WILL NOT WORK for centerMean : I.e., origScaling=True
df_scaleBounds = initialGuess.fetchScaleBounds() 

# TODO Recast this into a high performance approach
df_new_temp_unscaled = pd.DataFrame()
for i in df_scaleBounds.index:
    max = df_scaleBounds.loc[i]['MAX']
    min = df_scaleBounds.loc[i]['MIN']
    df_new_temp_unscaled[i] = [(j-min)/(max-min) for j in df_new_S_temp[i]]

# Add original effect columns back in and we are finished

df_new_temp_unscaled.index = df_new_S_temp.index

finalR_scaled = pd.merge(df_orig_Z,df_new_S_temp,left_index=True,right_index=True)
finalR = pd.merge(df_orig_Z,df_new_temp_unscaled,left_index=True,right_index=True)

outputRimputed = 'Imputed_R_matrix_descaled_withEffectColumns.tsv'
finalR.to_csv(outputRimputed,sep=' ')

outputRimputedScaled = 'Imputed_R_matrix_scaled_withEffectColumns.tsv'
finalR_scaled.to_csv(outputRimputedScaled,sep=' ')

#
if (converged):
    print('Iterations has converged')
print('Exit the loop with number of iteration = '+str(istart))
print('imputation completed')
print('Final imputted descaled file is '+ outputRimputed) 
print('Final imputted scaled file is '+ outputRimputedScaled)

