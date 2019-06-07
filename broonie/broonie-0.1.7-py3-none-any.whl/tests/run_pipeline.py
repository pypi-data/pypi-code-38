#
# Construct the data sets given the sizes n,p,k,and w
#
import time as tm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from broonie.project_group import projectGroupDataClass
from broonie.generate_neighbor_matrix import generateNeighborMatrixClass
from broonie.regress import regressDataClass
from broonie.construct_initial_guess import constructInitialGuess
import sys
from sklearn.externals.joblib import Parallel, delayed

#############################################################################
# Define functions for convergence testing
# X matrices include all effects: So we want to remove them all (again)

maxDiffElemsThreshold = 0.1
maxFrobeniusThreshold = 0.05
maxIterations = 12

iterationMode = 'raw'
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
#initialGuess.runInitialGuess()
initialGuess.fetchInitialGuess() # Take Seurat imputed data rescale to MinMax (0,1) and proceed
initialGuessFilename = initialGuess.getOutputFilename() # return Ben's seurat regressed data set as initial guess
print('output bounds filename is '+initialGuess.getBoundsFilename())
scaleBounds = initialGuess.fetchScaleBounds()


# Initialize the iterative procedure 
inputfilename = initialGuessFilename
inputregressionfilename = rawfilename

# Try using the pregressed file as the "raw" data
# rawfilename = inputfilename

istart = 0 
kindicesprevious = None
converged=False

print('Read RAW input file '+rawfilename)
RinData = pd.read_csv(rawfilename,index_col=0,delim_whitespace=True) # Bootstrap for the convergence testing
Sold = None 
Scurrent = RinData

if (iterationMode == 'raw'):
    print('Iteration will impute always versus RAW R')
else:
    print('Iteration will impute always versus current R')

while istart < maxIterations:
    #
    # if scaling by cells and features neede then do it here> Not required for initialGuess data
    print('Start the next new iteration'+str(istart))
###################################################### group effect
    outtildemeta='outputXtilde_'+str(istart)+'_'
    print('Run projection')
    x = projectGroupDataClass(k,inputfilename,inlist,outtildemeta,scale=True) # regress studenizes already
    x.reportParameters()
    x.runProjection()
    xtilde = x.fetchXtilde() # Keep this for testing convergence
    xfilename = x.getXtildeFilename()
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
    inputXfilename = xfilename
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
    z = regressDataClass(knn,inputregressionfilename,yindexfilename,ydistancefilename,outputRfilename,outputSfilename)
    z.reportParameters()
    z.runProcess()
    z.writeNewR()
    z.writeNewS()
    #inputrawfilename = z.getOutputRfilename() # This still contains effects like the rawR
    #############################################################
    #
    xtildeprevious = xtilde # Hold for next convergence test
    # This approach results in osscilation of the Max elements
    Scurrent = z.getSmatrix()
    #inputRmatrix = z.getRawRmatrix()
    inputfilename = z.getOutputSfilename() # Pass back to the OG methods
    if (iterationMode == 'raw'):
        inputregressionfilename = rawfilename
    else:
        print('Iteration will impute always versus RAW R')
        inputregressionfilename = z.getOutputRfilename()
    #
    istart += 1
#
if (converged):
    print('Iterations has converged')
print('Exit the loop with number of iteration = '+str(istart))
print('imputation completed')
print('Final imputted file is '+ z.getOutputRfilename())

