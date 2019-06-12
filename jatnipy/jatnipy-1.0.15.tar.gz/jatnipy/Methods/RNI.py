import numpy as np
from Methods.RInorm import RInorm
from datastruct.Dataset import Dataset
import copy
def RNI(*args):
	R = RInorm()
	Da = Dataset()
	rawZeta = 0
	regpath = 'input'
	alpha = 0.01
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
			if len(args[i]) >1:
				zetavec = args[i]
			else:
				alpha = args[i]
# should input the data#I don't write it
	lamda = np.asarray(data.lamda)
	P = np.asarray(data.P)
	if np.size(lamda) == 2:
		o = np.ones((P.shape[0],P.shape[1]))
		gamma,ps,Nrps = R.RInorm(np.asarray(Da.response(data,net)).T,np.asarray(data.P).T,np.dot(lamda[(int(len(lamda)/2-1))],o.T),np.dot(lamda[(int(len(lamda)/2))],o.T)+np.finfo(float).eps,alpha)
		
	else:
		o = np.ones(P.shape[1])
		gamma,ps,Nrps = R.RInorm(np.asarray(Da.response(data,net)).T,np.asarray(data.P).T,np.dot(lamda[(int(len(lamda)/2-1))].T,o).T,np.dot(lamda[(int(len(lamda)/2-1))].T,o).T+np.finfo(float).eps,alpha)
	if regpath is 'full':
		zetavec = np.abs(gamma[:].T)
		zetavec = np.unique(zetavec)
	
	if not rawZeta and regpath is 'input':
		zetaRange = []
		estA = gamma
		estAtmp = estA!=0
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
		temp = np.abs(gamma) <= zetavec[i]
		Atmp = copy.deepcopy(gamma)
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
	
