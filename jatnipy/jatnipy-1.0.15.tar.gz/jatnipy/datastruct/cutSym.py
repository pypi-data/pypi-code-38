import numpy as np
#A should be a np.array like A=np.array([[1,1],[1,1]])
def cutSym(A,pin,pout):
	A = np.asarray(A)
	N=A.shape[0]
	for i in range(1,N):
		for j in range (i+1,N+1):
			if A[i-1,j-1] ==1:
				r=np.random.uniform(0,1)
				if r <= pin:
					A[i-1,j-1]=0
				elif r<=pin+pout:
					A[j-1,i-1]=0
	return A
