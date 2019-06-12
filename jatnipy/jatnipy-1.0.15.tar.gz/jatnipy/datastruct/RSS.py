#should keep going to do
import numpy as np
from Dataset import Dataset
def RSS(Alist,data,i,type1):
	Da =Dataset()
	if isinstance(data,dict):
		P = data['P']
		Y = Da.response1(data)
	else:
		P = data.P
		Y = Da.response(data)
	A = np.zeros(Alist.shape[0],Alist.shape[1],1)
	for j in range(Alist.shape[2]):
		A=Alist[:,:,j]
		
"""i should set a integral RSS line25-26"""
Pr = np.array(P)
Ar = np.array(A)
Yr = np.array(Y)
y = -np.linalg.pinv(A)*Pr[:,i]
p = -Ar*Yr[:,i]
"""line 29"""
np.cov(data)
