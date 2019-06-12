import numpy as np
import math
import matplotlib.pyplot as plt
from numpy import linalg as LA
from find import find
from ind import ind1
class CompareModels:
	def __init__(self):
		self.tol = np.finfo(float).eps
		self.A = []
		self.zetavec = []
		self.SA = []
		self.UA = []
		self.VA = []
		self.LA = []
		self.QA = []
		self.DGA = []
		self.STA = []
		self.N = []
		self.ntl = []
		self.npl = []
		self.abs2norm = []
		self.rel2norm = []
		self.maee = []
		self.mree = []
		self.mase = []
		self.mrse = []
		self.masde = []
		self.mrsde = []
		self.maeve = []
		self.mreve = []
		self.maede = []
		self.mrede = []
		self.afronorm = []
		self.rfronorm = []
		self.al1norm = []
		self.rl1norm = []
		self.n0larger = []
		self.r0larger = []
		self.ncs = []
		self.sst = []
		self.sst0 = []
		self.plc = []
		self.nlinks = []	
		self.TP = []
		self.TN = []
		self.FP = []
		self.FN = []
		self.sen = []
		self.spe = []
		self.comspe = []
		self.pre = []
		self.TPTN = []
		self.structsim = []
		self.Fl = []
		self.MCC = []
		self.TR = []
		self.TZ = []
		self.FI = []
		self.FR = []
		self.FZ = []
		self.dirsen = []
		self.dirspe = []
		self.dirprec = []
		self.SMCC = []
	#M = M.CompareModels(M,np.asarray(Net['A']),estA)
	def CompareModels(self,M,*args):
		if len(args) >= 1:
			M.A = args[0]
		if len(args) >= 2:
			Alist = args[1]
			M = self.compare(M,args[1])#to end
		return M
	
	def compare(self,M,Alist,*args):
		A = M.A
		if len(A) == 0:
			print('True network, A , needs to be set')
		if len(args) == 3:
			selected = args[0]
		if self.issquare(M):
			M = M.system_measures(M,Alist)
			M = M.topology_measures(M,Alist)
			M = M.correlation_measures(M,Alist)
			M = M.graph_measures(M,Alist)
			M = M.signGraph_measures(M,Alist)
		else:
			M = M.topology_measures(M,Alist)
			M = M.correlation_measures(M,Alist)
			M = M.graph_measures(M,Alist)
			M = M.signGraph_measures(M,Alist)
		'''
		if 
		'''
		return M
	def set_A(self,M,net):
		A = M.A
		if len(A) != 0 and len(net) !=0:
			print('True A already set, overwriting')
		if hasattr(net,'G'):
			if np.asarray(net.A).ndim > 2:
				print('3d matrices are not allowed as golden standard')
			M.A = np.asarray(net.A)
		else:
			if np.asarray(net.A).ndim > 2:
				print('3d matrices are not allowed as golden standard')
			M.A = net
		M =M.setA(M,M.A)
		return M
	def setA(self,M,net):
		M.A = net
		UA,SA1,VA = np.linalg.svd(np.asarray(M.A))
		VA = VA.transpose()
		SA = np.zeros((SA1.shape[0],SA1.shape[0]))
		for i in range(len(SA)):
			SA[i][i]=SA1[i]
		if self.issquare(M):#issquare
			LA1,QA = LA.eig(np.asarray(M.A))
			crap = np.sort(LA1)
			index = np.argsort(LA1)
			QA = QA[:,index]
			M.LA = LA1
			M.QA = QA
		Z = np.zeros((np.asarray(M.A).shape[0],np.asarray(M.A).shape[1]))
		DiGraphA = np.zeros((np.asarray(M.A).shape[0],np.asarray(M.A).shape[1]))
		for i in range(Z.shape[0]):
			for j in range(Z.shape[1]):
				if Z[i][j] == 0:
					DiGraphA[i][j] = 0
				else:
					DiGraphA[i][j] = 1
		
		for j in range(Z.shape[1]):
			for i in range(Z.shape[0]):
				if abs(np.asarray(M.A)[j][i]) > np.finfo(float).eps:
					DiGraphA[j][i] = 1
				else:
					DiGraphA[j][i] = 0
		STopoA = Z
		for j in range(Z.shape[1]):
			for i in range(Z.shape[0]):
				if np.asarray(M.A)[j][i] > np.finfo(float).eps:
					STopoA[j][i] = 1
				
		for i in range(Z.shape[0]):
			for j in range(Z.shape[1]):
				if np.asarray(M.A)[i][j] < -np.finfo(float).eps:
					STopoA[i][j] = -1

				
		M.UA = UA
		M.SA = SA
		M.VA = VA
		M.DGA = DiGraphA
		M.STA = STopoA
		M.N = np.asarray(M.A).shape[0]
		M.npl = np.asarray(M.A).size
		M.ntl = np.sum(DiGraphA)
		return M
	def system_measures(self,M,Alist):
		
		for i in range(Alist.shape[2]):
			T = Alist[:,:,i]
			M.abs2norm.append(LA.norm(T-M.A,ord=2))
			
			try:
				M.rel2norm.append(LA.norm(np.dot(LA.pinv(T),T)-M.A,ord=2))
			except:
				M.rel2norm.append(np.inf)
			M.maee.append(np.max(np.abs(T-M.A)))
			A_tem =np.zeros((len(T),len(T)))
			B_tem = 1/np.max(np.abs(T),axis = 1)
			for i in range(len(T)):
				A_tem[i][i] = B_tem[i]
			M.mree.append(np.max(np.dot(A_tem,np.abs(T-M.A))))
			
			S = LA.svd(T)[1]
			M.mase.append(np.max(np.abs(S-np.diag(M.SA)),axis = 0))
			M.mrse.append(np.max(np.dot(np.abs(np.diag(S)-M.SA),(1/S)),axis = 0))
			
			temp = np.dot(np.dot(np.transpose(M.UA),T),M.VA)
			M.masde.append(np.max(np.abs(np.diag(temp)-np.diag(M.SA)),axis = 0))
			M.mrsde.append(np.max(np.dot(np.diag(np.abs(np.diag(temp)-np.diag(M.SA))),(1/np.diag(temp))),axis = 0))
			
			L = LA.eig(T)[0]
			crap = -np.sort(-np.abs(L),axis = 0)
			index = np.argsort(-np.abs(L),axis = 0)

			L = L[index]
			M.maeve.append(np.max(np.abs(L-M.LA),axis = 0))
			
			M.mreve.append(np.max(np.abs(np.dot(np.diag(1/L),(L-M.LA))),axis = 0))
			
			temp = np.dot(np.dot(LA.pinv(M.QA),T),M.QA)
			temp2 = np.abs(np.diag(temp)-M.LA)
			M.maede.append(np.max(temp2,axis = 0))
			M.mrede.append(np.max(np.abs(np.dot(np.diag(temp2),(1/np.diag(temp)))),axis = 0))
			
			M.afronorm.append(LA.norm((T-M.A), 'fro'))
			try:
				M.rfronorm.append(LA.norm(np.dot(LA.pinv(T),(T-M.A)), 'fro'))
			except:
				M.rfronorm.append(np.inf)
			
			BB=[]
			for j in range(M.DGA.shape[1]):
				for k in range(M.DGA.shape[0]):
					if (M.DGA ==0)[k][j] == 1:
						BB.append(T[k][j])
			BB1=[]
			for j in range(M.DGA.shape[1]):
				for k in range(M.DGA.shape[0]):
					if (M.DGA !=0)[k][j] == 1:
						BB1.append(M.A[k][j])
			
			M.al1norm.append(np.sum(abs(np.asarray(BB))))
			
			M.rl1norm.append(np.sum(abs(np.asarray(BB)))/np.sum(np.sum(abs(M.A))))
		
			M.n0larger.append(np.sum(abs(np.asarray(BB)) > np.min(abs(np.asarray(BB1)))))

			M.r0larger.append(np.sum(abs(np.asarray(BB)) > np.min(abs(np.asarray(BB1))))/np.sum(np.sum(M.DGA ==0)))
			
		return M
