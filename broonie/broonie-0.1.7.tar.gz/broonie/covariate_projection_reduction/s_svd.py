#################################################################
##
## Some elementary steps of the method by
## Aliverti, Lum, Johndrow, and Dunson.
## Attempt to build the simulation data set as instructed in 
## arXiv: 1810.08255v1 18,Oct,2018, pg 8
##
## READ preconstructed X and Z matrices
##
## Return the proper U and S matrices to construct Xtilde
## Xtilde is retunred as a NUMPY array
##
## The below code is equivelent to ALiverti et. al sSVD method
## sSVD is basically the same as sOG with the exclusion of the linear fit
##
##################################################################

import pandas as pd
import numpy as np
from numpy import zeros
from numpy import diag
import math
import matplotlib.pyplot as plt
import sklearn.preprocessing
from scipy.optimize import line_search,brentq,brent
from scipy import stats
import random

#####################################################################

class sSVDCovariateProjection(object):
    """Perform the projection of Z from X. Ultimately construct the final U and S
    matrices required ot buld a new X-tilde matrix
    
    Attributes
    ----------
    self.metadata = 'base naming for output files U and S and Xtilde'
    self.X: input X array in numpy format
    self.Z: input Z array in nunpy format
    self.n: Number of obsewrvations
    self.p: Number of parameters
    self.k: number of components - an input parameter for variable reduction selection
    self.w: Number of Z covariates to remove (not tested sufficiently beyond 1)
    self.conv_steps: Parameters driuving the convergence of Js
    self.conv_steps: Parameters driving the convergence of Theta (large u)
    self.prog_params: specify verbosity for now
    self.initialGuess declares intent to provuide a U and S starting matrix FROM which
        u and s initial vectors will be grabbed

    OUTPUTS U, S, (normalized),finalError list
    """

    def __init__(self, k, metadata='defaultName',initialGuess=False,inU=0,inS=0):
        self.metadata = metadata
        self.prog_params = {
            'verbose':False,
            'debug':False }
        self.conv_steps = {
            'lim_max':200,
            'lim_std':60,
            'lim_step':5 }
        self.conv_params = {
            'maxiter':500,
            'tolerance':1e-6,
            't_val':10,
            'diffTol':1e-7 }
        self.k = k
        self.data_read = False
        self.completeErrors = list()
        self.initialGuess=initialGuess
        self.guessU = inU
        self.guessS = inS

    def set_conv_params(self, in_params):
        self.conv_params = in_params
        return

    def set_conv_steps(self, in_steps):
        self.conv_steps = in_steps
        return

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

    def get_completeErrors():
        return (completeErrors)

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
        if (self.initialGuess):
            print('Initial guess for U and S is provided')
            inn=self.guessS.shape[0]
            inp=self.guessU.shape[1]
            ink=self.guessS.shape[1]
            print('Parameters found for initial Guesses: '+str(inn)+' '+str(inp)+' '+str(ink))
            if ( self.n != inn or self.p != inp or self.k != ink):
                print(self.guessU.shape)
                print(self.guessS.shape)
                print('Guess sizes mismatch n,p,or k: Reset guess status to RANDOM')
                self.initialGuess=False
        return

##################################################################
# Find Theta computations: These are usually inside of iterative search methods
# methods for finding the best THETA: Primarily when > t_val
# NOTE if X is not centered/scaled. this function gets heavily impacted versus t_val = 10 

    def Stheta(self, x, Xts, t_val=0):
        """Evaluate the function S_theta == S_theta(Xts) = =sign(Xts)(avbs(Xts)-theta)I(abs(Zts))
        """
        newX = self.SthetaMatrix(x, Xts)
        stheta = np.abs(newX).sum()-t_val
        if (self.prog_params['debug']): print('Stheta: input lambda is '+str(x)+' output Stheta estimate '+str(stheta))
        return(stheta)

# Apply the final Stheta to generate the U matrix
# In this situation "*" is a Hadamard product (element wise)
# Danger checking a float for zero

    def SthetaMatrix(self, theta, Xts):
        """Evaluate the function S_theta == S_theta(Xts) = =sign(Xts)(avbs(Xts)-theta)I(abs(Zts))
        If theta enters as None then no root NOR minimum was found. So simply return the original Xts vector
        as if the large phase iterations were never entered
        """
        if (theta is None):  # Should almost never get here
            print('Warning: Stheta was None should not commonly be here')
            #Xts / np.linalg.norm(Xts)
            return ( self.normMatrix(Xts))
        absXts = np.abs(Xts)
        signXts = np.sign(Xts)
        newX = signXts * (absXts-theta) * ((np.sign(absXts-theta)+1.0)/2.0)
        normNewX = np.linalg.norm(newX)
        if (normNewX==0.0):
            if (self.prog_params['debug']): print('Xnew norm is zero: probably root finder is at boundary')
            return (np.abs(newX)) # returns an empty vector of zeros
        else:
            return (newX / normNewX )

