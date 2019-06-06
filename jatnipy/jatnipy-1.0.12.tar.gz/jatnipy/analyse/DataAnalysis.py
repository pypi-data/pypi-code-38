import numpy as np
from numpy import linalg as LA
from analyse.Dataset_function import true_response
from analyse.Dataset_function import response
from analyse.Model import Model
import scipy
from scipy import stats
from analyse.DataModel import DataModel
class DataAnalysis():
	def __init__(self):
		self.dataset = ''
		self.SNR_Phi_true= 0
		self.SNR_Phi_gauss = 0
		#self.SNR_L = 0
		self.SNR_phi_true = 0
		self.SNR_phi_gauss = 0
	def Data(self,data,*args):
		analysis = DataModel()
		'''
		if len(args) > 1:
			ind = ('tol' == args[0])
			if ind:
				analysis.tol = args[ind]
		'''
		analysis = self.analyse_model(analysis,data,args)
		return analysis

	
	def analyse_model(self,analysis,data,*args):
		analysis.dataset = data.name
		analysis.SNR_Phi_true = self.calc_SNR_Phi_true(data)
		analysis.SNR_Phi_gauss = self.calc_SNR_Phi_gauss(data)
		#analysis.SNR_L = self.calc_SNR_L(data)
		analysis.SNR_phi_true = np.min(self.calc_SNR_phi_true(data))
		analysis.SNR_phi_gauss = np.min(self.calc_SNR_phi_gauss(data))
		return analysis
	def identifier(self,data):
		if hasattr(data,'M'):
			dataset = data.dataset
		else:
			dataset = ''
		return dataset
	def calc_SNR_Phi_true(self,data):
		SNR1 = np.max(LA.svd(data.E)[1])
		SNR2 = np.min(LA.svd(true_response(data))[1])
		SNR = SNR2/SNR1
		return SNR
	def calc_SNR_phi_true(self,data):
		snr = []
		X = true_response(data)
		for i in range(int(data.N)):
			snr.append(LA.norm(X[i,:])/LA.norm(np.asarray(data.E)[i,:]))
		return snr
	def calc_SNR_Phi_gauss(self,data):
		alpha = DataModel.alpha()
		sigma = np.min(LA.svd(response(data))[1])
		SNR = sigma/(scipy.stats.chi2.ppf(1-alpha,(np.asarray(data.P).shape[0])*(np.asarray(data.P).shape[1]))*data.lamda[0])**0.5
		return SNR
	def calc_SNR_L(self,data):
		alpha = DataModel.alpha()
		sigma = np.min(LA.svd(true_response(data))[1])
		SNR = sigma/(scipy.stats.chi2.ppf(1-alpha,(np.asarray(data.P).shape[0])*(np.asarray(data.P).shape[1]))*data.lamda[0])**0.5
		return SNR
	def calc_SNR_phi_gauss(self,data):
		alpha = DataModel.alpha()
		Y = np.asarray(response(data))
		SNR = []
		for i in range(int(data.N)):
			SNR.append(LA.norm(Y[i,:])/(scipy.stats.chi2.ppf(1-alpha,int(data.M))*data.lamda[0])**0.5)
		return SNR

	def scale_lambda_SNR_L(self,data,SNR_L):
		alpha = DataModel.alpha()
		s = np.min(LA.svd(true_response(data))[1])
		lamda = s**2/(scipy.stats.chi2.ppf(1-alpha,np.size(data.P))*SNR_L**2)
		return lamda

	def scale_lambda_SNR_E(self,data,SNR_t):
		alpha = DataModel.alpha()
		s = np.min(LA.svd(true_response(data))[1])
		e = np.max(LA.svd(data.E)[1])
		e2 = s/SNR_t
		lamda = np.var(np.reshape(np.asarray(data.E.T),(np.size(data.E),1))*e2/e)*(np.size(data.E))/(np.size(data.E)-1)
#the value is different from Matlab version, so I change the formula to divolves the (N-1)
		return lamda
	def scale_lambda_SNRv(self,data,SNRv):
		alpha = DataModel.alpha()
		Y = np.asarray(response(data))
		lamda = []
		for i in range(int(data.N)):
			lamda.append(LA.norm(Y[i,:])/(scipy.stats.chi2.ppf(1-alpha,int(data.M))*(SNRv)**2))
		return lamda
#lack of irrepresentability function
