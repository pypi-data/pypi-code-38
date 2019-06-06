from sklearn import linear_model
import numpy as np
import copy
import glmnet_py
from glmnet import glmnetSet
from glmnet import glmnet
from datastruct.Dataset import Dataset

def Glmnet(*args):
	Da = Dataset()
	rawZeta = 0
	zetavec = []
	net = []
	alpha = 1
	regpath = 'input'
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
			if zetavec:
				zetavec = args[i]	
			else:
				alpha = args[i]

# should input the data#I don't write it
	if zetavec:
		regpath = 'full'
	
	if not rawZeta and regpath is 'input':
		zetaRange = []
		tol = 10**-6
		zmax = 1
		zmin = 0
		estA = Glmnet(data,net,zmax,True)
		while np.count_nonzero(estA[0]) > 0:
			tmp = zmax
			zmax = zmax*2
			estA = Glmnet(data,net,zmax,True)
		while (zmax - zmin) > tol:
			i = (zmax + zmin)*0.5
			estA = Glmnet(data,net,i,True)
			if np.count_nonzero(estA[0]) ==0:
				zmax = i
			else:
				zmin = i
		zetaRange.append(0)
		zetaRange.append(zmax)
		delta = zetaRange[1]-zetaRange[0]
		zetavec = zetavec*delta+zetaRange[0]

	if regpath == 'full':
		zetavec = np.zeros(np.asarray(data.P).shape[0])
		for i in range(np.asarray(data.P).shape[0]):
			fit = glmnet(x=Da.response(data,net).T,y=np.transpose(-np.asarray(data.P,dtype=np.float64)[i,:]),family = 'gaussian',nlambda=np.asarray(data.P).shape[0],alpha=alpha)
			if i == 0:
				zetavec = zetavec
			else:
				zetavec = np.insert(zetavec, i, fit['lambdau'], axis=0)
		zetavec = np.unique(np.sort(zetavec))
	
	
	if not rawZeta:
		zetaRange=[]
		zetaRange.append(min(zetavec))
		zetaRange.append(max(zetavec))
		delta = zetaRange[1]-zetaRange[0]
	else:
		zetaRange=[]
		zetaRange.append(0)
		zetaRange.append(1)		
		delta = 1
	Afit = 0
	a=[]
	for i in range(np.asarray(data.P).shape[0]):
		fit = glmnet(x=Da.response(data,net).T,y=np.transpose(-np.asarray(data.P,dtype=np.float64)[i,:]),family = 'gaussian',alpha=alpha,lambdau=zetavec)['beta']
		
	
		
		if i == 0:
			Afit = np.zeros((np.asarray(data.P).shape[0], fit.shape[0], fit.shape[1]))
			Afit[i,:,:] = fit[:,:]
		if i == 1:
			Afit[i,:,:] = fit[:,:]
	
	
		else:
			Afit[i,:,:] = fit[:,:]
	
	
	Afit[:,:,:] = Afit[:,:,Afit.shape[2]::-1]
	if regpath == 'full':
		zetavec = (zetavec-zetaRange[0])/delta
		return Afit,zetavec,zetaRange
	elif regpath == 'input':
		return Afit,zetavec,zetaRange
	

