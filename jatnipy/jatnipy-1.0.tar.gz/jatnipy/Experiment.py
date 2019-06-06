import numpy as np
from numpy import linalg as LA
import scipy
from scipy import stats
from scipy.stats import chi2
from numpy import random
class Experiment():
	def __init__(self):
		self.A = [] 
		self.G = []
		self.P = []
		self.Yinit = []
		self.E = []
		self.F = []
		self.lamda = [1,0]
		self.alpha = 0.05
		self.nExp = np.inf
		self.mag = 1
		self.maxmag = 2
		self.SignalThreshold = 1
		self.tol = np.finfo(float).eps
		self.nnzP = 0
		self.SNR = []
		self.N = 0
		self.M = 0
	def Experiment(self,*args):
		data = Experiment()
		if len(args) == 0:
			print('Make sure to supply a Network before further experimentation')
		if len(args) > 0 :
			data.A = args[0]
		if len(args) > 1:
			args[1] = np.asarray(args[1],dtype = float)
			if isinstance(args[1],np.ndarray):
				data.P = args[1]
			else:
				print('Perturbation needs to be of class double')
		if len(args) > 2:
			args[2] = np.asarray(args[2],dtype = float)
			if isinstance(args[2],np.ndarray):
				data.Yinit = args[2]
			else:
				print('Initial response needs to be of type double')
		return data
	def set_A(self,data,net):
		if not data.A:
			data = np.asarray(data,dtype = float)
			if isinstance(net,np.ndarray):
				data.A = net
			elif 'G' in net:
				data.A = net['A']
			else:
				print('Network input argument must be a of double array or Network type')
			data.G = -LA.pinv(data.A)
			tmp = np.zeros((data.A.shape[0]-1,1))
			data.P = np.insert(tmp,0,1)
			if not data.nnzP:
				data.nnzP = data.N
		else:
			print('True A already set, will not change it!')
	def get_N(self,data):
		N = data.A.shape[0]
		return N
	def get_M(self,data):
		M = data.P.shape[1]
		return M
	def set_alpha(self,data,SignificanceLevel):
		if SignificanceLevel > 1 or SingnificanceLevel < 0:
			print('Significance level must be in the range [0,1].T')
		data.alpha = SignificanceLevel
	def Pinit(self,data,P):
		data.P = P
	def set_Yinit(self,data,Yinit):
		data.Yinit = Yinit
	def set_lambda(self,lamda):
		if not lamda.ndim == 1:
			lamda = lamda.T
		if A.size == 1:
			lamda = np.insert(lamda,-1,0)
		if A.size == data.P.shape[0]:
			lamda = np.insert(A,-1,np.zeros(A.size))
		if not np.mod(len(lamda),2) == 0:
			print('Something is wrong with the size of lambda. Help!')
		data.lamda = lamda
	def set_SignalThreshold(self,data,SignalThreshold):
		if SignalThreshold <= 0 :
			print('SignalThreshold must be > 0')
		data.SignalThreshold = SignalThreshold
	def set_nExp(self,data,M):
		if np.remainder(M,1) != 0 or M < 1:
			print('# experiments must be a positive integer')
		data.nExp = M
	def terminate(self,data,*args):
		TF = false
		if data.P.shape[1] >= data.nExp:
			TF = True
			return TF
		if len(args) == 2:
			condition = args[0]
			if condition is 'ST':
				s = LA.svd(self.noiseY(data))[1]
				if (np.min(s) > data.SignalThreshold) and (data.P.shape[1] >= data.N):
					TF = True
			elif condition is 'SCT':
				k = data.P.shape[1]
				s = np.divide(LA.svd(self.noiseY(data))[1],(scipy.stats.chi2.ppf(1-data.alpha,np.dot(data.N,k))*self.var(data))**0.5)
				if (np.min(s) > data.SignalThreshold) and (data.P.shape[1] >= data.N):
					TF = True
		return TF
	def trueY(self,data):
		pre = data.Yinit.shape[1] 
		Y = np.concatenate(data.Yinit,np.dot(data.G,data.P[:,pre:]),axis = 1)
		return Y
	def noiseY(self,data):
		pre = data.Yinit.shape[1]
		while data.E.shape[1] < data.P.shape[1]:
			self.gaussian(data)
		Y = np.concatenate(data.Yinit,np.dot(data.G,data.P[:,pre:]-data.F[:,pre:data.P.shape[1]]+data.E[:,pre:data.P.shape[1]]),axis = 1)
		return Y
	def noiseP(self,data):
		while data.F.shape[1] < data.P.shape[1]:
			self.gaussian(data)
		P = data.P-data.F[:,:data.P.shape[1]]
		return P
	def var(data):
		if size(data.lamda) == 2:
			vY = np.dot(data.lamda[0],np.ones(size(data.P)))
		else:
			vY = data.lamda[:data.N].T*np.ones((1,data.P.shape[1]))
	def sparse(self,data,*args):
		if len(args) == 1:
			nnzP = args[0]
		else:
			nnzP = data.nnzP
		p = data.P[:,]
		nZero = data.N-nnzP
		sortedValues = np.sort(np.abs(p[:]))
		sortIndex = np.argsort(np.abs(p[:]))
		minIndex = sortIndex[:nZero]
		p[minIndex] = 0
		data.P[:,] = p
	def initE(self,data,E):
		data.E = E
	def initF(self,data,F):
		data.F = F
	def gaussian(self,data):
		if size(data.lamda) == 1:
			data.E = np.concatenate(data.E,(data.lamda)**0.5*np.random.rand(data.N,1),axis = 1)
			data.F = np.concatenate(data.F,np.zeros((data.N,1)),axis = 1)
		elif size(data.lamda) == 2:
			data.E = np.concatenate(data.E,(data.lamda[0])**0.5*np.random.rand(data.N,1),axis = 1)
			data.F = np.concatenate(data.E,(data.lamda[1])**0.5*np.random.rand(data.N,1),axis = 1)
		elif size(data.lamda) == data.N:
			data.E = np.concatenate(data.E,(data.lamda.T)**0.5*np.random.rand(data.N,1),axis = 1)
			data.F = np.concatenate(data.F,np.zeros((data.N,1)),axis = 1)
		elif size(data.lamda) == data.N*2:
			data.E = np.concatenate(data.E,(data.lamda[:data.N].T)**0.5*np.random.rand(data.N,1),axis = 1)
			data.F = np.concatenate(data.F,(data.lamda[data.N:].T)**0.5*np.random.rand(data.N,1),axis = 1)
	def get_SNR(self,data):
		if not data.SNR:
			SNR = np.min(LA.svd(self.trueY(data))[1])/np.max(LA.svd(data.E)[1])
		else:
			SNR = data.SNR
		return SNR
	def scaleSNR(self,data,SNR):
		self.noise(data)
		sY = LA.svd(self.trueY(data))[1]
		sE = LA.svd(data.E)[1]
		scale = 1/SNR*np.min(sY)/np.max(sE)
		data.lamda = scale**2*data.lamda
		data.E = scale*data.E
	def scaleSNR(data,SNRm,*args):
		lambdaOld = data.lamda
		if len(args) == 1:
			nvar = args[0]
		else:
			nvar = data.N*data.M
		sY = LA.svd(self.trueY(data))[1]
		lamda = np.min(sY)**2/(scipy.stats.chi2.ppf(1-data.alpha,nvar)*SNRm**2)
		data.lamda = lamda
		data.E = lamda[0]/lambdaOld[0]*data.E
	def scaleSNRm(data,SNRm,*args):
		print('hello there')
	def signify(self,data):
		data.P = np.dot(data.mag,self.sign(data.P))
	def SVDE(self,data):
		k = data.P.shape[1]
		if k+1 <= data.N:
			pass
			#what is GramSch
			#data.P[:,k+1] = np.dot(data.mag,)
		if k>0:
			u,s1,v = LA.svd(self.noiseY(data))
			v = v.transpose()
			s = np.zeros((s1.shape[0],s1.shape[0]))
			for i in range(len(s)):
				s[i][i]=s1[i]
			if np.min(np.diag(s)) < data.SignalThreshold:
				data.P[:k+1] = 0
				for j in range(np.min(len(s))):
					if s[j][j] > data.SignalThreshold:
						data.P[:,k+1] = data.P[:,k+1] + np.dot(np.dot(data.SignalThreshold/s[j][j],data.P[:,:k]),v[:,j])
	def BCSE(self,data):
		k = data.P.shape[1]
		if k+1 <= data.N:
			pass
			#
			#
		else:
			uu,su1,vu = LA.svd(self.noiseY(data))
			vu = vu.transpose()
			su = np.zeros((su1.shape[0],su1.shape[0]))
			for i in range(len(su)):
				su[i][i]=su1[i]			
			u,s1,v = np.divide(LA.svd(self.noiseY(data)),(scipy.stats.chi2.ppf(1-data.alpha,np.dot(data.N,k))*self.var(data))**0.5)
			v = v.transpose()
			s = np.zeros((s1.shape[0],s1.shape[0]))
			for i in range(len(s)):
				s[i][i]=s1[i]
			data.P[:,k+1] = np.zeros((data.N,1))
			for j in range(data.N):
				if s[j][j] < data.SignalThreshold:
					data.P[:,k+1] = data.P[:,k+1] + np.dot(np.dot(np.dot(data.mag,np.divide(data.SignalThreshold,s[j][j])),data.P[:,:k]),vu[:,j])
	def BCSEE(self,data):
		k = data.P.shape[1]
		uu,su1,vu = LA.svd(self.noiseY(data))
		vu = vu.transpose()
		su = np.zeros((su1.shape[0],su1.shape[0]))
		for i in range(len(su)):
			su[i][i]=su1[i]	
		u,s1,v = np.divide(LA.svd(self.noiseY(data)),(scipy.stats.chi2.ppf(1-data.alpha,np.dot(data.N,k))*self.var(data))**0.5)
		v = v.transpose()
		s = np.zeros((s1.shape[0],s1.shape[0]))
		for i in range(len(s)):
			s[i][i]=s1[i]
		data.P[:,k+1] = np.zeros((N,1))
		for j in range(data.N):
			data.P[:,k+1] = data.P[:,k+1] + np.dot(np.dot(np.dot(data.mag,data.SignalThreshold/s[j][j]),data.P[:,:k]),vu[:,j])
	def BSVE(self,data):
		k = data.M
		if k+1 <= data.N:
			pass
			#
			#
		else:
			data.P[:,k+1] = np.dot(data.SignalThreshold/s[data.N][data.N],data.P[:,:k]*v[:,data.N])
	def RANDPE(self,data):
		temp = np.random.rand(data.G.shape[1],1)
		k = data.P.shape[1]
		if k+1 <= data.N:
			pass
			#temp = temp
		#if any
			#data.P
		else:
			data.P[:,k+1] = np.divide(np.dot(data.mag,temp),LA.norm(temp,np.inf))
	def BHCSE(self,data):
		k = data.P.shape[1]
		if k+1 <= data.N:
			pass
			#
			#
		else:
			uu,su1,vu = LA.svd(self.noiseY(data))
			vu = vu.transpose()
			su = np.zeros((su1.shape[0],su1.shape[0]))
			for i in range(len(su)):
				su[i][i]=su1[i]

			u,s1,v = np.divide(LA.svd(self.noiseY(data)),(scipy.stats.chi2.ppf(1-data.alpha,np.dot(data.N,k))*self.var(data))**0.5)
			v = v.transpose()
			s = np.zeros((s1.shape[0],s1.shape[0]))
			for i in range(len(s)):
				s[i][i]=s1[i]
			data.P[:,k+1] = np.zeros((data.N,1))
			for j in range(data.N):
				if s[j][j] < data.SignalThreshold:
					data.P[:,k+1] = data.P[:,k+1] + np.dot(np.dot(np.dot(data.mag,data.SignalThreshold/s[j][j]),data.P[:,:k]),vu[:,j])
			#if any
				for j in range(1,data.N):
					data.P[:,k+1] = data[:,k+1] + np.dot(np.dot(np.dot(data.mag,data.SignalThreshold/s[j][j]),data.P[:,:k]),vu[:,j])
			















