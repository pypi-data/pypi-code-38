#################################################################
##
## Some elementary steps of the method by
## Aliverti, Lum, Johndrow, and Dunson.
## Attempt to build the simulation data set as instructed in 
## arXiv: 1810.08255v1 18,Oct,2018, pg 8
##
## Generate a simulated dataset.
## n: number of observations
## p: number of explanatory bariables
## k: number of dimensions 
## w: number of z terms that are "group effects" to be folded into the data (X) Z(nxw)
##
## X(nxp)
## Z(nxw)
## Y(nx1)
##
## X.Y data are centered and scaled to 1 on exit
##
## metadata: Base naming for output filename construction

##################################################################

import pandas as pd
import numpy as np
from numpy import zeros
from numpy import diag
import matplotlib.pyplot as plt
import sklearn.preprocessing
import random

class constructSimulatedDatasetCode(object):
    """Construct data set consisting of X,Y, and Z for testing the
    group projection method of Aliverti,Lum, Johndrow,and Dunson
    A Z is constructed of size nxw dimensions which is then folded into the X
    terms for subsequent removal testing

    Attributes
    ----------
    self.metadata = 'experimentOne'
    seld.metaparams = 'additional filename metadata :n-p-k-w
    self.numsubjects = n
    self.numvariables = p
    self.numcomponents = k
    self.numZterms = w
    """
    def __init__(self, metadata='testing', n=1000, p=100, k=10, w=1):
        self.metadata = metadata
        self.n = n
        self.p = p
        self.k = k
        self.w = w
        self.metaparams = str(self.n)+'_'+str(self.p)+'_'+str(self.k)+'_'+str(self.w)
        if (self.w > 1):
            print('Current code tested for SINGLE Z component' )
            #self.w = 1
        self.dfX = pd.DataFrame()
        self.dfY = pd.DataFrame()
        self.dfZ = pd.DataFrame()

    def outputSimulationParams(self):
        print('-------------------------------------------------------')
        print('Simulation parameters follows')
        print('Number of observations(n) = '+str(self.n))
        print('Number of variables(p) = '+str(self.p))
        print('Number of components(k) = '+str(self.k))
        print('Number of Z terms(w) = '+str(self.w))
        print('Filename meta data are '+self.metadata+'_'+self.metaparams)
        print('-------------------------------------------------------')

    def setn(self,inn):
        self.n = inn
    def setp(self,inp):
        self.p = inp
    def setk(self,ink):
        self.k = ink
    def setw (self,inw):
        self.w

##
## If ZI is one column then python subtracts ZI from EACH COLUMN OF S. IF ZI has same columns as S
## Pands does a column-wise subtrraction, otherwise they are nonconforming and the method fails
## So we must explicitly iterate tp subtract all W columns from S
    def buildXandYmatrix(self,S,W,Z,beta):
        """ Each row is drawn from a p-variate standard normal dist with 
        mean vector u_i = (s_i-2z_i1)W,i=1,n
        W are going to build the vector (MU) for all N simultaniously
        How do we handle the covariance part?
        """
        n = S.shape[0]
        p = W.shape[1]
        k = W.shape[0]
        w = Z.shape[1]
        SmZI = S
        if (Z.shape[1] != 1):
            print('Z should only have a single column for now '+str(Z.shape[1]))
        if (w > 1):
            for i in range(0,w):
                SmZI = SmZI - 2.0*Z[:,i].reshape(n,1)
        else:
            SmZI = SmZI - 2.0*Z
        mu_matrix = np.matmul(SmZI,W)
        mu_matrix_y = np.matmul(SmZI,beta)
        outputX = np.zeros((n,p),dtype=float)
        outputY = np.zeros((n,1),dtype=float)
        # Second part. Construct p-variate normal distributed row with mean vector meanrow
        icov = np.identity(p)
        for irow in range(0,n):
            meanrow = mu_matrix[irow]
            outputX[irow]=np.random.multivariate_normal(meanrow,icov,1)
            meanYrow = mu_matrix_y[irow]
            outputY[irow]=np.random.normal(loc = meanYrow,scale = 1)
        return outputX,outputY,mu_matrix,mu_matrix_y

    def constructDataObjects(self):
        """Construct the X,Y terms based on W,S,beta
        """
        n = self.n
        p = self.p
        k = self.k
        w = self.w

        # Build S(n*k) and W(k*p): independant normal sampled entries
        S = np.random.normal(0,1,size = (n,k))
        W = np.random.normal(0,1,size = (k,p))

        # Build indicator variable to remove
        Z = np.random.binomial(1,0.5,size=(n,w)) # Get me n samples of [0,1]
        beta = np.random.uniform(-5.0, 5.0,size=(k*1))
        beta = beta.reshape(k,1)

        # Build the X,Y matrix 
        Xprescaled,Yprescaled,mu_matrix,mu_matrix_y = self.buildXandYmatrix(S,W,Z,beta)

        # Center and Scale the X,Y matrices
        print('scale center/stddev the X data')

        X = sklearn.preprocessing.scale(Xprescaled,axis=0, with_mean=True, with_std=True, copy=True)
        Y = sklearn.preprocessing.scale(Yprescaled,axis=0, with_mean=True, with_std=True, copy=True)
        self.dfX = pd.DataFrame(X)
        self.dfY = pd.DataFrame(Y)
        self.dfZ = pd.DataFrame(Z)
        return

        #def checkHistogram(name,column):
        #    """For the name = dfX,dfY,dfZ
        #    choose the column (0,..) for display as a histrogram
        #    """
        #    if (name != 'dfX' and name != 'dfY' and name != 'dfZ'):
        #        print('Bad name to histrogram: Use only dfX,dfY,or dfZ')
        #        return
        #    if (column >= name.shape[1]):
        #        print('Column specification to large: must be less than '+str(name.shape[1]-1))
        #        return
        #    plt.plot(name[,column])
        #    plt.show()
        #    return

    def writeObjectsToDisk(self):
        """Write the new X,Y,Z terms to disk. X,Y are scaled
        """
        meta_params = self.metaparams
        metadata = self.metadata
        xfilename = metadata+'_'+meta_params+'Xdata.tsv'
        yfilename = metadata+'_'+meta_params+'Ydata.tsv'
        zfilename = metadata+'_'+meta_params+'Zdata.tsv'
        print('Writing simulated datasets')
        print('X file = '+xfilename)
        print('Y file = '+yfilename)
        print('Z file = '+zfilename)
        self.dfX.to_csv(xfilename,sep=' ')
        self.dfY.to_csv(yfilename,sep=' ')
        self.dfZ.to_csv(zfilename,sep=' ')
        print('finished with writing simulated datasets')

    def writeCombinedObjectToDisk(self):
        """Write the new X,and Z terms as a singlew entity to disk. X are scaled
        """
        combinedR = pd.merge(self.dfZ,self.dfX,left_index=True,right_index=True)
        combfilename = metadata+'_'+meta_params+'XandZdata.tsv'
        print('Writing simulated datasets')
        print('Writing simulated datasets')
        print('X file = '+xfilename)
        combinedR.to_csv(combfilename,sep=' ')



