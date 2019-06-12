'''do the uitable from 107-112'''
'''do the biograph from 115-124'''
'''throw the error message from 167-169'''
'''save network from 179-181'''	
import numpy as np
import datetime
#from datastruct.Exchange import Exchange
from datastruct.Exchange import Exchange as E
from numpy import linalg as LA
from scipy.sparse import csr_matrix
import os
import math
import pandas as pd
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import networkx as nx
from datastruct.obj_dict import obj_dict
from matplotlib.pyplot import figure
import copy
_uri = "random/N10/Nordling-D20100302-random-N10-L25-ID1446937.json"
_database = "https://bitbucket.org/api/2.0/repositories/sonnhammergrni/gs-networks/src/master"

class Network():
	def __init__(self,net = None):
		if net == None:
			self.name = 0 
			self.A = []
			self.G = []
			self.names = []
			self.description =[]
			self.created =	{
					'creator':'',
					'time':datetime.datetime.now().strftime('%s'),
					'id':'',
					'nodes':'',
					'type':'unknown',
					'sparsity':'',
					}
			self.tol = np.finfo(float).eps
			self.N = 0
			self.structure = 'none'
			self.nodes = []
			self.params = []
		else:
			self.name = net['network']
			self.A = net['A']
			self.G = net['G']
			if len(net["names"][0]) == 2:
				Newname = copy.copy(net['names'])
				for i in range(9):
					Newname[i] = 'G0'+'%s'%(i+1)
				self.names = Newname
			else:
				self.names = net['names']
			self.description = net['description']
			self.created = net['created']
			self.tol = np.finfo(float).eps
			self.N = net['N']
			self.structure = net['network'].split('-')[2]
			names = pd.Series(self.names, name='node')
			names.name = 'node'
			names = names.apply(lambda x: x[0] + x[1:].zfill(2))
			self.nodes = names
			fr = names.copy()
			fr.name = 'source'
			to = names.copy()
			to.name = 'target'
			model_params = pd.DataFrame(net['A'], index=to, columns=fr).T
			self.params = model_params.stack()[~(model_params.stack() == 0)]
			self.params.name = 'value'
			paramind = self.params.index
			self.shape = tuple([max(i) + 1 for i in paramind.labels])			
			

	def Network(self,*args):
		net = Network()
		if len(args) == 2:
			self.setA(net,args[0])
			net.created['type'] = args[1]
			self.setname(net)
			self.get_N(net)
			self.get_names(net)
			names = pd.Series(net.names, name="node")
			names.name = "node"
			net.A = pd.DataFrame(net.A, index=names, columns=names)
			net.G = pd.DataFrame(net.G, index=names, columns=names)
		elif len(args) == 1:
			self.setA(net,args[1])
			self.setname(net)
			self.get_N(net)
			self.get_names(net)
			names = pd.Series(net.names, name="node")
			names.name = "node"
			net.A = pd.DataFrame(net.A, index=names, columns=names)
			net.G = pd.DataFrame(net.G, index=names, columns=names)
		return net
	def setA(self,net,A):
		N = Network()
		net.A = A
		net.G = -LA.pinv(csr_matrix(A).todense())
		net.created['id'] = str(int(np.around(LA.cond(csr_matrix(A).todense())*10000)))
		net.created['nodes'] = str(A.shape[0])
		net.created['sparsity'] = self.nnz(net)
		if 0:#ispc??
			net.created['creator'] = os.environ['HOME'][6:]
		else:
			net.created['creator'] = os.environ['HOME'][6:]
		
	def setname(self,net,*args):
		N = Network()
		if len(args) == 0:
			namestruct = net.created
		
		elif len(args) == 1:
			namestruct = args[0]
		
		if not isinstance(namestruct,dict):
			print('input argument must be name/value pairs in struct form')
		namer = net.created
		inpNames = list(namestruct.keys())
		optNames = namer.keys()
		for i in range(len(inpNames)):
			if inpNames[i] in optNames:
				namer['%s'%(inpNames[i])] = namestruct['%s'%(inpNames[i])]
		net.name = namer['creator'] + '-D' + datetime.datetime.now().strftime('%Y%m%d') + '-' + namer['type'] + '-N' + namer['nodes'] + '-L' + str(int(self.nnz(net))) + 'ID' + namer['id']
		return net

	def get_N(self,net):
		b = np.asarray(net.A)
		net.N = b.shape[0]
		return b.shape[0]
	def get_names(self,net):
		names = net.names
		if len(names) == 0:
			for i in range(int(net.N)):
				names.append('G%d'%(i+1))
			net.names =names
		else:
			names = net['names']
			net.names = names
		return names
	def show(self,net):
		if isinstance(net,dict):
			net=obj_dict(net)
		#net.description = []
		Property = ['Name','Description','Sparseness','# Nodes','# links']
		Value = [net.name,net.description,self.nnz(self,net)/(self.size(self,net)[0]*self.size(self,net)[1]),self.size(self,net)[0],self.nnz(self,net)]
		d = {'Property':Property,'Value':Value}
		networkProperties = pd.DataFrame(d)
		return networkProperties
		aa=[None]
		for i in range(self.size(net)[0]):
			aa.append('G%d'%(i+1))
		x = PrettyTable(aa)
		for i in range(self.size(net)[0]):
			bb=[]
			bb.append('G%d'%(i+1))
			for w in range(self.size(net)[0]):
				bb.append(net.A[i][w])
			x.add_row(bb)
		'''
		networkProperties = {
					'Name':net.network,
					'Description':net.description,
					'Sparseness':self.nnz(net)/self.size(net)[0]*self.size(net)[1],
					'# Nodes':self.size(net)[0],
					'# links':self.nnz(net),
					}
		'''
		return networkProperties,x
	
	'''
	def view(self,net,*args):##this figures do not show the weight
		if isinstance(net,dict):
			net=obj_dict(net)
		G = nx.from_numpy_matrix(np.array(net.A), create_using=nx.DiGraph(),parallel_edges = True)
		if len(args)>0:
			if args[0] == 'circular':		
				pos = nx.circular_layout(G)
				nx.draw_circular(G)
			elif args[0] == 'random':
				pos = nx.random_layout(G)
				nx.draw_random(G)
			elif args[0] == 'shell':
				pos = nx.shell_layout(G)
				nx.draw_shell(G)
			elif args[0] == 'spring':		
				pos = nx.spring_layout(G)
				nx.draw_spring(G)
			elif args[0] == 'spectral':
				pos = nx.spectral_layout(G)
				nx.draw_spectral(G)
		else:
			pos = nx.circular_layout(G)
			nx.draw_circular(G)
		labels = {i : i + 1  for i in G.nodes()}
		nx.draw_networkx_labels(G,pos,labels, font_size=15,font_weight='normal')
		
		plt.show()

	'''
	def view(net, labels=None, 
		node_size=400, node_color='blue', node_alpha=0.3,
		node_text_size=12,
		edge_color='red', edge_alpha=0.5, edge_tickness=1,
		edge_text_pos=0.1,
		text_font='sans-serif'):
		graph_layout = input('choose the graph layout (spring,spectral, random,shell)\t')
	    # create networkx graph
		G = nx.from_numpy_matrix(np.array(net.A), create_using=nx.DiGraph(),parallel_edges = None)
	    # these are different layouts for the network you may try
	    # shell seems to work best
		if graph_layout == 'spring':
			graph_pos=nx.spring_layout(G)
		elif graph_layout == 'spectral':
			graph_pos=nx.spectral_layout(G)
		elif graph_layout == 'random':
			graph_pos=nx.random_layout(G)
		else:
			graph_pos=nx.shell_layout(G)
		labels = {i : i + 1  for i in G.nodes()}
		graph_pos1 = copy.copy(graph_pos)
		if graph_layout == 'random':
			a = 0.03
			b = 0.04
		elif graph_layout == 'shell':
			a = 0.07
			b = 0.08
		else:
			a = 0.06
			b = 0.07
		for i in range(len(graph_pos)):
			if i//(int(len(graph_pos))/2) == 0: 
				graph_pos1[i] = graph_pos1[i]+[0,a]
			else:
				graph_pos1[i] = graph_pos1[i]-[0,b]
		
	    # draw graph
		fig,ax = plt.subplots(dpi = 120,figsize=(100,100))
		#fig.set_size_inches(18.5, 10.5, forward=True)
		#fig,ax = plt.figure(1,dpi = 120,figsize=(100,100))
		#plt.figure(1,figsize=(100,100))
		nx.draw_networkx_nodes(G,graph_pos,node_size=node_size, 
		                   alpha=node_alpha, node_color=node_color)
		nx.draw_networkx_edges(G,graph_pos,width=edge_tickness,
		                   alpha=edge_alpha,edge_color=edge_color)
		nx.draw_networkx_labels(G, graph_pos1,labels,font_size=node_text_size,
		                    font_family=text_font)
		nx.draw_networkx_edge_labels(G, graph_pos,font_size=8)
		#plt.savefig('~/nordlinglab-ni/ni/savepath')
		fig.patch.set_visible(False)
		ax.axis('off')
		#plt.savefig('myfig')
		plt.show()
	def sign(self,net):#index will compare to original lower 1
		SA = np.sign(net.A)
		return SA
	def logical(self,net):
		LA = np.asarray(net.A)
		for i in range(LA.shape[0]):
			for w in range(LA.shape[1]):
				if LA[i][w]==0:
					LA[i][w]=0
				else:
					LA[i][w]=1
		return LA
	def size(self,net,*args):
		if len(args)>0:
			sA = np.size(net.A,args[0])
		else:
			A=np.asarray(net.A)		
			sA = [A.shape[0],A.shape[1]]
		return sA
	def nnz(self,net):
		nnzA =  np.count_nonzero(net.A)
		return nnzA
	def svd(self,net):
		s = LA.svd(net.A, full_matrices=True)
		return s[1]
	def mtimes(self,net,p): 
		if p.shape[0]==1:
			p=np.transpose(p)
		Y = np.dot(net.G,p)
		return Y
	
	def populate(self,net,inpu):##have not tested
		#if not isinstance(inpu,dict):#have many condictions
		#	error('Needs to be a dict...') #modify
		#throw the error messages from 167-169
		inputnames = list(vars(inpu).keys())
		names = vars(net).keys()
		for i in range(len(inputnames)):
			if inputnames[i] in names:
				net.__dict__['%s'%(inputnames[i])] = inpu.__dict__['%s'%(inputnames[i])]

		return net
	def save(self,obj,savepath,fending,*args):
		#E = Exchange()
		E.save(obj,savepath,fending)
	
	def load(self,savepath,name,fending,*args):
		E = Exchange()
		return 	E.load(savepath,name,fending)
	#not the same as original, but it works

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
				if 'A' in obj_data:
					net=obj_data
					names = pd.Series(net["names"], name="node")
					names.name = "node"
					names = names.apply(lambda x: x[0] + x[1:].zfill(2))
					fr = names.copy()
					fr.name = "source"
					to = names.copy()
					to.name = "target"
					net['A'] = pd.DataFrame(net["A"], index=to, columns=fr)
					net['G'] = pd.DataFrame(net["G"], index=to, columns=fr)		
					return net
				elif isinstance(obj_data,dict):
					print('This is not a network')
				else:
					return obj_data
			except:		
				default_file = 'Nordling-D20100302-random-N10-L25-ID1446937.json'
				obj_data = E.fetch(options,default_file)
				net = obj_data
				names = pd.Series(net["names"], name="node")
				names.name = "node"
				names = names.apply(lambda x: x[0] + x[1:].zfill(2))
				fr = names.copy()
				fr.name = "source"
				to = names.copy()
				to.name = "target"
				net['A'] = pd.DataFrame(net["A"], index=to, columns=fr)
				net['G'] = pd.DataFrame(net["G"], index=to, columns=fr)			
				return net
		else:
			#default_url =  options['baseurl']+options['version']+'/'+options['type']+'/'+'N'+str(options['N'])+'/'
			#obj_data = E.fetch(options,default_url)		
			#net = obj_data	
			#return net
			pass
