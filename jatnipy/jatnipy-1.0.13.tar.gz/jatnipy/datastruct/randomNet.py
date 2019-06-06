'''research round how to use and '''

import numpy as np
import scipy.sparse as sparse

def randomNet (N,n):
	sparsity = n/N
	A = np.zeros((N,N))
	tspar = round(N**2*sparsity*N**2/(N*(N-1)))/N**2
	c=sparse.rand(N,N-1,density=tspar,format='coo',dtype=None,random_state=None)
	tmp = (1+np.random.uniform(0,1)*9)*c.toarray()	
	for i in range(1,tmp.shape[0]+1):
		A[i-1,i:] = tmp[i-1,i-1:]
	for i in range(2,tmp.shape[0]+1):
		A[i-1,0:i-2] = tmp[i-1,0:i-2]
	return A
