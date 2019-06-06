#keep going to do
import numpy as np
from numpy import linalg as LA
def weightP(A,P):
	UA,SA1,VA = LA.svd(np.asarray(M.A))
	VA = VA.transpose()
	SA = np.zeros((SA1.shape[0],SA1.shape[0]))
	for i in range(len(SA)):
		SA[i][i]=SA1[i]
	G=-LA.pinv(A)
	level = [0.1,0.01,0.01,0.001]
	tol = 10**-4
	limitSVY = 0.33
	k = 1
	removedelement = False
	while k <= len(level):
		SVY = np.svd(np.dot(G,P))[1]
		SVYsumPold = LA.norm(SVY-np.ones(SVY.shape),2)
		SVYsumP = SVYsumPold
		while True:
			for i in range(P.shape[0]):
				for j in range(P.shape[1]):
					if P[i][j] !=0:
						Ptemp = P
						Ptemp[i][j] = Ptemp[i][j] +level[k]
						SVY = LA.svd(np.dot(G,Ptemp))[1]
						SVYsumplus = LA.norm(SVY - np.ones(SVY.shape),2)
						Ptemp[i][j] = Ptemp[i][j] - 2*level[k]
						SVY  = svd(np.dot(G,Ptemp))[1]
						SVYsumminus = LA.norm(SVY - np.ones(SVY.shape),2)
						val = np.min([SVYsumP,SVYsumminus,SVYsumplus])
						ind = np.argmin([SVYsumP,SVYsumminus,SVYsumplus])
						SVYsumP = val
						if ind ==0:
							pass
						elif ind == 1:
							P[i][j] = P[i][j] - level[k]
						elif ind == 2:
							P[i][j] = P[i][j] + level[k]
			if SVYsumP -SVYsumPold < -np.finfo(float).eps:
				SVYsumPold = SVYsumP
			else:
				break
		k=k+1
	SVY = LA.svd(np.dot(G,P))[1]
	SVYeffall = np.max(np.abs(SVY-np.ones(SVY.shape)),axis = 0)
	###
	candidateP = P
	##print
