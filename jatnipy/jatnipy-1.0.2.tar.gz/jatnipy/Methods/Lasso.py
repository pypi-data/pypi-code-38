#from Dataset_fetch import fetch2
#fetch2(11)
#from Glmnet import Glmnet
#Glmnet(Data,'full')
from sklearn import linear_model
import numpy as np
def Lasso(*args):
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
			if not zetavec:
				zetavec = args[i]	
			else:
				alpha = args[i]
# should input the data#I don't write it
	if not zetavec:
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
		return zetaRange
		delta = zetaRange[1]-zetaRange[0]
		zetavec = zetavec*delta+zetaRange[0]
	if regpath == 'full':
		zetavec = np.zeros(np.asarray(data.P).shape[0])
		clf_v = linear_model.Lasso(alpha=1, tol=1e-6)
		for i in range(np.asarray(data.P).shape[0]):
			fit = clf_v.path(np.transpose(np.asarray(data.Y)),np.transpose(-np.asarray(data.P)[i,:]), n_alphas=np.asarray(data.P).shape[0])
			if i == 0:
				zetavec = fit[0]
			else:
				zetavec = np.insert(zetavec, i, fit[0], axis=0)
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
	for i in range(np.asarray(data.P).shape[0]):
		fit = clf_v.path(np.transpose(np.asarray(data.Y)), np.transpose(-np.asarray(data.P)[i,:]), alphas=zetavec)
		if i == 0:
			Afit = np.zeros((np.asarray(data.P).shape[0], fit[1].shape[0], fit[1].shape[1]))
			Afit[i,:,:] = fit[1]
		else:
			Afit[i,:,:] = fit[1]
	Afit[:,:,:] = Afit[:,:,Afit.shape[2]::-1]
	
	if regpath == 'full':
		zetavec = (zetavec-zetaRange[0])/delta
		return Afit,zetavec,zetaRange
	elif regpath == 'input':
		return Afit,zetavec,zetaRange
