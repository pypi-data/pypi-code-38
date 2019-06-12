import numpy as np
import scipy
from scipy import sparse
from numpy import linalg as LA
from numpy.linalg import matrix_rank
import copy
def scalefree(N,n,*args):
	rank_check = True
	if len(args) > 0:
		for i in range(len(args)):
			if isinstance(args[i],bool):
				rank_check = args[i]
			else:
				seed = args[i]
	if n < 1:
		sparsity = n
	else:
		sparsity = n/N
	m0 = np.around(sparsity*N)
	#exist??
	c=sparse.rand(m0*2,m0*2-1,density=m0/m0**2,format='coo',dtype=None,random_state=None)	
	d=c.toarray()
	seed = d !=0
	k = 0
	if rank_check:
		while LA.matrix_rank(seed) < np.min(seed.shape):
			seed = np.random.rand(seed.shape[0],seed.shape[1])*copy.deepcopy(seed)
			k = copy.deepcopy(k)+1
			if not np.mod(k,100):
				print('k = %d'%k)
	tmp = np.zeros((m0*2,m0*2))
	for i in range(seed.shape[0]):
		tmp[i,i+1:] = seed[i,i:]
	for i in range(1,seed.shape[0]):
		tmp[i,:i-1] = seed[i,:i-1]
	seed = tmp+tmp.T !=0
	A = np.zeros((N,N))
	A[:seed.shape[0],:seed.shape[1]] = seed
	for i in range(m0*2,N):
		if rand < np.mod(sparsity,np.around(sparsity)):
			m = np.ceil(m0)
		else:
			m = np.mod(m0)
		if m==0:
			m = 1
		k=0
		while k < m:
			ps = 0
			r = rand
			for inode in range(i-1):
				pl = np.sum(A[inode,:i-1],axis=0)/np.count_zero(A[:i-1,:i-1])
				ps = copy.deepcopy(ps) + copy.deepcopy(pl)
				if r < ps:
					A[i][inode] = 1
					A[inode][i] = 1
					k = k+1
					break
	
