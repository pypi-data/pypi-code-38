#################################################################
##
## Some elementary steps of the method by
## Aliverti, Lum, Johndrow, and Dunson.
## Attempt to build the simulation data set as instructed in 
## arXiv: 1810.08255v1 18,Oct,2018, pg 8
##
## READ preconstructed X and Z matrices
##
## NON iterative solution probably best for the p < n case. Solve
## The SVD equations directly

## Can we reintroduce the "linear" terms of group effects back into the Xtilde matrix?
## The nonlinear terms are lost to the residuals vector and so prob canot be recovered.

##################################################################

import pandas as pd
import numpy as np
from numpy import zeros
from numpy import diag
import math
import matplotlib.pyplot as plt
import sklearn.preprocessing
from scipy.sparse.linalg import svds, eigs
from scipy.linalg import svd
from scipy.optimize import line_search,brentq,brent
from scipy import stats
from sklearn import linear_model
from scipy.spatial.distance import cdist
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import RidgeCV
from sklearn.datasets import load_boston
from sklearn.preprocessing import StandardScaler

import random
import sys

#############################################################################

#
# Also want to return VT,S for subset of betas set to ZERO 

class denseClassCovariateProjectionReductionReaddata(object):
    """Perform the projection of Z from X. Ultimately construct the final U and S
    matrices required to buld a new X-tilde matrix
    
    Attributes
    ----------
    self.metadata = 'base naming for output files U and S and Xtilde'
    self.X: input X array in numpy format
    self.Z: input Z array in nunpy format
    self.n: Number of obsewrvations
    self.p: Number of parameters
    self.k: number of components - an input parameter for variable reduction selection
    self.w: Number of Z covariates to remove (not tested sufficiently beyond 1)

    OUTPUTS VT, S (normalized)
    """

    def __init__(self, k, metadata='defaultName',initialGuess=False,inU=0,inS=0):
        self.metadata = metadata
        self.k = k
        self.betaIndicesToZero = list()
        self.prog_params = {
            'verbose':False,
            'debug':False }

    def set_prog_params(self, in_params):
        self.prog_params = in_params
        return

    def set_k(self, ink):
        self.k = ink
        return

    def get_X(self):
        return self.X

    def get_Z(self):
        return self.Z

    def specifyBetasToZero(self, inBetas):
        self.betaIndicesToZero = inBetas

    def readXandZdata(self, filenameX='XdataSimulatedAliverti.tsv', filenameZ='ZdataSimulatedAliverti.tsv'):
        dfX = pd.read_table(filenameX, delim_whitespace=True)
        self.X = dfX.values
        dfZ = pd.read_table(filenameZ, delim_whitespace=True)
        self.Z = dfZ.values
        self.n = self.X.shape[0]
        self.p = self.X.shape[1]
        self.w = self.Z.shape[1]
        self.data_read=True
        return

    def setXandYdata(self, inX,inZ):
        """X and Z are in numpy ndarray format
        """
        self.X = inX
        self.Z = inZ
        self.n = self.X.shape[0]
        self.p = self.X.shape[1]
        self.w = self.Z.shape[1]
        self.read_data = True
        return

    def outputMatrixRanks(self):
        print('n,p,k,w are')
        print(str(self.n)+' '+str(self.p)+' '+str(self.k)+' '+str(self.w))
        return

    def returnSVDdata(self):
        return self.U,self.d,self.VT,self.effectCorrection

###############################################################################
# Basic Solver equations: OK these have been tested
# Options for computing the betas required for Z projection

    def fetchBetaNaturalEquations(self,X,Z):
        """This can be used to solve for a number of Z terms >1
        On return is the new normalized s
        Actuallly, if al the effects are onehotencoded (0,1) and
        since every row as a catagory, then the inverse should always
        be singular becasue SUM(onehot)i = Meani
        So we should either do a pseudoinvsser with throw a message OR
        solve the OLS using function calls
        """
        print('Natural Equation solution using pseudoInverse')
        w = Z.shape[1]
        newz = np.concatenate((np.ones((Z.shape[0],1)),Z),axis=1)
        invZ = self.inverseZtZ(newz)
        betanew = np.matmul(invZ, np.matmul(np.transpose(newz),X))
        return (betanew.tolist())

    def fetchBetaLinearRegression(self,X,Z):
        """Solve using linregress. Can only have one Z component
        returns the new normalized s. Best numerical stability
        """
        print('Linear Regression solver')
        reg = linear_model.LinearRegression()
        reg.fit(Z,X)
        coefs = reg.coef_
        intercept = reg.intercept_.reshape(reg.intercept_.shape[0],1)
        data = np.append(intercept,coefs,axis=1).T
        return (data.tolist())

    def fetchBetaLinearRegressionOld(self,X,Z):
        """Solve using linregress. Can only have one Z component
        returns the new normalized s. Best numerical stability
        """
        slope, intercept, r_value, p_value, std_err = stats.linregress(Z[:,0],X[:,0])
        debug = self.prog_params['debug']
        if (debug):
            print('intercept '+str(intercept))
            print('slope '+str(slope))
        return ([[intercept],[slope]])

    def fetchBeta(self, X, Z, iflag=0):
        """interface to real solvers. Manually choose one for now
        iflag=0 linearregression solver
        iflag=1 natural equation solvers ( possible numerical instability)
        """
        if (iflag !=0 and iflag!=1):
            print('Wrong iflag choice: changing to iflag=0 linear regression solver')
            iflag=0
        if (iflag==0):
            return(self.fetchBetaLinearRegression(X,Z))
        else:
            return(self.fetchBetaNaturalEquations(X,Z))

