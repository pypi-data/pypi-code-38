#
# Construct the data sets given the sizes n,p,k,and w
#
import time as tm
import pandas as pd
import numpy as np
from broonie.project_group_sog import projectGroupDataClassSOG

#############################################################################
# Define functions for convergence testing
# X matrices include all effects: So we want to remove them all (again)

print('Begin imputation')

# Specify subspace for group effect reduction
k = 60

inputfilename='./DATA/initialGuess.tsv'

###################################################### group effect
# Straight up projection using the inlist and default effects
inlist='MOUSE_DATE_SEX_TREATMENT'
outtildemeta='testingOneXtilde_'
print('Run projection')
x = projectGroupDataClassSOG(k,inputfilename,inlist,outtildemeta)
x.reportParameters()
x.runProjection()
xtilde = x.fetchXtilde() # Keep this for testing convergence
xfilename = x.getXtildeFilename()

######################################################
# Attempt to reconstruct TREATMENT projection using the inlist and default effects
inlist='MOUSE_DATE_SEX_TREATMENT'
outtildemeta='testingTwoXtilde_'
print('Run projection')
x = projectGroupDataClassSOG(k,inputfilename,inlist,outtildemeta)
x.reconstructList('TREATMENT')
x.reportParameters()
x.runProjection()
xtilde = x.fetchXtilde() # Keep this for testing convergence
reconstructedXtilde = fetchReconstructedXtilde()
xfilename = x.getXtildeFilename()
reconstructedxfilename = getReconstructedXtilde()
print('Xtilde '+xfilename)
print('Reconstructed Xtilde '+reconstructedxfilename)

######################################################
# Use the filebased techniques for specifying possible effect names
# batchfile must contain ALL possible effects in the data set
# If batchfile list is incomplete errors from the SVD method will occur:
####
####AttributeError: 'str' object has no attribute 'conjugate'
####>>> xtilde = x.fetchXtilde() # Keep this for testing convergence
####>>> xfilename = x.getXtildeFilename()
####AttributeError: 'str' object has no attribute 'conjugate'
####>>> xtilde = x.fetchXtilde() # Keep this for testing convergence
####>>> xfilename = x.getXtildeFilename()

inlist='MOUSE_DATE_SEX_TREATMENT'
outtildemeta='testingThreeXtilde_'
batchfilename='listOfBatchEffects.txt'
x = projectGroupDataClassSOG(k,inputfilename,inlist,outtildemeta,batchfilename)
x.reportParameters()
x.runProjection()
xtilde = x.fetchXtilde() # Keep this for testing convergence
xfilename = x.getXtildeFilename()


######################################################
# Use the filebased techniques for specifying possible effect names
# And build a reconstructed matrix

inlist='MOUSE_DATE_SEX_TREATMENT'
outtildemeta='testingFourXtilde_'
batchfilename='listOfBatchEffects.txt'
x = projectGroupDataClassSOG(k,inputfilename,inlist,outtildemeta,batchfilename)
x.reconstructList('TREATMENT')
x.reportParameters()
x.runProjection()
xtilde = x.fetchXtilde() # Keep this for testing convergence
xfilename = x.getXtildeFilename()
reconstructedxfilename = getReconstructedXtilde()
print('Xtilde '+xfilename)
print('Reconstructed Xtilde '+reconstructedxfilename)


print('SOG projection completed')

