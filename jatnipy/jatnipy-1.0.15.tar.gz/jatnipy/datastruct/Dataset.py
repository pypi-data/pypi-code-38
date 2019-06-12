'''cannot write from 44-72'''
'''cannot write from 81-96'''
import numpy as np
import datetime
#from datastruct.Exchange import Exchange
from datastruct.Exchange import Exchange as E
from numpy import linalg as LA
import json, requests
from datastruct.Exchange_fetch import fetch
import scipy
from scipy import stats
from scipy.stats import chi2
from scipy.sparse import csr_matrix
import os
import re
from collections import namedtuple
from datastruct.obj_dict import obj_dict
import pandas as pd
from sklearn.linear_model import LinearRegression
_uri = "N10/Nordling-ID1446937-D20150825-N10-E15-SNR3291-IDY15968.json"
_database = "https://bitbucket.org/api/2.0/repositories/sonnhammergrni/gs-datasets/src/master/"
class Dataset():
	def __init__(self,data=None):
		if data == None:
			self.name = '' 
			self.network = ''
			self.P = []
			self.F = []
			self.F_covariance_variable = []
			self.E_covariance_variable = []
			self.F_covariance_element = []
			self.E_covariance_element = []
			self.Y = []
			self.E = []
			self.lamda = 0
			#self.SNR_L = 0 #remove the SNR_L
			self.nodes = ''
			self.description = ''
			self.N = 0
			self.M = 0
			self.created =	{
					'creator':'',
					'time':datetime.datetime.now().strftime('%s'),
					'id':'',
					'nexp':'',
					}
			self.tol = np.finfo(float).eps
			self.__model_eq__ = "X ~ -dot(P, pinv(A).T)"
		else:
			self.name = data['dataset'] 
			self.network = data['network']
			self.P = data['P']
			self.F = data['F']
			self.F_covariance_variable = data['cvP']
			sdY1 = pd.DataFrame(np.eye(int(data['N'])), index=data["Y"].index, columns=data["Y"].index)
			sdY2 = pd.DataFrame(data['sdY'], index=data["Y"].index, columns=data["Y"].columns)
			frames1_Y = [sdY1,sdY2]
			sdY_c_1 = pd.concat(frames1_Y,axis = 1)
			sdY3 = pd.DataFrame(np.asarray(data['sdY']).transpose(), index=data["Y"].columns, columns=data["Y"].index)
			sdY4 = pd.DataFrame(np.eye(int(data['M'])), index=data["Y"].columns, columns=data["Y"].columns)
			frames2_Y = [sdY3,sdY4]
			sdY_c_2 = pd.concat(frames2_Y,axis = 1)
			frames_Y = [sdY_c_1,sdY_c_2]
			self.E_covariance_element =  pd.concat(frames_Y,axis = 0)
			sdP1 = pd.DataFrame(np.eye(int(data['N'])), index=data["Y"].index, columns=data["Y"].index)
			sdP2 = pd.DataFrame(data['sdP'], index=data["Y"].index, columns=data["Y"].columns)
			frames1_P = [sdP1,sdP2]
			sdP_c_1 = pd.concat(frames1_P,axis = 1)	
			sdP3 = pd.DataFrame(np.asarray(data['sdP']).transpose(), index=data["Y"].columns, columns=data["Y"].index)
			sdP4 = pd.DataFrame(np.eye(int(data['M'])), index=data["Y"].columns, columns=data["Y"].columns)
			frames2_P = [sdP3,sdP4]
			sdP_c_2 = pd.concat(frames2_P,axis = 1)
			frames_P = [sdP_c_1,sdP_c_2]
			self.F_covariance_element = pd.concat(frames_P,axis = 0)
			self.E_covariance_variable = data['cvY']
			self.Y = data['Y']
			self.E = data['E']
			self.lamda = data['lambda']
			#self.SNR_L = data['SNR_L'] #remove the SNR_L
			names = pd.Series(data["names"], name="node")
			names.name = "node"
			self.nodes = names
			self.description = data['description']
			self.N = data['N']
			self.M = data['M']
			self.created =	data['created']
			self.tol = np.finfo(float).eps
			self.__model_eq__ = "X ~ -dot(P, pinv(A).T)"
		#for k, v in data:
		#	setattr(self, k, v)
	def Dataset(self,*args):
		data = Dataset()
		if len(args) > 0:
			for i in range(len(args)):
				if 'G' in args[i].__dict__:
					self.populate(data,args[i])
				
				##Experiment not do do for dataset
				elif 'P' in args[i].__dict__:
					newdata = args[i]
					self.populate(data,newdata)
					data.created['id'] = str(int(np.around(LA.cond(np.asarray(data.Y)-np.asarray(data.E))*10000)))
					#data.SNR_L = self.get_SNR_L(data) #remove the SNR_L
				##
			if 0:#ispc??
				data.created['creator'] = os.environ['HOME'][6:]
			else:
				data.created['creator'] = os.environ['HOME'][6:]
			self.setname(data)
		
		return data
	##start from this
	def get_interaction_format(self):
		X, y = self.Y.transpose()-self.E.transpose(),-self.P.transpose()+self.F.transpose()
		return X,y
	def get_interaction_matrix(self):
		#return self.get_interaction_format()[0]
		reg = LinearRegression().fit(self.get_interaction_format()[0],self.get_interaction_format()[1])
		return reg.coef_
	def get_static_gain_format(self):
		X, y  = self.P-self.F,self.Y-self.E
		return X,y
	def get_static_gain_matrix(self):
		reg = LinearRegression().fit(self.get_static_gain_format()[0],self.get_static_gain_format()[1])
		return reg.coef_
	def get_M(self,data):
		a = np.asarray(data.P)
		return a.shape[1]
	def get_N(self,data):
		b = np.asarray(data.P)
		return b.shape[0]
	
	def set_lamda(self,data,lamda):
		lamda = np.asarray(lamda)
		if not lamda.ndim == 1:
			lamda = np.transpose(lamda)
		if lamda.size == 1:
			lamda = [lamda,0]
		if lamda.size == data.N:
			lamda = [lamda,np.zeros((lamda.shape[0],lamda.shape[1]))]
		if not np.mod(len(lamda),2) == 0:
			print('Something is wrong with the size of lamda. Help!')
		data.lamda = lamda
	
	def get_SNR_L(self,data): ##97-103
		alpha = 0.01
		sigma1 = LA.svd(self.true_response(data))
		sigma = min(sigma1[1])
		SNR = sigma/(scipy.stats.chi2.ppf(1-alpha,self.get_N(data)*self.get_M(data))*data.lamda[0])**0.5
		#data.SNR_L = SNR #remove the SNR_L
		return SNR
	def Phi(self):
		#if isinstance(self,dict):
		#	data=obj_dict(self)
		p = np.transpose(self.Y)
		return p
	def Xi(self):
		#if isinstance(self,dict):
		#	data=obj_dict(self)
		x = -np.transpose(self.P)
		return x
	def Upsilon(data):
		#if isinstance(data,dict):
		#	data=obj_dict(data)
		u = np.transpose(data.E)
		return u
	def Pi(self):
		#if isinstance(self,dict):
		#	data=obj_dict(self)
		p = -np.transpose(self.F)
		return p
	def Psi(self):
		a=np.asarray(self.Phi())
		b=np.asarray(self.Xi())
		p = np.hstack((a,b))
		p1=pd.DataFrame(p)
		return p1
	def Omicron(self):
		#if isinstance(self,dict):
		#	self=obj_dict(self)
		a=np.asarray(self.Upsilon())
		b=np.asarray(self.Pi())
		o = np.hstack((a,b))
		o1=pd.DataFrame(o)
		return o1
	def setname(self,data,*args):
		if len(args) == 0:
			namestruct = data.created
		elif len(args) == 1:
			namestruct = args[0]
		if not isinstance(namestruct,dict):
			print('input argument must be name/value pairs in struct form')
		namer = data.created
		inpNames = list(namestruct.keys())
		optNames = namer.keys()
		for i in range(len(inpNames)):
			if inpNames[i] in optNames:
				namer['%s'%(inpNames[i])] = namestruct['%s'%(inpNames[i])]
		if not np.asarray(data.lamda).size:
			SNR_L = '0'
		else:
			SNR_L = str(int(np.around(self.get_SNR_L(data)*1000)))##SNR=0??
		data.name = namer['creator'] + '-ID' + re.findall('ID.*',data.network)[0][2:] + '-D' + datetime.datetime.now().strftime('%Y%m%d') + '-N' + str(np.asarray(data.P).shape[0]) + '-E' + str(np.asarray(data.P).shape[1]) + '-SNR' + str(SNR_L) + '-IDY' + namer['id']
		
		return data
	def get_names(self,data):
		names = data.nodes
		if not names:
			for i in range(int(data.N)):
				names[i] = 'G%2.0f'%i
		else:
			names = data.nodes
		return names
	def std(self,data):
		if isinstance(data,dict):
			data=obj_dict(data)
		if  np.asarray(data.lamda).size == 2:
			sdY = np.sqrt(np.asarray(data.lamda)[0])*np.ones((np.asarray(data.P).shape[0],np.asarray(data.P).shape[1]))
			sdY1 = np.eye(int(data.N))
			sdY2 = sdY
			sdY_c_1 = np.concatenate((sdY1,sdY2),axis = 1)
			sdY3 = sdY.transpose()
			sdY4 = np.eye(int(data.M))
			sdY_c_2 = np.concatenate((sdY3,sdY4),axis = 1)
			E_covariance_element= np.concatenate((sdY_c_1,sdY_c_2),axis = 0)
			sdP = np.sqrt(np.asarray(data.lamda)[1])*np.ones((np.asarray(data.P).shape[0],np.asarray(data.P).shape[1]))
			sdP1 = np.eye(int(data.N))
			sdP2 = sdP
			sdP_c_1 = np.concatenate((sdP1,sdP2),axis = 1)
			sdP3 = sdP.transpose()
			sdP4 = np.eye(int(data.M))
			sdP_c_2 = np.concatenate((sdP3,sdP4),axis = 1)
			F_covariance_element= np.concatenate((sdP_c_1,sdP_c_2),axis = 0)
		else:
			sdY = np.sqrt(np.asarray(data.lamda)[:int(data.N)-1])*np.ones((1,np.asarray(data.P).shape[1]))
			sdY1 = np.eye(int(data.N))
			sdY2 = sdY
			sdY_c_1 = np.concatenate((sdY1,sdY2),axis = 1)
			sdY3 = sdY.transpose()
			sdY4 = np.eye(int(data.M))
			sdY_c_2 = np.concatenate((sdY3,sdY4),axis = 1)
			E_covariance_element= np.concatenate((sdY_c_1,sdY_c_2),axis = 0)
		return E_covariance_element,F_covariance_element
	def scaleSNR(self,data,net,SNR):
		newdata =  self.Dataset(data,net)
		sY = LA.svd(self.true_response(newdata))[1]
		sE = LA.svd(newdata.E)[1]
		scale = 1/SNR*np.min(sY)/np.max(sE)
		newdata.lamda = np.dot(scale**2,newdata.lamda)
		newdata.E = scale*newdata.E
		return newdata
	def noise_normalization_scaling(self,data,*args):
		if isinstance(data,dict):
			data=obj_dict(data)
		print('This function is not fully reliable and should not be used without caution.')
		dim = 2
		if len(args) > 0:
			dim = args[0]
		norm_fun = 'std_normalize'
		if len(args) > 1 :
			norm_fun = args[1]
		
		if norm_fun == 'std_normalize':
			newdata = self.std_normalize(data,dim)
		elif norm_fun == 'range_scaling':
			newdata = self.range_scaling(data,dim)
		elif norm_fun == 'unit_length_scaling':
			newdata = self.unit_length_scaling(data,dim)
		sYo = LA.svd(self.response(data))[1]
		if np.count_nonzero(np.asarray(data.E)) != 0:
			sEo = LA.svd(data.E)[1]
			SNR = np.min(sYo)/np.max(sEo)
		else:
			alpha = 0.01
			sigma = np.min(sYo)
			SNR = sigma/(scipy.stats.chi2.ppf(1-alpha,D.get_N(data)*D.get_M(data))*data.lamda[0])**0.5
		sY = LA.svd(self.response(data))[1]
		if np.count_nonzero(np.asarray(data.E)) != 0:
			E = data.E*np.min(sY)/np.min(sYo)
			scale = np.max(LA.svd(E)[1])/np.max(sEo)
			newdata.lamda = np.dot(scale**2,newdata.lamda)
			newdata.E = E
		else:
			sigma = np.min(LA.svd(Yhat)[1])
			newdata.lamda = lamda
		newdata.F_covariance_variable = []
		newdata.E_covariance_variable = []
		E_covariance_element,F_covariance_element = self.std(newdata)
		self.setE_covariance_element(newdata,E_covariance_element)
		self.setF_covariance_element(newdata,_covariance_element)
		return newdata
	def std_normalize(self,data,*args):
		if isinstance(data,dict):
			data=obj_dict(data)
		if len(args) == 0:
			dim = 2
		else:
			dim = args[0]
		newdata = self.Dataset(data)
		Y = self.response(newdata)
		s1,s2= np.shape(Y)
		if dim == 2:
			s1 = 1
		elif dim == 1:
			s2 = 1
		s=s1,s2
		mu = np.mean(Y,axis = dim-1)
		sigma = np.std(Y,axis = dim-1)
		Mu = np.tile(np.reshape(mu,(np.size(mu),1)),(s1,s2))
		
		Sigma = np.tile(np.reshape(sigma,(np.size(sigma),1)),(s1,s2))
		
		Yhat = (Y - Mu)/Sigma
		newdata.Y = Yhat 
		newdata.E = np.zeros((np.asarray(Yhat).shape[0],np.asarray(Yhat).shape[1]))
		newdata.F_covariance_variable = []
		newdata.E_covariance_variable = []
		return newdata
	def range_scaling(self,data,*args):
		if isinstance(data,dict):
			data=obj_dict(data)
		dim = 2
		if len(args) > 0:
			dim = args[0]
		if len(args) > 1:
			rang = np.sort(args[1],axis = 0)
		newdata = self.Dataset(data)
		Y = self.response(data)
		s1,s2= np.shape(Y)
		if dim == 2:
			s1 = 1
		elif dim == 1:
			s2 = 1
		s=s1,s2
		mx = np.max(Y,axis = dim-1)
		mn = np.min(Y,axis = dim-1)
		mxmat = np.tile(np.reshape(mx,(np.size(mx),1)),(s1,s2))
		mnmat = np.tile(np.reshape(mn,(np.size(mn),1)),(s1,s2))
		Yhat = (Y-mnmat)/(mxmat - mnmat)
		newdata.Y = Yhat
		newdata.E = np.zeros((np.asarray(Yhat).shape[0],np.asarray(Yhat).shape[1]))
		newdata.F_covariance_variable = []
		newdata.E_covariance_variable = []
		return newdata
		
	def unit_length_scaling(self,data,*args):
		if isinstance(data,dict):
			data=obj_dict(data)
		dim = 2
		if len(args) > 0:
			dim = args[0]
		if len(args) > 1:
			rang = np.sort(args[1],axis = 0)
		newdata = self.Dataset(data)
		Y = self.response(data)
		s1,s2= np.shape(Y)
		if dim == 2:
			s1 = 1
		elif dim == 1:
			s2 = 1
		length = np.sqrt((np.sum(Y**2,axis = dim-1)))
		norm_mat = np.tile(np.reshape(length,(np.size(length),1)),(s1,s2))
		Yhat = np.true_divide(Y,norm_mat)
		newdata.Y = Yhat
		newdata.E = np.zeros((np.asarray(Yhat).shape[0],np.asarray(Yhat).shape[1]))
		newdata.F_covariance_variable = []
		newdata.E_covariance_variable = []
		return newdata


		
	def gaussian(self,data):
		data.N = self.get_M(data)
		data.M = self.get_N(data)
		if len(data.lamda) == 1:
			E = np.sqrt(data.lamda)*np.random.rand(data.N,data.M)
			F = np.zeros(data.M,data.N)
		elif len(data.lamda) == 2:
			E = np.sqrt(data.lamda[0])*np.random.rand(data.N,data.M)
			F = np.sqrt(data.lamda[1])*np.random.rand(data.N,data.M)
			
		elif len(data.lamda) == data.N:
			E = np.dot(np.transpose(np.sqrt(data.lamda[0])),np.random.rand(1,data.N))
			F = np.zeros(data.N,data.M)
		elif len(data.lamda) == 2*data.N:
			E = np.dot(np.transpose(np.sqrt(data.lamda[:data.N-1])),np.random.rand(1,data.N))
			F = np.dot(np.transpose(np.sqrt(data.lamda[data.N:])),np.random.rand(1,data.N))
		return E,F
	def setE_covariance_element(self,data,E_covariance_element):
		data.E_covariance_element = E_covariance_element
	def setF_covariance_element(self,data,F_covariance_element):
		data.F_covariance_element = F_covariance_element
	def cov(self,data):
		if len(data.lamda) == 1:
			E_covariance_variable1 = np.dot(data.lamda,np.eye(data.N))
			F_covariance_variable1 = np.dot(0,np.eye(data.N))
		elif len(data.lamda) == 2:
			E_covariance_variable1 = np.dot(data.lamda[0],np.eye(data.N))
			F_covariance_variable1 = np.dot(data.lamda[1],np.eye(data.N))
		elif len(data.lamda) == data.N:
			E_covariance_variable1 = np.diagflat(data.lamda)
			F_covariance_variable1 = np.dot(0,np.eye(data.N.shape[0]))
		elif len(data.lamda) == 2*data.N:
			E_covariance_variable1 = np.diagflat(data.lamda[:data.N-1])
			F_covariance_variable1 = np.diagflat(data.lamda[data.N:])
		E_covariance_variable = pd.DataFrame(E_covariance_variable1, index=np.transpose(data.Y).columns, columns=np.transpose(data.Y).columns)
		F_covariance_variable = pd.DataFrame(F_covariance_variable1, index=np.transpose(data.P).columns, columns=np.transpose(data.P).columns)
		return E_covariance_variable,F_covariance_variable
	def setcovY(self,data,E_covariance_variable):
		data.E_covariance_variable = E_covariance_variable
	def setcovP(self,data,F_covariance_variable):
		data.F_covariance_variable = F_covariance_variable
	def response(self,data,*args):
		n = np.asarray(data.P).shape[0]
		m = np.asarray(data.P).shape[1]
		if len(args) > 1  :
			if 'G' in args[0]:
				Net = args[0]
				X = np.matmul(np.asarray(Net.G),(np.asarray(data.P)))
				Y = X + np.asarray(data.E)[:,0:m]
			else:
				Y = np.asarray(data.Y)
		else:
			Y = np.asarray(data.Y)
		return Y
	def response1(self,data,*args):#for dictionary
		n = np.asarray(data['P']).shape[0]
		m = np.asarray(data['P']).shape[1]
		if len(args) > 1  :
			if 'G' in args[0]:
				Net = args[0]
				X = np.matmul(np.asarray(Net['G']),(np.asarray(data.P)))
				Y = X + np.asarray(data['E'])[:,0:m]
			else:
				Y = np.asarray(data['Y'])
		else:
			Y = np.asarray(data['Y'])
		return Y
	def true_response(self,data,*args): ##449-465
		D = Dataset()
		n = np.asarray(data.P).shape[0]
		m = np.asarray(data.P).shape[1]
		if len(args) > 1  :
			if 'G' in args[0]:
				net = args[0]
				X = np.matmul(np.asarray(net.G),(np.asarray(data.P) + np.asarray(data.F)[:,0:m]))
				return X
			else:
				X = np.asarray(data.Y) - np.asarray(data.E)[:,0:m]
			
		else:
			X = np.asarray(data.Y) - np.asarray(data.E)[:,0:m]	
		return X
	
	def without(self,data,i,*args):
		'''
		MyStruct = namedtuple('MyStruct', 'Y P E F')
		tmp = MyStruct(Y=np.delete(np.asarray(data.Y),i,1),P=np.delete(np.asarray(data.P),i,1),E=np.delete(np.asarray(data.E),i,1),F=np.delete(np.asarray(data.F),i,1))
		'''
		tmp={
			'Y':np.delete(np.asarray(data.Y),i,1),
			'P':np.delete(np.asarray(data.P),i,1),
			'E':np.delete(np.asarray(data.E),i,1),
			'F':np.delete(np.asarray(data.F),i,1),
			}
		
		sdY = np.asarray(data.E_covariance_element.head(data.N).iloc[:, int(data.N):int(data.N)+int(data.M)])
		if not sdY.size:
			tmp.sdY = np.delete(np.asarray(sdY),i,1)
		sdP = np.asarray(data.F_covariance_element.head(data.N).iloc[:, int(data.N):int(data.N)+int(data.M)])
		if not sdP.size:
			tmp.sdP = np.delete(np.asarray(sdP),i,1)
		if len(args) == 1:
			newdata = self.Dataset(data,net)
		else:
			newdata = self.Dataset(data)
		newdata = self.populate1(newdata,tmp)
		return newdata
	def eta(self,data,*args):
		D = Dataset()
		net = []
		if len(args) == 1:
			if 'G' in args[0]:
				net = args[0]
		Y = D.response(data,net)
		P = data.P
		etay = []
		etau = []
		for i in range(data.M):
			Ytemp = Y
			Ptemp = P
			Ytemp = np.delete(Ytemp,i,1)
			Ptemp = np.delete(Ptemp,i,1)
			ytemp = Y[:,i]
			ptemp = P[:,i]
			etay.append(np.sum(np.abs(np.dot(np.transpose(Ytemp),ytemp)),axis = 0))
			etau.append(np.sum(np.abs(np.dot(np.transpose(Ptemp),ptemp)),axis = 0))
		return etay,etau
	def w_eta(self,data,*args):
		net = []
		if len(args) ==1:
			if 'G' in args[0]:
				net = args[0]
		Y = self.response(data,net)
		P = data.P
		etay = []
		etau = []
		for i in range(data.M):
			tmpdata = self.without(data,i)
			yiU,dyiS,yiVt =LA.svd(self.response(tmpdata,net))
			yiV = np.transpose(yiVt)
			uiU,duiS,uiVt =LA.svd(tmpdata.P)
			uiV = np.transpose(uiVt)
			if len(dyiS) < tmpdata.M:
				dyiS = np.concatenate(dyiS,np.zeros(np.size(np.asarray(tmpdata['N']),1)-len(dyiS),1))
				duiS = np.concatenate(duiS,np.zeros(np.size(np.asarray(tmpdata['N']),1)-len(duiS),1))
			yv = np.true_divide(Y[:,i],LA.norm(Y[:,i],2))
			uv = np.true_divide(P[:,i],LA.norm(P[:,i],2))
			yg = np.true_divide(np.dot(np.transpose(dyiS),np.abs(np.dot(np.transpose(yiU),yv))),np.sum(dyiS,axis=0))
			etay.append(yg)
			ug = np.true_divide(np.dot(np.transpose(duiS),np.abs(np.dot(np.transpose(uiU),uv))),np.sum(duiS,axis=0))
			etau.append(ug)
		return etay,etau
	def etay(self,data):
		#D = Dataset(data)
		eta = self.eta(data)[0]
		return eta
	def etau(self,data):
		#D = Dataset()
		eta = self.eta(data)[1]
		return eta
	##should add some context for the following function
	'''
	def include(data,*args):
		if len(args) == 1:
			etaLim = args[0]
		if 0: #what is exist??
			sY = LA.svd(response(data))[1]
			sP = LA.svd(data['P']+data['F'])
			included = np.logical_and((np.asarray(data['etay'])>=etaLim),(data['etau']>=etaLim))
		elif 1: #what is exist??
			included = np.logical_and((np.asarray(data['etay'])>=etaLim[0]),(data['etau']>=etaLim[1]))
		return included
	'''
	'''
	def bootstrap(self,data,*args):
		if len(args) == 1:
			boots = args[0]
		else:
			bb = []
			jj = np.cumsum(np.sum(data.P,axis = 1))
			jj = np.concatenate((jj,jj[-1]+1),axis = None)
			bb.append(np.random.randint(1,jj[0],size=(1,1)))
			for dd in range(len(jj)-1):
				bb.append(np.random.randint(jj[dd]+1,jj[dd+1],size=(1,1)))
		## bbappend would be nothing because 1 not bigger than jj[0]  
			##boots use the np.concatenate to append column
		#return jj
	'''
	'''
	def shuffle(data,*args):
		tmpdata = data
		for i in range(data.M):
			shuf = np.random.permutation(int(data.N))
			#tmpdata.Y use the np.concatenate
	'''
	def populate(self,data,inpu):
		#if not isinstance(inpu,dict):#have many condictions
		#	error('Needs to be a dict...') #modify
		inputnames = list(vars(inpu).keys())
		names = vars(data).keys()
		for i in range(len(inputnames)):
			if inputnames[i] in names:
				data.__dict__['%s'%(inputnames[i])] = inpu.__dict__['%s'%(inputnames[i])]
		
		return data
	def populate1(self,data,inpu):
		#if not isinstance(inpu,dict):#have many condictions
		#	error('Needs to be a dict...') #modify
		inputnames = list(inpu.keys())
		names = vars(data).keys()
		for i in range(len(inputnames)):
			if inputnames[i] in names:
				data.__dict__['%s'%(inputnames[i])] = inpu['%s'%(inputnames[i])]
		
		return data
	def save(self,obj,savepath,fending,*args):
		#E = Exchange()
		E.save(obj,savepath,fending)
	def load(self,savepath,name,fending,*args):
		E = Exchange()
		return 	E.load(savepath,name,fending)
	def Load(*args):
		#directurl,baseurl,version,type,N,name,filelist,filetype
		#options=['','https://bitbucket.org/api/1.0/repositories/sonnhammergrni/gs-networks/raw/','master','random','10','','0',]
		#options={
		#	'directurl':'',
		#	'baseurl':'https://bitbucket.org/api/1.0/repositories/sonnhammergrni/gs-networks/raw/',
		#	'version':'master',
		#	'type':'random',
		#	'N':'10',
		#	'name':'',
		#	'filelist':'0',
		#	'filetype':'',
		#	}
		#E=Exchange()
		if len(args) != 0:
			try:
				if len(args)==1:
					if args[0] == 'test':
						obj_data = E.Load(_uri,_database)
					#default_file = args[0]
					#obj_data = E.fetch(options,default_file)
					else:
						obj_data = E.Load(args[0])
				elif len(args)>1:
					try:
						obj_data = E.Load(args[0],wildcard='%s'%(args[1]))
					except:
						obj_data = E.Load(args[0],args[1])				