'''
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 19:30:14 2018

@author: ap932
"""
import numpy as np
from numpy import linalg as LA
class Experiment():
    def __init__(self,A,G,P,Yinit,E,F,nnzp):
        self._A = A
        self._G = G
        self._P = P
        self._Yinit = Yinit
        self._E = E
        self._F = F
        
        self.lamda = [1,0]
        self.alpha = 0.05
        self.nExp = np.inf
        self.mag = 1
        self.maxmag = 2
        self.SignalThreshold = 1
        self.tol = np.finfo(float).eps
        self.nnzP
        self.SNR = []
        
        self._N
        self._M
        
    def Experiment(*args):
        if len(args)==0:
            #warn
        if len(args)>0:
            data.A = args[0]
        if len(args)>1:
            if isinstance(args[1],'double'):
                data.P = args[1]
            else:
                #error
        if len(args)>2:
            if isinstance(args[2],'double'):
                data.Yinit = args[2]
            else:
                #error
    def setA(data,net):
        if len(data.A)==0:
            if isinstance(net,'double'):
                data.A = net
            elif isinstance(net,'Network'):
                data.A =net.A
            else:
                #error
            data.G = -np.linalg.svd(data.A, full_matrices=True)
            #data.P =
            if len(data.nnzp)==0:
                data.nnzp = data.N
         else:
             #warning
    def getN(data):
        A=data.A
        N=A.shape(0)
    def getM(data):
        P=data.P
        M=P.shape(1)
    def setalpha(data,SignifivanceLevel):
        if SignifivanceLevel >1 || SignficanceLevel <0:
            #error
        data.alpha = SignificanceLevel
    def Pinit(data.P):
        data.P = P
    def detYinit(data,Yinit):
        data.Yinit = Yinit
    def setlamda(data,lamda):
        if lamda.shape(0)==1: #lamba should be numpy array
            lamda = np.transpose(lamda)
        if np.prod(lamda.shape)==1: #lamba should be numpy array
            lamda = lamda.append(0)
        if np.prod(lamda.shape)==data.N #lamba should be numpy array
            lamda = lamda.append(np.zeros(lamda.size))
        if not len(lamda)%2 ==0:
            sys.exit('Something is wrong with the size of lambda. Help!')
        data.lamda =lamda
    def setSignalThreshold(data,SignalThreshold):
        if SignalThreshold <=0:
            #error
        data.SignalThreshold=SignalThreshold
    def setnExp(data,M):
        if remainder(M,1)!=0 || M<1:
            #error
        data.nExp = M
    def terminate(data,*args):
        TF = False
        if data.P.shape(1)>= data.nExp:
            TF = True
            return TF
        if len(*args)==2:
            condition = args[0]
            if condition == 'ST':
                s = np.linalg.svd(noiseY.data, full_matrices=True)
                if (np.amin(s)>data.SignalThreshold) && (data.P.shape(1) >=data.N)
                    TF = True
                elif condition == 'SCT'
                    k = data.P.shape(1)
                    #s = np.divide(np.linalg.svd(noiseY.data, full_matrices=True),np.sqrt())
                    if (np.amin(s)>data.SignalThreshold) && (data.P.shape(1) >= data.N):
                        TF =True
    def trueY(data):
        pre = data.Yinit.shape(1)+1
        #Y =
    
    def noiseY(data):
        pre = data.Yinit.shape(1)+1
        while data.E.shape(1) < data.P.shape(1):
            #gaussian(data)
        #Y=[data.Yinit]
    def noiseP(data):
        while data.F.shape(1) < data.P.shape(1):
            gaussian(data)
        #P =
    def var(data):
        if size(data.lamda)==2:
            #vY=
        else:
            #vY=
    def sparse(data,*args):
        if len(*args) == 2:
            nnzP = args[0]
        else:
            nnzP = data.nnzp
        #p=data.P
        nZero = data.N-nnzP
        #[]
        #minIndex
        #p(minIndex)=0
        #data.P
    def initE(data,E):
        data.E = E
    def initF(data,F):
        data.F=F
    def gassian(data):
        if size(data.lamda) == 1:
            #data.E = 
            #data.F = 
        elif size(data.lamda) == 2:
            #data.E = 
            #data.F = 
        elif size(data.lamda) == data.N:
            #data.E = 
            #data.F = 
        elif size(data.lamda) == 2*data.N:
            #data.E = 
            #data.F = 
    def getSNR(data):
        if len(data.SNR):
            #SNR = np.amin(np.linalg,svd())
        else:
            data.SNR
    def scaleSNR(data,SNR):
        noiseY(data)
        sY = np.linalg.svd(trueY(data), full_matrices=True)
        sE = np.linalg.svd(data.E, full_matrices=True)
        #scale = 1/SNR*
        data.lamda = scale**2data.lamda
        data.E = scale*data.E
    def scaleSNRm(data,SNRm,*args):
        lamdaOld = data.lamda
        if len(*args)==1:
            nvar = args[0]
        else:
            #nvar = 
        sY = np.linalg.svd(trueY(data), full_matrices=True)
        #lamda =
        data.lamda = lamda
        #data.E = 
    def scaleSNRm(data,SNRm,*args):
        'hello there'
    def signify(data):
        data.P =data.mag*sign(data.P)
    def SVDE(data):
        k = data.P.shape(1)
        if k+1 <= data.N:
            #newdir
            #data.P
        if k >0:
            [u,s,v] = np.linalg.svd(trueY(data), full_matrices=True)
            if np.amin(np.diag(s)) < data.SignalThreshold:
                #data.P
                #for j in range(0):
                    #if
                        #data.P
    def BCSE(data):
        k = size(data.P.shape[1]
        if k+1 <= data.N:
            #newdir
            #data.P
        else:
            #[uu,su,vu] = np.linalg.svd(, full_matrices=True)
            #data.P
            for j in range(0:(data.N)-1):
                #if
                    #data.P
                    
    def BCSEE(data):
        k = data.P.shape(1)
        [uu,su,vu] = np.linalg.svd(noiseY(data), full_matrices=True)
        #[u,s,v]
        #data.P
        for j in range(0:(data.N)-1):
    def BSVEE(data):
        k = data.M
        if k+1 <= data.N:
            #newdir = 
            #data.P
        else:
            [u,s,v] = np.linalg.svd(noiseY(data), full_matrices=True)
            #data.P
            for j in range(0,(data.N)-1):
                #data.P
    def PSVE(data):
        k = data.M
        if k+1 <= data.N:
            #newdir
            #data.P
        else:
            [u,s,v] = np.linalg.svd(noiseY(data), full_matrices=True)
            if np.amin(np.diag(s))<data.SignalThreshold:
                #data.P
    def PSVEE(data):
        k = data.M
        if k+1 <= data.N:
            #newdir
            #data.P
        else:
            [u,s,v] = np.linalg.svd(noiseY(data), full_matrices=True)
            #data.P
    def RANDPE(data):
        #temp =randn
        k = data.P.shape(1)
        if k+1 <= data.N:
            #temp = temp
        
        #if
            #
        else:
            #
            
    def BHCSE(data):
        k = data.P.shape(1)
        if k+1 <= data.N:
            #newdir = 
            #data.P
        else:
            [uu,su,vu] = np.linalg.svd(noiseY(data), full_matrices=True)
            #[u,s,v]=
            #data.P
            for j in range(0,(data.N)-1):
                #if s
                    #data.P
            #if any
                for j in range(1,N-1):
                    #data.P
                    
                    
'''               
                    
