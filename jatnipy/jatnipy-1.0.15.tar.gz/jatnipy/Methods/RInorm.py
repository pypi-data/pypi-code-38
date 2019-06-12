import scipy
from scipy import stats
from scipy.stats import chi2
import numpy as np
from numpy import linalg as LA

import copy
class RInorm():
	def RInorm(self,*args):
		R = RInorm()
		alpha = 0.05 
		LamPhi = 1
		LamXi = 1
		Xi = []
		alternative =0
	
		if len(args)<1:
			print('NordronAB:RInorm:InputNumberError'+','+'Too few input arguments. At least the regressor matrix must be supplied.')
		else:
			Phi = args[0]
			if len(args)>1:
				Xi = args[1]
				if len(args) >2:
					LamPhi = args[2]
					if len(args) >3:
						LamXi = args[3]
						if len(args)>4:
							alpha = args[4]
							if len(args)>5:
								alternative = args[5]
	

		if not len(Xi) == 0:
			Phi = np.asarray(Phi)
			Xi = np.asarray(Xi)
			if Phi.shape[0] != Xi.shape[0]:
				print('NordronAB:RInorm:NumberOfRowsError'+','+'The number of row in the regressand matrix does not match the number of rows in the regressor matrix.')
	
		LamPhi = np.asarray(LamPhi)
		Phi = np.asarray(Phi)
		if LamPhi.shape != Phi.shape:
			if LamPhi.size == 1:
				LamPhi = LamPhi*np.ones(Phi.shape)
			elif LamPhi.size == Phi.shape[1]:
				LamPhi = np.dot(np.ones(Phi.shape[0],1),LamPhi.reshape(1,Phi.shape[1]))
			else:
				print('NordronAB:RInorm:VarianceMatrixError'+','+'The variance matrix of the regressors has the wrong size. It should have the same size as Phi.')

	
	
		E= LamPhi<0
	
		if 1 in E:
			print('NordronAB:RInorm:VarianceMatrixError'+','+'Some element of the variance matrix of the regressors is negative.')
	
		if not len(Xi) == 0:
			if LamXi.shape != Xi.shape:
				if LamXi.size == 1:
					LamXi =LamXi*np.ones(Xi.shape)
				elif LamXi.size == Xi.shape[1]:
					LamXi = np.dot(np.ones(Xi.shape[0],1),LamXi.reshape(1,Xi.shape[1]))
				else:
					print('NordronAB:RInorm:VarianceMatrixError'+','+'The variance matrix of the regressands has the wrong size. It should have the same size as Xi.')
		
			F= LamXi<0
			if 1 in F:
				print('NordronAB:RInorm:VarianceMatrixError'+','+'Some element of the variance matrix of the regressors is negative.')	
		
		if alpha >1 or alpha < 0:
			print('NordronAB:RInorm:RangeError'+','+'The significance level is outside of its range [0,1].')
		PhiS = np.divide(Phi,(scipy.stats.chi2.ppf(1-alpha,Phi.size)*LamPhi)**0.5)
	
	
		if not len(Xi) == 0:
			XiS = np.divide(Xi,(scipy.stats.chi2.ppf(1-alpha,Xi.size)*LamXi)**0.5)
			if alternative == 2:
				Psi = np.concatenate((PhiS,XiS), axis=1)
				#no condition of vargout4 can change the if
				if 1:
					n = np.min(Psi.shape)
					UPsi,SPsi,VPsi = np.linalg.svd(Psi)
				
					VPsi = VPsi.transpose()
					SPsi = np.zeros((SPsi1.shape[0],SPsi1.shape[0]))
				
					for i in range(len(SPsi)):
						SPsi[i][i]=SPsi1[i]
					PsiSingulars = np.concatenate((Phi,Xi), axis=1) - np.dot(np.dot(SPsi[n,n],UPsi[:,n]),VPsi[:,n].transpose())*np.concatenate(((scipy.stats.chi2.ppf(1-alpha,Phi.shape[0]*Phi.shape[1])**0.5)*LamPhi,(scipy.stats.chi2.ppf(1-alpha,Xi.shape[0]*Xi.shape[1])**0.5)*LamXi), axis=1)
					del UPsi
					del VPsi
					SPsi = np.diag(SPsi)
				else:
					SPsi = LA.svd(Psi)[1]
				Gamma = SPsi[n]
			elif alternative == 1:
				n = LA.matrix_rank(np.concatenate((PhiS,XiS), axis=1))
				if n == PhiS.shape[1] + Xis.shape[1]:
					n = n-1
				for j in range(Phi.shape[1]):				
					Psi = np.concatenate((PhiS,XiS), axis=1)
					Psi[:,j] = []	
					if 1:
						Psi0 = np.concatenate((Phi,Xi), axis=1)
						Psi0[:,j] = []
						W0 = np.concatenate(((scipy.stats.chi2.ppf(1-alpha,Phi.shape[0]*Phi.shape[1])**0.5)*LamPhi,(scipy.stats.chi2.ppf(1-alpha,Xi.shape[0]*Xi.shape[1])**0.5)*LamXi), axis=1)
						W0[:,j] = []
						UPsi,SPsi1,VPsi = np.linalg.svd(Psi)
					
						VPsi = VPsi.transpose()
						SPsi = np.zeros((SPsi1.shape[0],SPsi1.shape[0]))
						for i in range(len(SPsi)):
							SPsi[i][i]=SPsi1[i]
						PsiSing = Psi0 - np.dot(SPsi[n,n],UPsi[:,n].T)*W0
						del UPsi
						del VPsi
						SPsi = np.diag(SPsi)
						PsiSingulars[:,:,1,j] = PsiSing
					else:
						SPsi = LA.svd(Psi)[1]
					Gamma[i,j] = SPsi[n]
		
			else:
			
				#Psi0 = np.empty([Phi.shape[0],Phi.shape[1]+Xi.shape[1]])
				Gamma = []
				for i in range(Xi.shape[1]):
					for j in range(Phi.shape[1]):
						Psi = copy.deepcopy(PhiS)
						Psi[:,j] = XiS[:,i]
						if 0:
							n = np.min(Psi.shape)
							Psi0 = np.concatenate((Phi,Xi), axis=1)
							np.delete(Psi0,j,1)##fix the problem delete the column
							W0 = np.concatenate(((scipy.stats.chi2.ppf(1-alpha,Phi.shape[0]*Phi.shape[1])**0.5)*LamPhi,(scipy.stats.chi2.ppf(1-alpha,Xi.shape[0]*Xi.shape[1])**0.5)*LamXi), axis=1)
							np.delete(W0,j,1)
							UPsi,SPsi1,VPsi = np.linalg.svd(Psi)
							VPsi = VPsi.transpose()
							SPsi = np.zeros((SPsi1.shape[0],SPsi1.shape[0]))
						
							for i in range(len(SPsi)):
								SPsi[i][i]=SPsi1[i]
							PsiSing = Psi0 - np.dot(np.dot(SPsi[n,n],UPsi[:,n]),VPsi[:,n].T)*W0
							del UPsi
							del VPsi
							SPsi = np.diag(SPsi)
							PsiSingulars[:,:,1,j] = PsiSing
					
						else:
							SPsi = LA.svd(Psi)[1]
							Gamma.append(SPsi[-1])
			Gamma = np.asarray(Gamma)			
			Gamma = Gamma.reshape((int(Gamma.size**0.5),int(Gamma.size**0.5)))
		
						#Gamma[i,j] =SPsi[-1]
		else:
			Gamma =np.min(LA.svd(PhiS)[1])
		PS = Gamma>1
		NrPS = np.sum(PS)
		return Gamma,PS,NrPS
	