###############################################################################
# Solver equations
# Options for computing the betas required for Z projection

    def solveBetaNaturalEquations(self, s,Z):
        """This can be used to solve for a number of Z terms >1
        On return is the new normalized s
        """
        newz = np.concatenate((np.ones((Z.shape[0],1)),Z),axis=1) 
        invZ = self.inverseZtZ(newz)
        betanew = np.matmul(invZ, np.matmul(np.transpose(newz),s))
        s = s - np.matmul(newz, betanew)
        #s = s / np.linalg.norm(s)
        s = self.normMatrix(s)
        return (s)

    def solveBetaLinearRegression(self, s,Z):
        """Solve using linregress. Can only have one Z component
        returns the new normalized s. Best numerical stability
        """
        #slope, intercept, r_value, p_value, std_err = stats.linregress(Z[:,0],s[:,0])
        print('Linear Regression solver')
        reg = linear_model.LinearRegression()
        ref.fit(Z,s)
        coefs = reg.coef_
        intercept = reg.intercept_.reshape(reg.intercept_.shape[0],1)
        data = np.append(intercept,coefs,axis=1).T
        newz = np.concatenate((np.ones((Z.shape[0],1)),Z),axis=1)
        s = s - np.matmul(newz, data)
        return (s)

    def solveBeta(self, s, Z, iflag=0):
        """interface to real solvers. Manually choose one for now
        iflag=0 linearregression solver
        iflag=1 natural equation solvers ( possible numerical instability)
        """
        if (iflag !=0 and iflag!=1):
            print('Wrong iflag choice: changing to to iflag=1 natural eqn solvers')
            iflag=1
        if (iflag==0):
            return(self.solveBetaLinearRegression(s,Z))
        else:
            return(self.solveBetaNaturalEquations(s,Z))
        
#################################################################################
# iterative methods

    def runBrentQ(self, lim, Xts, t_val):
        """Run a single instance of BrentQ
        """
        try:
              thetaStar = brentq(self.Stheta, 0, lim, args=(Xts,t_val))
        except:
              thetaStar = None
        return (thetaStar)

    def iterativeRootFind(self, increased_lim, Xts, t_val):
        """Find ROOT of the Stheta function
        """
        debug = self.prog_params['debug']
        verbose = self.prog_params['verbose']
        if (debug): print('Enter iterativeRootFind')
        icount=0
        while (increased_lim < self.conv_steps['lim_max']):
              icount += 1
              thetaStar= self.runBrentQ(increased_lim, Xts, t_val)
              increased_lim += self.conv_steps['lim_step']
              if (verbose) :print('---- iterating over find root theta step lim is '+str(increased_lim)+' theta '+str(thetaStar))
        return(thetaStar,icount)

    def iterativeMinimumFind(self, increased_lim, Xts, t_val):
        """Find the MINIMUM of the Stheta function IFF no ROOT found
        """
        debug = self.prog_params['debug']
        verbose = self.prog_params['verbose']
        if (debug): print('Enter iterativeMinimizeFind')
        thetaStar = None
        try:
              thetaStar = brent(self.Stheta,args=(Xts,self.conv_params['t_val']))
        except:
              thetaStar = None
              if (verbose): print('---- Looking for minumum. lim is '+str(increased_lim)+' theta '+str(thetaStar))
        return(thetaStar)

################################################################################
# Misc methods

    def checkUnormalization(self, U):
        """ Return the average error per diagonal of the input array
        """
        n = U.shape[0]
        s = np.sum(np.diag(np.matmul(np.transpose(U),U)))
        return ((n-s)/n)
    
    def inverseZtZ(self, Z):
        """return a 2D array Inverse of the overlap matrix for the giuven input array
        """
        A = np.matmul(np.transpose(Z),Z)
        return (np.linalg.pinv(A))

    def centerAndScale(X):
        outX = sklearn.preprocessing.scale(Xprescaled,axis=0, with_mean=True, with_std=True, copy=True)
        return(outX)

    def initialGuessRandomU(self):
        """Abstract it for now since we may want to read in guesses from 
        other sources
        """
        u0 = np.random.normal(0,1,size = (self.p,1))
        #u0 = u0 / np.linalg.norm(u0)
        u0 = self.normMatrix(u0)
        return (u0)

    def initialGuessRandomS(self):
        """Abstract it for now since we may want to read in guesses from 
        other sources
        """
        s0 = np.random.normal(0,1,size = (self.n,1))  # Go ahead and keep s,u as this allocates memory for them 
        #s0 = s0 / np.linalg.norm(s0)
        s0 = self.normMatrix(s0)
        return (s0)

    def fetchGuesses(self,j):
        """Simply grab the jth entry from U and S and return as a vector u,s
        We don't need ot check errors too much as we've already confirmed
        U and S conform
        """
        print('get U and S guess for j = '+str(j))
        u = self.guessU[j,]
        s = self.guessS[:,j]
        #u.reshape(self.guessU.shape[1],1)
        #s.reshape(self.guessS.shape[0],1)
        return( u.reshape(self.guessU.shape[1],1),s.reshape(self.guessS.shape[0],1))
        return (u,s)

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

