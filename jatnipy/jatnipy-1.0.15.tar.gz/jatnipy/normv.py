import numpy as np
from numpy import linalg as LA
def normv(*args):
	X=np.asarray(args[0])
	if X.ndim > 2:
		arraysize = X.shape
		X = X.reshape((arraysize[0],arraysize[1],arraysize[2]))
		temp = normv(X[:,:,0],args[1:])
		Y = np.zeros((temp.size,arraysize[2]))
		for i in range(arraysize[2]):
			Y[:,i] = normv(X[:,:,i],args[1:])
		if arraysize.size == 3:
			C = Y.reshape((temp.shape[0],temp.shape[1],arraysize[2]))
		else:
			C = Y.reshape((temp.shape[0],temp.shape[1],arraysize[2]))
	else:
		if len(args) ==2:
			if args[1] == 'vec':
				C = np.diag(np.dot(X.T,X))**0.5
			elif args[1] == 'l1':
				C = np.sum(np.abs(X))
			else:
				return LA.norm(args[0],np.inf)
		else:
			return LA.norm(args[0],np.inf)
	return C