####keep to modify
	def topology_measures(self,M,Alist):
		
		for i in range(Alist.shape[2]):
			T = Alist[:,:,i]
			STopoT = np.zeros((M.A.shape[0],M.A.shape[1]))	
			for j in range(STopoT.shape[1]):
				for k in range(STopoT.shape[0]):
					if T[k][j] > np.finfo(float).eps:
						STopoT[k][j] = 1
			for j in range(STopoT.shape[1]):
				for k in range(STopoT.shape[0]):
					if T[k][j] < -np.finfo(float).eps:
						STopoT[k][j] = -1
			
			for j in range(M.STA.shape[1]):
				for k in range(M.STA.shape[0]):
					if M.STA[k][j] == STopoT[k][j]:
						STopoT[k][j] = 1
			temp = STopoT
					
			M.ncs.append(np.sum(np.sum(temp)))
			M.sst.append(np.sum(np.sum(temp))/M.npl)
			BB1=[]
			for j in range(M.DGA.shape[1]):
				for k in range(M.DGA.shape[0]):
					if (M.DGA !=0)[k][j] == 1:
						BB1.append(temp[k][j])
			
			
			M.sst0.append(np.sum(np.sum(np.asarray(BB1)))/M.ntl)
		return M
	def correlation_measures(self,M,Alist):
		
		for i in range(Alist.shape[2]):
			T = Alist[:,:,i]
			M.plc.append(np.corrcoef(M.A,T)[0,1])
		return M
			#M.plc = should find the package
	def graph_measures(self,M,Alist):
		Z = np.zeros((M.A.shape[0],M.A.shape[1]))
		for i in range(Alist.shape[2]):
			T = Alist[:,:,i]
			DiGraphT = Z!=0
			for j in range(DiGraphT.shape[1]):
				for k in range(DiGraphT.shape[0]):
					if abs(T[k][j]) > np.finfo(float).eps:
						DiGraphT[k][j] = 1
			BB = 0
			for i in range(DiGraphT.shape[0]):
				for j in range(DiGraphT.shape[1]):
					if DiGraphT[i][j] != 0:
						BB = BB+1
			M.nlinks.append(BB)
			M.TP.append(np.sum(np.logical_and(M.DGA,DiGraphT)))
			M.TN.append(np.sum(np.logical_or(M.DGA,DiGraphT) == 0))
			M.FP.append(np.sum(np.logical_and(np.logical_not(M.DGA),DiGraphT)))
			M.FN.append(np.sum(np.logical_and(np.logical_not(DiGraphT),M.DGA)))
			
			M.sen.append(M.TP[-1]/(M.TP[-1]+M.FN[-1]))
			
			for j in range(np.asarray(M.sen).shape[0]):
				if math.isnan(M.sen[j]):
					M.sen[j] = 1
			M.spe.append(M.TN[-1]/(M.TN[-1]+M.FP[-1]))
			M.comspe.append(M.FP[-1]/(M.TN[-1]+M.FP[-1]))
			M.pre.append(M.TP[-1]/(M.TP[-1]+M.FP[-1]))
			for j in range(np.asarray(M.pre).shape[0]):
				if math.isnan(M.pre[j]):
					M.pre[j] = 1
			M.TPTN.append(M.TP[-1] + M.TN[-1])
			M.structsim.append(M.TPTN[-1]/M.npl)
			n = 2*M.TP[-1] + M.FP[-1] + M.FN[-1]
			if n == 0:
				M.Fl.append(0)
			else:
				M.Fl.append(2*M.TP[-1]/n)
			n = (M.TP[-1]+M.FP[-1])*(M.TP[-1] + M.FN[-1])*(M.TN[-1] + M.FP[-1])*(M.TN[-1] + M.FN[-1])
			if n == 0:
				M.MCC.append(0)
			else:
				M.MCC.append((M.TP[-1]*M.TN[-1]-M.FP[-1]*M.FN[-1])/np.sqrt(n))
		return M
	def signGraph_measures(self,M,Alist):
		for i in range(Alist.shape[2]):
			T = Alist[:,:,i]
			STT = np.zeros((M.A.shape[0],M.A.shape[1]))
			
			for j in range(STT.shape[1]):
				for k in range(STT.shape[0]):
					if T[k][j] > np.finfo(float).eps:
						STT[k][j] = 1
			for j in range(STT.shape[1]):
				for k in range(STT.shape[0]):
					if T[k][j] < -np.finfo(float).eps:
						STT[k][j] = -1
			
			CC = 0
			DD = np.logical_and(M.STA==1,STT ==1)
			for j in range(np.asarray(DD).shape[0]):
				for k in range(np.asarray(DD).shape[1]):
					if DD[j][k] != 0:
						CC=CC+1
			
			CCC = 0
			DDD = np.logical_and(M.STA ==-1,STT ==-1)
			for j in range(np.asarray(DDD).shape[0]):
				for k in range(np.asarray(DDD).shape[1]):
					if DDD[j][k] != 0:
						CCC=CCC+1
			
			M.TR.append(CC+CCC)
			
			CC1 = 0
			DD1 = np.logical_and(np.logical_not(M.STA),np.logical_not(STT))
			for j in range(np.asarray(DD1).shape[0]):
				for k in range(np.asarray(DD1).shape[1]):
					if DD1[j][k] != 0:
						CC1=CC1+1
			M.TZ.append(CC1)
			CC2 = 0
			DD2 = np.logical_and(M.STA==1,STT ==-1) 
			for j in range(np.asarray(DD2).shape[0]):
				for k in range(np.asarray(DD2).shape[1]):
					if DD2[j][k] != 0:
						CC2=CC2+1
			CCC2 = 0
			DDD2 = np.logical_and(M.STA ==-1,STT ==1)
			for j in range(np.asarray(DDD2).shape[0]):
				for k in range(np.asarray(DDD2).shape[1]):
					if DDD2[j][k] != 0:
						CCC2=CCC2+1
			M.FI.append(CC2+CCC2)
			CC3 = 0
			DD3 = np.logical_and(np.logical_not(M.STA),np.abs(STT))
			for j in range(np.asarray(DD3).shape[0]):
				for k in range(np.asarray(DD3).shape[1]):
					if DD3[j][k] != 0:
						CC3=CC3+1
			M.FR.append(CC3)
			CC4 = 0
			DD4 = np.logical_and(np.abs(M.STA),np.logical_not(STT))
			for j in range(np.asarray(DD4).shape[0]):
				for k in range(np.asarray(DD3).shape[1]):
					if DD4[j][k] != 0:
						CC4=CC4+1
			M.FZ.append(CC4)
			
			if (M.TR[-1] + M.FI[-1] + M.FZ[-1]) == 0:
				M.dirsen.append(0)
			else:
				M.dirsen.append(M.TR[-1]/(M.TR[-1]+ M.FI[-1] + M.FZ[-1]))
			if (M.TZ[-1]+M.FR[-1]) == 0:
				M.dirspe.append(0)
			else:
				M.dirspe.append(M.TZ[-1]/(M.TZ[-1]+M.FR[-1]))
			if (M.TR[-1]+M.FI[-1]+M.FR[-1]) == 0:
				M.dirprec.append(0)
			else:
				M.dirprec.append(M.TR[-1]/(M.TR[-1]+M.FI[-1]+M.FR[-1]))
			n = (M.TR[-1]+M.FR[-1])*(M.TR[-1]+M.FI[-1]+M.FZ[-1])*(M.TZ[-1]+M.FR[-1])*(M.TZ[-1]+M.FI[-1]+M.FZ[-1])
			
			if n ==0:
				M.SMCC.append(0)
			else:
				M.SMCC.append((M.TR[-1]*M.TZ[-1] - M.FR[-1]*(M.FI[-1] + M.FZ[-1]))/np.sqrt(n))
		return M	
	def issquare(self,M):
		square = True
		n = M.A.shape[0]
		m = M.A.shape[1]
		if n != m:
			square = False
		return square
	def AUROC(self,M):
		M.TPR = M.sen
		M.FPR = M.comspe
		M.orde = np.argsort(M.nlinks)
		TPR1 = []
		FPR1 = []
		for i in M.orde:			
			TPR1.append(M.TPR[i])
			FPR1.append(M.FPR[i])
		M.TPR = TPR1	
		M.FPR = FPR1
		M.auroc = np.trapz(M.TPR,M.FPR)
		return M
	def ROC(self,M):
		h = plt.plot(M.FPR,M.TPR)
		plt.xlabel('False positive rate')
		plt.ylabel('True positive rate')
		plt.title('ROC curve'+'\nAUROC = %0.3f'%(M.auroc))
		plt.xlim(0,1.05)
		plt.ylim(0,1.05)
		#plt.hold(True)
		plt.plot([0,1],[0,1],'--')
		plt.grid()
		return plt.show(h)
	
	def AUPR(self,M):
		
		M.PRE = M.pre
		M.REC = M.sen
		M.orde = np.argsort(M.nlinks)
		PRE1 = []
		REC1 = []
		for i in M.orde:			
			PRE1.append(M.PRE[i])
			REC1.append(M.REC[i])
		M.PRE = PRE1	
		M.REC = REC1
		M.aupr = np.trapz(M.PRE,M.REC)
		return M
	def PR(self,M):
		
		h = plt.plot(M.REC,M.PRE)
		plt.xlabel('recall')
		plt.ylabel('precision')
		plt.title('PR curve'+'\nAUPR = %0.3f'%(M.aupr))
		plt.xlim(0,1.05)
		plt.ylim(0,1.05)
		plt.grid()
		return plt.show(h)
	
	def show(self,M,*args):
		tmp = vars(M)
		if 'A' in tmp:
			del tmp['A']
			del tmp['SA']
			del tmp['UA']
			del tmp['VA']
			del tmp['LA']
			del tmp['QA']
			del tmp['DGA']
			del tmp['STA']
			del tmp['N']
			del tmp['ntl']
			del tmp['npl']
			del tmp['tol']
		allprops = tmp.keys()
		liallprops = list(tmp.keys())
		if 0:#nargout ==0
			for i in range(len(allprops)):
				print(' %d %s'%(i,liallprops[i]))
		else:
			if len(args) == 0:
				return liallprops
			else:
				measure = args[0]
				if isinstance(measure,str):
					tmp1 = measure in allprops				
					return tmp1
				
				elif isinstance(measure,int):
					tmp2 = liallprops[measure]
					return tmp2
				
		
	def max(self,M,*args):
		
		m = 'all'
		if len(args) >= 0:
			props = M.show(M)
		
		if len(args) >= 1:
			m = args[0]
		
		if isinstance(m,int):
			m = props[m]
		
		maximums = []
		maximumst = []
		a={}
		if m is 'all':
			for i in range(len(props)):
				pass
		else:
			ind = find(props,m)
			junk = np.max(M.__dict__[props[ind]])
			maxind = ind1(M.__dict__[props[ind]],junk)
			
			for i in range(len(props)):
				prop = M.__dict__[props[i]]
				try:
					maximums.append(prop[int(maxind)])
					maximumst.append(props[i])
				except:
					pass
			
	#			maximums.append(prop[int(maxind)])
			
			for j in range(len(maximumst)):
				a.update({maximumst[j]:maximums[j]})
				
		return a,maxind
	def min(self,M,*args):
		
		m = 'all'
		if len(args) >= 0:
			props = M.show(M)
		
		if len(args) >= 1:
			m = args[0]
		
		if isinstance(m,int):
			m = props[m]
		
		minimums = []
		minimumst = []
		a={}
		if m is 'all':
			for i in range(len(props)):
				pass
		else:
			ind = find(props,m)
			junk = np.min(M.__dict__[props[ind]])
			minind = ind1(M.__dict__[props[ind]],junk)
			
			for i in range(len(props)):
				prop = M.__dict__[props[i]]
				try:
					minimums.append(prop[int(minind)])
					minimumst.append(props[i])
				except:
					pass
			
	#			maximums.append(prop[int(maxind)])
			
			for j in range(len(minimumst)):
				a.update({minimumst[j]:minimums[j]})
				
			return a,minind