################################################################################
# Perform the full solution set here
# Begin algorithym: Specify K the "cluster size" from which projections will be performed
# On input we need X(nxp) and Z(nx1). Information regarding the error convergence rates
# are collected for future analyses

    def computeUandS(self):
        """Perform the full procedure here. We should refactor this but who has time now?
        """
        self.outputMatrixRanks() # This guarentees handling the guess correctly by resetting class flags
        k = self.k
        n = self.n
        p = self.p
        w = self.w
        prog_params = self.prog_params
        conv_params = self.conv_params
        conv_steps = self.conv_steps
        X = self.X
        Z = self.Z
# Specify Initial guesses: is reading in a guess potentially useful?
        U = np.zeros((k,p)) 
        S = np.zeros((n,k))
        P = np.zeros((n,n))
        u0 = self.initialGuessRandomU() # May be used even if you specified a guess U
        s0 = self.initialGuessRandomS()
        convergedJs = ['Notconverged']*k
        finalError = [-99]*k
        #completeErrors = list() 
        verbose = prog_params['verbose']
        for j in range(0,k):
            if (verbose): print('Perform outer sweep for j = '+str(j))
            nit = 0
            err = 10
            #
            if (self.initialGuess):
                u,s = self.fetchGuesses(j)  # NOTE we do not update the guess data Just use as a starting point
            else:
                u = u0
                s = s0
            px = np.matmul(np.identity(n)-P,X) if j != 0 else X
            error = list()
            deltaErr=err
            while (nit < conv_params['maxiter'] and err > conv_params['tolerance'] and deltaErr > conv_params['diffTol']):
                if (verbose): print('While iteration '+str(nit)+' for J = '+str(j))
                errold = err
                sold = s
                uold = u
                s = np.matmul(px,u)  
                s = self.normMatrix(s)
                s = s / np.linalg.norm(s)
                ##Not used s = self.solveBeta(s,Z,iflag=0) #iflag 0 is linregress 
                Xts = np.matmul(np.transpose(X),s)
                if (np.abs(Xts).sum() < conv_params['t_val']):
                    print('small u < t_val')
                    #u = Xts / np.linalg.norm(Xts)
                    u = self.normMatrix(Xts)
                else:
                    if (verbose): print('large u: >= t_val'+str(conv_steps['lim_std'])+' '+str(conv_params['t_val']))
                    thetaStar = self.runBrentQ(conv_steps['lim_std'], Xts, conv_params['t_val'])
                    increased_lim = conv_steps['lim_std'] + conv_steps['lim_step']
                    if (thetaStar is None):
                        thetaStar,icount = self.iterativeRootFind(increased_lim, Xts, conv_params['t_val'])
                    if (thetaStar is None): # try another method to estimate thetaStar
                        print('Find theta using minimizer')
                        thetaStar = self.iterativeMinimumFind(increased_lim, Xts, conv_params['t_val'])
                        print('minimum stheta is  '+str(thetaStar))
                    u = self.SthetaMatrix(thetaStar, Xts)
                nit += 1
                err = (sum(np.abs(s-sold)) + sum(np.abs(u-uold)))[0]
                if (err <= conv_params['tolerance']):
                    print('U: J term '+str(j)+' converged to '+str(err)+' in numiter = '+str(nit))
                    convergedJs[j]='Converged'

                error.append(err)    # Grab these to study convergence behavior for a given j
                finalError[j] = err
                deltaErr = np.abs(errold-err) # alternative criteria for completing J
                if (deltaErr <= conv_params['diffTol'] and convergedJs[j] != 'Converged'):
                    print('U: J term '+str(j)+' stuck at '+str(err)+' in numiter = '+str(nit))
                    if (verbose): print('Warning (u/s) is stuck')
                    convergedJs[j]='Stuck'
            P = P + np.matmul(s,np.transpose(s))
            U[j,] = u.flatten()
            S[:,j] = s.flatten()
            self.completeErrors.append(error)
            if (verbose):
                print('--------- Status of converged for each J for K = '+str(k))
                print(convergedJs)
                print(finalError)
        d = np.identity(k)
        np.fill_diagonal(d, diag(np.matmul(np.transpose(S),np.matmul(X,np.transpose(U)))))
        print(diag(d))
        S = np.matmul(S,d)
        print('Finished projecting Z out of Xk')
        #Xtilderaw = np.matmul(S,U)
        #Xtilde =  sklearn.preprocessing.scale(Xtilderaw,axis=0, with_mean=True, with_std=True, copy=True)
        print('Final convergence status')
        print(convergedJs)
        print(finalError)
        return(U,S,finalError)