#from this to modify		
				if 'P' in obj_data:
					data = obj_data
					names = pd.Series(data["names"], name="node")
					names.name = "node"
					M = data["M"]
					N = data['N']
					samples = pd.Series(["S" + str(i + 1) for i in range(M)], name="sample")
					data['Y'] = pd.DataFrame(data["Y"], index=names, columns=samples)
					data['P'] = pd.DataFrame(data["P"], index=names, columns=samples)
					data['E'] = pd.DataFrame(data["E"], index=names, columns=samples)
					data['F'] = pd.DataFrame(data["F"], index=names, columns=samples)
					data['sdY'] = pd.DataFrame(data['sdY'], index=data["Y"].index, columns=data["Y"].columns)
					data['sdP'] = pd.DataFrame(data['sdP'], index=data["P"].index, columns=data["P"].columns)
					data['cvY'] = pd.DataFrame(data['cvY'], index=names, columns=names)
					data['cvP'] = pd.DataFrame(data['cvP'], index=names, columns=names)
					data['lambda'] = pd.Series(np.array([np.array(i) for i in data["lambda"]]), index=["E_variance", "F_variance"])
					return data
				elif isinstance(obj_data,dict):
					print('This is not a dataset')
				else:
					return obj_data
			except:
				pass		
				#default_file = 'Nordling-D20100302-random-N10-L25-ID1446937.json'
				#obj_data = E.fetch(options,default_file)
				#net = obj_data
				#names = pd.Series(net["names"], name="node")
				#names.name = "node"
				#net['A'] = pd.DataFrame(net["A"], index=names, columns=names)
				#net['G'] = pd.DataFrame(net["G"], index=names, columns=names)			
				#return net
		else:
			#default_url =  options['baseurl']+options['version']+'/'+options['type']+'/'+'N'+str(options['N'])+'/'
			#obj_data = E.fetch(options,default_url)		
			#net = obj_data	
			#return net
			pass
