import numpy as np
from datastruct.Dataset import Dataset
import copy
def lsco(*args):
	rawZeta = 0
	regpath = 'input'
	net = []
	for i in range(len(args)):
		if hasattr(args[i],'F'):
			data = args[i]
		elif hasattr(args[i],'G'):
			net = args[i]
		elif isinstance(args[i],bool):
			rawZeta = args[i]
		elif isinstance(args[i],str):
			regpath = args[i]
		else:
			zetavec = args[i]
# should input the data#I don't write it
	Da = Dataset()
	if regpath is 'input':##zetavec and
		estA = np.dot(-np.asarray(data.P),np.linalg.pinv(Da.response(data,net)))
	else:
		Als = np.dot(-np.asarray(data.P),np.linalg.pinv(Da.response(data,net)))
		estA = Als
	if regpath is 'full':
		Als = Als.transpose()
		Als = Als.reshape((1,Als.shape[0]*Als.shape[1]))
		zetavec = abs(Als)
		zetavec = np.unique(zetavec)
	
	if not rawZeta and regpath is 'input':
		zetaRange = []
		estA = Als
		estAtmp = Als!=0
		for i in range(estAtmp.shape[0]):
			for j in range(estAtmp.shape[1]):
				if estAtmp[i][j] ==1:
					estA[i][j] = estA[i][j]
		zetaRange.append(np.min(np.abs(estA))-np.finfo(float).eps)
		zetaRange.append(np.max(np.abs(estA))+10*np.finfo(float).eps)
		delta =zetaRange[1]-zetaRange[0]
		zetavec = np.dot(zetavec,delta) +zetaRange[0]
	elif not rawZeta and regpath is 'full':
		zetaRange = []
		zetaRange.append(np.min(zetavec))
		zetaRange.append(np.max(zetavec))
		delta =zetaRange[1]-zetaRange[0]
	elif rawZeta and regpath is 'full':
		zetaRange = []
		zetaRange.append(0)
		zetaRange.append(1)
		delta = 1
	est = []
	for i in range(len(zetavec)):
		temp = np.abs(estA) <= zetavec[i]
		Atmp = copy.deepcopy(estA)
		for j in range(Atmp.shape[0]):
			for k in range(Atmp.shape[1]):
				if temp[j][k] ==1:				
					Atmp[j][k] = 0
		c = Atmp
		est.append(c)
	est = np.asarray(est)
	estA = np.zeros((est.shape[1],est.shape[2],est.shape[0]))
	for i in range(est.shape[0]):
		estA[:,:,i] = est[i]
	if regpath is 'input':
		return estA,zetavec,zetaRange
	elif regpath is 'full':
		zetavec = (zetavec-zetaRange[0])/delta
		return estA,zetavec,zetaRange
			
		
		
		
		###from here
		
