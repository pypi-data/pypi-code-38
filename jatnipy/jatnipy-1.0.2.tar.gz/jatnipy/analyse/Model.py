from analyse.DataModel import DataModel
import numpy as np
from numpy import linalg as LA
import scipy
from scipy import sparse
from scipy.sparse import csc_matrix
from numpy import linalg as LA
import networkx as nx
from networkx import (
	draw,
	DiGraph,
	Graph,
)
import statistics
class Model():
	def __init__(self):
		self.network = ''
		self.interampatteness = 0
		#self.proximity_ratio = 0
		self.NetworkComponents = 0
		#self.networkComponents = 0
		#self.medianPathLength = 0
		self.AvgPathLength = 0
		#self.meanPathLength = 0
		self.tauG = 0
		self.CC = 0
		self.DD = 0
	def Model(self,mat,*args):
		analysis = DataModel()
		'''
		if len(args) > 1:
			ind = ('tol' == args[0])
			if ind:
				analysis.tol = args[ind]
		'''
		analysis = self.analyse_model(analysis,mat,args)
		return analysis
	def analyse_model(self,analysis,mat,*args):#model = Net
		analysis.network = self.identifier(mat)
		analysis.interampatteness = self.cond(mat)
		analysis.NetworkComponents = self.graphconncomp(mat)
		#analysis.networkComponents = self.graphconncomp(mat)
		#analysis.medianPathLength = self.median_path_length(mat)[0]
		analysis.AvgPathLength = self.median_path_length(mat)[1]
		#analysis.meanPathLength = self.median_path_length(mat)[1]
		analysis.tauG = self.time_constant(mat)
		analysis.CC = np.nanmean(np.asarray(self.clustering_coefficient(mat)[0]))
		analysis.DD = np.mean(np.asarray(self.degree_distribution(mat)[0]))
		#analysis.proximity_ratio = self.calc_proximity_ratio(mat)
		return analysis
	
	def identifier(self,model):
		if hasattr(model,'G'):
			network = model.name
		else:
			network = ''
		return network
	def give_matrix(self,model,*args):
		if hasattr(model,'G') and len(args) < 1:#should modify the condition
			A = np.asarray(model.A)
		elif hasattr(model,'G') and args[0] is 'inv':
			A = np.asarray(model.G)
		else:
			A = np.asarray(model)
		return A
	def cond(self,model):
		A = self.give_matrix(model)
		A1 = scipy.sparse.csc_matrix(A)
		interampatteness = LA.cond(A1.todense())
		return interampatteness
	def time_constant(self,model):
		G =self.give_matrix(model,'inv')
		G1 = LA.eig(G)
		tauG = np.ndarray.min(np.sort(1/np.absolute(G1[0].real)))
	#	tauG = time_constant(G)
		return tauG
	def graphconncomp(self,model,*args):#args should specificially say undirected, but now undirected result is not correct. directed not need to say.
		A = self.give_matrix(model)
		if len(args)>0:
			NC2 = nx.Graph(scipy.sparse.csc_matrix(np.sign(A)))
			NC = nx.number_connected_components(NC2)
		else:
			NC1 = nx.DiGraph(scipy.sparse.csc_matrix(np.sign(A)))
			NC = nx.number_strongly_connected_components(NC1)
		return NC
	def median_path_length(self,model,*args): #should add function about delete inf, but I think it is not necessary. now it only can use in directed #and now it can only reply two values, the rest of two values is same as the first and second value(difference:logical or not), and the last value is len(np.inf) it could appear in undirected graph.
		if len(args)>0:#for undireceted median will be wrong #args should specificially say undirected, but now undirected result is not correct. directed not need to say.
			A = self.give_matrix(model)
			for i in range(A.shape[0]):
				for w in range(A.shape[1]):
					if A[i][w]==0:
						A[i][w]=0
					else:
						A[i][w]=1
			p11 = nx.Graph(scipy.sparse.csc_matrix(A)) 
			pl=[]
			for i in range(len(A)):
				for w in range(len(A)):
					p12 = nx.shortest_path_length(p11,source=w)
					try:
						pl.append(p12[i])
					except:
						pass
				pl.remove(0)
			mpl = statistics.median(pl)
			apl = statistics.mean(pl)
			return mpl,apl
		else:
			A = self.give_matrix(model)
			for i in range(A.shape[0]):
				for w in range(A.shape[1]):
					if A[i][w]==0:
						A[i][w]=0
					else:
						A[i][w]=1
			p11 = nx.DiGraph(scipy.sparse.csc_matrix(A)) #change to Graph() it could be transform to undireceted, but mean value will be wrong median value is correct for one example 
			pl=[]
			for i in range(len(A)):
				for w in range(len(A)):
					p12 = nx.shortest_path_length(p11,source=w)
					try:
						pl.append(p12[i])
					except:
						pass
				pl.remove(0)
			mpl = statistics.median(pl)
			apl = statistics.mean(pl)
			return mpl,apl

	def clustering_coefficient(self,model,*args):#args should specificially say undirected, but now undirected result is not correct. directed not need to say.
		A = self.give_matrix(model)
		for i in range(A.shape[0]):
			A[i][i]=0
		if len(args) > 0: #undirected ##correct but the coding should modify to analysis.CC = np.nanmean(np.asarray(self.clustering_coefficient(mat)))
			A = A + np.transpose(A)			
			for i in range(A.shape[0]):
				for w in range(A.shape[1]):
					if A[i][w]==0:
						A[i][w]=0
					else:
						A[i][w]=1
			C=[]
			for i in range(A.shape[0]):
				local_vertices = np.nonzero(A[i])
				subnet = []
				for w in range(len(local_vertices[0])):
					for m in range(len(local_vertices[0])):
						subnet.append(A[local_vertices[0][w]][local_vertices[0][m]])
						
				subnet = np.asarray(subnet)
				subnet = np.reshape(subnet,(len(local_vertices[0]),len(local_vertices[0])))
				try:
					C.append(len(np.nonzero(subnet)[0])/(subnet.size-subnet.shape[0]))
				except:
					C.append(np.inf)
				C.append(len(np.nonzero(subnet)[0])/(subnet.size-subnet.shape[0]))			
			return C
		else:
			Cout=[]
			Cin=[]
			for i in range(A.shape[0]):
				local_vertices = np.nonzero(A[i])
				subnet = []
				for w in range(len(local_vertices[0])):
					for m in range(len(local_vertices[0])):
						subnet.append(A[local_vertices[0][w]][local_vertices[0][m]])			
				subnet = np.asarray(subnet)
				subnet = np.reshape(subnet,(len(local_vertices[0]),len(local_vertices[0])))
				try:
					Cout.append(len(np.nonzero(subnet)[0])/(subnet.size-subnet.shape[0]))
				except:
					Cout.append(np.inf)
				A = np.transpose(A)
				local_vertices = np.nonzero(A[i])
				subnet = []
				for w in range(len(local_vertices[0])):
					for m in range(len(local_vertices[0])):
						subnet.append(A[local_vertices[0][w]][local_vertices[0][m]])
						
				subnet = np.asarray(subnet)
				subnet = np.reshape(subnet,(len(local_vertices[0]),len(local_vertices[0])))
				try:
					Cin.append(len(np.nonzero(subnet)[0])/(subnet.size-subnet.shape[0]))
				except:
					Cin.append(np.inf)
			
				for i in range(len(Cout)):
					if np.isinf(Cout[i]):
						Cout[i]=0
				for j in range(len(Cin)):
					if np.isinf(Cin[i]):
						Cin[i]=0 
			return Cout,Cin
	def degree_distribution(self,model,*args):
		A = self.give_matrix(model)
		for i in range(A.shape[0]):
			A[i][i]=0
		for i in range(A.shape[0]):
				for w in range(A.shape[1]):
					if A[i][w]==0:
						A[i][w]=0
					else:
						A[i][w]=1
		if len(args) > 0:#undirected##correct
			A = A + np.transpose(A)			
			for i in range(A.shape[0]):
				for w in range(A.shape[1]):
					if A[i][w]==0:
						A[i][w]=0
					else:
						A[i][w]=1
			degree_list = np.sum(A,axis=0)
			return degree_list,degree_list
		else:
			out_degree = np.sum(A,axis=0)
			in_degree = np.sum(np.transpose(A),axis=0)
			return out_degree,in_degree
	def calc_proximity_ratio(self,model):
		A = self.give_matrix(model)
		for i in range(A.shape[0]):
			A[i][i]=0
		for i in range(A.shape[0]):
				for w in range(A.shape[1]):
					if A[i][w]==0:
						A[i][w]=0
					else:
						A[i][w]=1	
		N = A.shape[0]
		L = self.median_path_length(model)
		Lt = L[0]
		L = L[1]
		md = len(np.nonzero(A)[0])/N
		Lr = np.log(N)/np.log(md)
		try:	
			C = statistics.mean(self.clustering_coefficient(A))
		except:
			C=[]
			C.append(statistics.mean(self.clustering_coefficient(A)[0]))
			C.append(statistics.mean(self.clustering_coefficient(A)[1]))
	
		Cr = len(np.nonzero(A)[0])/(N*(N-1))
		try:
			smallworldness = []		
			smallworldness.append((C[0]/Cr)*(Lr/L))
	#		smallworldness.append((C[1]/Cr)*(Lr/L))
			return smallworldness
		except:
			smallworldness = (C/Cr)*(Lr/L)
			return smallworldness

	##final things upload the properties and modify the give_matrix	
	
	'''	NetworkComponets = network.is_connected()##networkx 
	def graphconncomp_fake(model,*args):
		flag = 1
		if Model.type() == 'directed':
			flag = True
		else:
			flag = False
		return flag
	def graphconncomp_true(model):
		A = give_matrix(model)
		NetworkComponents = graphconncomp_fake(scipy.sparse.csc_matrix(np.sign(A)),'directed',1) #sparse matrixindex will compare to original lower 1
		return NetworkComponents'''
	

