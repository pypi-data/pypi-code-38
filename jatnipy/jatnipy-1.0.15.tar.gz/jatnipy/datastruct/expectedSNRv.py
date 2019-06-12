#keep going to do
import numpy as np
from normv import normv
from Dataset import Dataset
import scipy
from scipy import stats
from scipy.stats import chi2
def expectedSNRv(data):
	alpha = 0.01
	Da = Dataset()
	if isinstance(data,dict):#for dictionary
		N = data['N']
		M = data['M']
		P = data['P']
		Y = Da.response1(data)
	else:#for object
		N = data.N
		M = data.M
		P = data.P
		Y = Da.response(data)
	ResponseLengths = normv(Y,'vec')
	RegressorLength = ResponseLengths/((Y.T).shape[0])**0.5
	if isinstance(data,dict):#for dictionary
		lamda = data['lambda'][:int(len(data['lambda'])/2)]
	else:#for object
		lamda = data.lamda[:int(len(data['lambda'])/2)]
	SNRv = np.divide(np.dot(RegressorLength,M**0.5),(np.dot(lamda,scipy.stats.chi2.ppf(1-alpha,M)))**0.5)
	##cannot run in original codings from ResponseLengths
	return SNRv