###############################################################################
# Alternative Solver and related equations: 
# Options for computing the betas required for Z projection withj colinearity. Use ridge regularization
# Need a way to search out the best lambda terms
# Featuresa MUST be standardize here for proper training

    def fetchRidgeBeta(self, X, Z): 
        """Solve using ridge regression and simple CV determination of lambda
        Z here acts as the independant variable and X the dependent term
        NOTE inputs are PANDAS dataframes
        """
        alphaList =  [x/10.0 for x in range(1,100,5)]
        regr_cv = RidgeCV(alphas=alphaList)  # Provide a range of alphas to test
        model_cv = regr_cv.fit(Z, X)
        print ('Best model params is ='+str(model_cv.alpha_))
        #ridge = linear_model.Ridge(alpha=a, normalize=True,fit_intercept=False)
        #ridge.fit(X, y)
        #coefs.append(ridge.coef_)
        type(regr_cv.coef_)
        print(str(regr_cv.coef_.shape))
        betas = regr_cv.coef_[alphaList.index(model_cv.alpha_),:]
        intercept = regr_cv.intercept_[alphaList.index(model_cv.alpha_)]
        print('intercept '+str(intercept))
        print('slope '+str(betas))
        return ([[intercept],betas])
        print(results)

############################################################################
# MISC
    def checkUnormalization(self, U):
        """ Return the average error per diagonal of the input array
        """
        n = U.shape[0]
        s = np.sum(np.diag(np.matmul(np.transpose(U),U)))
        return ((n-s)/n)

    def inverseZtZ(self, Z):
        """return a 2D array pseudo Inverse 
        By construction this should always be singular
        """
        print('Using a Moore-Penrose pseudoinverse to solve the OLS')
        A = np.matmul(np.transpose(Z),Z)
        Ainv = np.linalg.pinv(A)
        return (Ainv)

    def centerAndScale(X):
        outX = sklearn.preprocessing.scale(Xprescaled,axis=0,with_mean=True,with_std=True, copy=True)
        return(outX)

    def normMatrix(self,M):
        """Simply return the normalized term for M
        IF the norm is ZERO then thorugh a warning and return M 
        unchanged
        """
        invM = np.linalg.norm(M)
        if (invM == 0.0):
            print('matrix norm is ZERO return M unchanged')
            return (M)
        return (M / invM )

###################################################################################
# Get the work done 
    def computeUandS(self):
        """Perform the full procedure here. We should refactor this but who has time now?
        """
        self.outputMatrixRanks() # This ensures handling the guess correctly by resetting class flags
        k = self.k
        n = self.n
        p = self.p
        w = self.w
        X = self.X
        Z = self.Z
        p = X.shape[1]