'''
	def fetch(self,*args):
		options={
			'directurl':'',
			'baseurl':'https://bitbucket.org/api/1.0/repositories/sonnhammergrni/gs-datasets/raw/',
			'version':'master',
			'N':'10',
			'name':'Nordling-ID1446937-D20150825-N10-E15-SNR3291-IDY15968',
			'filetype':'.json',
			}
		E=Exchange()
		if len(args) != 0:
			try:
				default_file = args[0]
				obj_data = E.fetch(options,default_file)
				data = obj_data
				names = pd.Series(data["names"], name="node")
				names.name = "node"
				M = data["M"]
				N = data['N']
				samples = pd.Series(["S" + str(i + 1) for i in range(M)], name="sample")
				data['Y'] = pd.DataFrame(data["Y"], index=names, columns=samples)
				data['P'] = pd.DataFrame(data["P"], index=names, columns=samples)
				data['E'] = pd.DataFrame(data["E"], index=names, columns=samples)
				data['F'] = pd.DataFrame(data["F"], index=names, columns=samples)
				data['sdY'] = pd.DataFrame(data['sdY'], index=data["Y"].index, columns=data["Y"].columns)
				data['sdP'] = pd.DataFrame(data['sdP'], index=data["P"].index, columns=data["P"].columns)
				data['cvY'] = pd.DataFrame(data['cvY'], index=names, columns=names)
				data['cvP'] = pd.DataFrame(data['cvP'], index=names, columns=names)
				data['lambda'] = pd.Series(np.array([np.array(i) for i in data["lambda"]]), index=["E", "F"])
				return data
			except:
				default_file = 'Nordling-ID1446937-D20150825-N10-E15-SNR3291-IDY15968.json'
				obj_data = E.fetch(options,default_file)
				data = obj_data
				
				names = pd.Series(data["names"], name="node")
				names.name = "node"
				M = data["M"]
				N = data['N']
				samples = pd.Series(["S" + str(i + 1) for i in range(M)], name="sample")
				data['Y'] = pd.DataFrame(data["Y"], index=names, columns=samples)
				data['P'] = pd.DataFrame(data["P"], index=names, columns=samples)
				data['E'] = pd.DataFrame(data["E"], index=names, columns=samples)
				data['F'] = pd.DataFrame(data["F"], index=names, columns=samples)
				data['sdY'] = pd.DataFrame(data['sdY'], index=data["Y"].index, columns=data["Y"].columns)
				data['sdP'] = pd.DataFrame(data['sdP'], index=data["P"].index, columns=data["P"].columns)
				data['cvY'] = pd.DataFrame(data['cvY'], index=names, columns=names)
				data['cvP'] = pd.DataFrame(data['cvP'], index=names, columns=names)
				data['lambda'] = pd.Series(np.array([np.array(i) for i in data["lambda"]]), index=["E", "F"])
				
				return data
		else:
			default_url =  options['baseurl']+options['version']+'/'+'N'+str(options['N'])+'/'
			obj_data = E.fetch(options,default_url)		
			data = obj_data
			return data
'''	