'''
	def fetch(self,*args):
		#directurl,baseurl,version,type,N,name,filelist,filetype
		#options=['','https://bitbucket.org/api/1.0/repositories/sonnhammergrni/gs-networks/raw/','master','random','10','','0',]
		options={
			'directurl':'',
			'baseurl':'https://bitbucket.org/api/1.0/repositories/sonnhammergrni/gs-networks/raw/',
			'version':'master',
			'type':'random',
			'N':'10',
			'name':'',
			'filelist':'0',
			'filetype':'',
			}
		E=Exchange()
		if len(args) != 0:
			try:
				default_file = args[0]
				obj_data = E.fetch(options,default_file)
				net=obj_data
				names = pd.Series(net["names"], name="node")
				names.name = "node"
				net['A'] = pd.DataFrame(net["A"], index=names, columns=names)
				net['G'] = pd.DataFrame(net["G"], index=names, columns=names)		
				return net
			except:		
				default_file = 'Nordling-D20100302-random-N10-L25-ID1446937.json'
				obj_data = E.fetch(options,default_file)
				net = obj_data
				names = pd.Series(net["names"], name="node")
				names.name = "node"
				net['A'] = pd.DataFrame(net["A"], index=names, columns=names)
				net['G'] = pd.DataFrame(net["G"], index=names, columns=names)			
				return net
		else:
			default_url =  options['baseurl']+options['version']+'/'+options['type']+'/'+'N'+str(options['N'])+'/'
			obj_data = E.fetch(options,default_url)		
			net = obj_data	
			return net
	#the net should be stored to tuple from 242-249
	#i don't know about the if the len(arg)==2?? from 250-261  
'''