## Perform the SVD. 
## It is unclear if simply sorting in reverse is sufficient given the ridiculous 
## definition provided by scipy of sorting "not in increasing order"
## So we have to do this the hard way  - such madness
## Can choose to zero out betas (temp) here
        if (k==p):
            U, s, VT = svd(X.astype('d'))
        else:
            U, s, VT = svds(X.astype('d'),k=k,which='LM')
        high2low = np.argsort(s)[::-1][:k]
        s = s[high2low]
        U = U[:,high2low]
        VT = VT[high2low,:]
        d = np.identity(k)
        np.fill_diagonal(d, s)
        # Keep the U,S,VT for inverse OG transformations
        self.U = U
        self.VT = VT
        self.d = d
        lmX = np.matmul(U,d) 
        temp = self.fetchBeta(lmX,Z,iflag=0)
        self.beta = temp
        newz = np.concatenate((np.ones((Z.shape[0],1)),Z),axis=1)
        self.effectCorrection = np.matmul(newz , temp)
        S = lmX - self.effectCorrection
        return(VT,S)

    def computeUandS_ZscoredEigenvalues(self):
        """Select order of components based on the variance_explained Zscores rather than
        eigenvalue magnitude. It seems no difference in the selection
        """
        self.outputMatrixRanks() # This ensures handling the guess correctly by resetting class flags
        k = self.k
        n = self.n
        p = self.p
        w = self.w
        X = self.X
        Z = self.Z
        p = X.shape[1]
        if (k==p):
            U, s, VT = svd(X.astype('d'))
        else:
            U, s, VT = svds(X.astype('d'),k=k,which='LM')
        sdev = s / np.sqrt(np.maximum(1, X.shape[1] - 1))
        Proportion = np.square(sdev) / sum(np.square(sdev))
        m = Proportion.mean()
        sd = Proportion.std()
        zscore = (Proportion - m)/sd
        high2low = np.argsort(zscore)[::-1][:k]
        s = s[high2low]
        U = U[:,high2low]
        VT = VT[high2low,:]
        d = np.identity(k)
        np.fill_diagonal(d, s)
        # Keep the U,S,VT for inverse OG transformations
        self.U = U
        self.VT = VT
        self.d = d
        lmX = np.matmul(U,d)
        temp = self.fetchBeta(lmX,Z,iflag=0)
        self.beta = temp
        newz = np.concatenate((np.ones((Z.shape[0],1)),Z),axis=1)
        self.effectCorrection = np.matmul(newz , temp)
        S = lmX - self.effectCorrection
        return(VT,S)

    def computeUandS_ZscoredEigenvaluesReturnReconstructed(self,betaZeroList):
        """Select order of components based on the variance_explained Zscores rather than
        eigenvalue magnitude. It seems no difference in the selection
        Also return the Matricers that result from zeroing out the betas listed
        in betaZeroList
        """
        self.outputMatrixRanks() # This ensures handling the guess correctly by resetting class flags
        k = self.k
        n = self.n
        p = self.p
        w = self.w
        X = self.X
        Z = self.Z
        p = X.shape[1]
        if (k==p):
            U, s, VT = svd(X)
        else:
            U, s, VT = svds(X,k=k,which='LM')
        sdev = s / np.sqrt(np.maximum(1, X.shape[1] - 1))
        Proportion = np.square(sdev) / sum(np.square(sdev))
        m = Proportion.mean()
        sd = Proportion.std()
        zscore = (Proportion - m)/sd
        high2low = np.argsort(zscore)[::-1][:k]
        s = s[high2low]
        U = U[:,high2low]
        VT = VT[high2low,:]
        d = np.identity(k)
        np.fill_diagonal(d, s)
        lmX = np.matmul(U,d)
        temp = self.fetchBeta(lmX,Z,iflag=0) # Might want to regularized
        tempZeros = temp.copy()
        zerorow = [0.0]*k
        for i in self.betaIndicesToZero: # Set values to zero FOR EACH K component
            print(' Zero index includes intercept term '+str(i+1))
            tempZeros[i+1]=zerorow
        newz = np.concatenate((np.ones((Z.shape[0],1)),Z),axis=1)
        #print(str(temp))
        #print('_____________________________________________________________')
        #print('_____________________________________________________________')
        #print(str(tempZeros))
        S = lmX - np.matmul(newz,temp)
        self.effectCorrectionReconstruction = np.matmul(newz,tempZeros)
        SZeros = lmX - self.effectCorrectionReconstruction 
        # NOTE VT here corresponds to U in the other solvers
        return(VT,S,SZeros)

# Use the Ridge methods: THis might be required as beta values are rather big

    def computeUandS_ZscoredEigenvaluesRidge(self):
        """Select order of components based on the variance_explained Zscores rather than
        eigenvalue magnitude. It seems no difference in the selection
        """
        self.outputMatrixRanks() # This ensures handling the guess correctly by resetting class flags
        k = self.k
        n = self.n
        p = self.p
        w = self.w
        X = self.X
        Z = self.Z
        p = X.shape[1]
        if (k==p):
            U, s, VT = svd(X)
        else:
            U, s, VT = svds(X,k=k,which='LM')
        sdev = s / np.sqrt(np.maximum(1, X.shape[1] - 1))
        Proportion = np.square(sdev) / sum(np.square(sdev))
        m = Proportion.mean()
        sd = Proportion.std()
        zscore = (Proportion - m)/sd
        high2low = np.argsort(zscore)[::-1][:k]
        s = s[high2low]
        U = U[:,high2low]
        VT = VT[high2low,:]
        d = np.identity(k)
        np.fill_diagonal(d, s)
        lmX = np.matmul(U,d)
        temp = self.fetchRidgeBeta(lmX,Z)
        newz = np.concatenate((np.ones((Z.shape[0],1)),Z),axis=1)
        S = lmX - np.matmul(newz , temp)
        return(VT,S)

