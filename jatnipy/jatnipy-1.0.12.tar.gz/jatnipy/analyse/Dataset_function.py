#from Network_fetch import fetch1
#from Dataset_fetch import fetch2
#Data = fetch2('')
#Net = fetch1('')
#from Dataset_function import true_response
#true_response(Data,Net)
#from 72-80
from analyse.Dataset_fetch import fetch2
import numpy as np
from numpy import linalg as LA
import scipy
from scipy import stats
data = fetch2('Nordling-ID1446937-D20150825-N10-E15-SNR3291-IDY15968.json') #can change the file name
def get_M():
	a = np.asarray(data['P'])
	return a.shape[1]
def get_N():
	b = np.asarray(data['P'])
	return b.shape[0]
def get_SNR_L():
	alpha = 0.01
def response(data,*args):
	n = np.asarray(data.P).shape[0]
	m = np.asarray(data.P).shape[1]
	if len(args) > 1  :
		if hasattr(data,'G'):
			Net = args[0]
			X = np.matmul(np.asarray(Net.G),(np.asarray(data.P)))
			Y = X + np.asarray(data.E)[:,0:m]
		else:
			Y = np.asarray(data.Y)
	else:
		Y = np.asarray(data.Y)
	return Y

def true_response(*args): ##449-465
	n = get_N()
	m = get_M()
	if len(args) > 1  :
		if 'G' in args[1]:
			Net = args[1]
			X = np.matmul(np.asarray(Net['G']),(np.asarray(data['P']) + np.asarray(data['F'])[:,0:m]))
			return X
		else:
			X = np.asarray(data['Y']) - np.asarray(data['E'])[:,0:m]
			
	else:
		X = np.asarray(data['Y']) - np.asarray(data['E'])[:,0:m]	
	return X
def get_SNR_L(): ##97-103
	alpha = 0.01
	sigma1 = LA.svd(true_response())
	sigma = min(sigma1[1])
	SNR = sigma/(scipy.stats.chi2.ppf(1-alpha,get_N()*get_M())*data['lambda'][0])**0.5
	return SNR
#from 103-133
def Phi():
	p = np.transpose(data['Y'])
	return p
def Xi():
	x = -np.transpose(data['P'])
	return x
def Upsilon():
	u = np.transpose(data['E'])
	return u
def Pi():
	p = -np.transpose(data['F'])
	return p
def Psi():
	a=np.asarray(Phi())
	b=np.asarray(Xi())
	p = np.hstack((a,b))
	return p
def Omicron():
	a=np.asarray(Upsilon())
	b=np.asarray(Pi())
	o = np.hstack((a,b))
	return o
	
