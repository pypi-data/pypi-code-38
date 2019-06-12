#keep going to do

import numpy as np
def candidateP():
    def optimalRandomP(A,nCandidates,nm):
        n=nm(1)
        m=nm(2)        
        UA,SA,VA = np.linalg.svd(A)
        G = -np.linalg.pinv(A)
        limitSVY = 0.33
        level1 = np.logspace(-1,-3,base=10,num=3)
        level = np.append(level1,level1[2])
        tol = 10**-4
        keepOneElementOnEachColumn = True
