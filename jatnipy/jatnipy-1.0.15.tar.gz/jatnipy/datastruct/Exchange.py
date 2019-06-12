from pathlib import Path
import urllib.parse
import urllib.request
import urllib.error
import pprint
import os 
import re
import json
import requests
import re
import datastruct.Exchange
import ubjson
import pickle
import numpy as np
_uri = "N10/Nordling-ID1446937-D20150825-N10-E15-SNR3291-IDY15968.json"
_database = "https://bitbucket.org/api/2.0/repositories/sonnhammergrni/gs-datasets/src/master"


class Exchange():
	
	def __init__(self):
		pass
	'''
	def populate(obj,inpu):
		inputnames = list(inpu.keys())
		names = list(obj.keys())
		for name in inputnames:
			if 1:
				obj['%s'%(name)] = inpu['%s'%(name)]
		return obj
	'''
	def save(obj,savepath=None,fending=None,*args):
		if fending is None:
			fending = '.pickle'
		if savepath is None:
			print('save path does not exist')
		
		if len(args) == 0:
			if not isinstance(fending,str):
				print('Input arguments must be a string')
			##now method only lack of xmlfile
		if 'G' in obj.__dict__:
			obj.A = np.asarray(obj.A)
			obj.G = np.asarray(obj.G)
			obj.nodes = list(obj.nodes)
			name = obj.name
			obj.network = obj.name
			#obj.names = obj.nodes
			try:
				del obj.__dict__['structure']
				del obj.__dict__['name']
				del obj.__dict__['nodes']
				del obj.__dict__['params']
			except:
				pass
			savevar = 'obj_data'
			if not isinstance(obj.A,list):
				obj.G = obj.G.tolist()
				obj.A = obj.A.tolist()
		elif 'E' in obj.__dict__:
			obj.P = np.asarray(obj.P)
			obj.F = np.asarray(obj.F)
			try:
				obj.cvP = np.asarray(obj.F_covariance_variable)
			except:
				pass
			try:
				obj.sdP = np.asarray(obj.F_covariance_element.head(obj.N).iloc[:, int(obj.N):int(obj.N)+int(obj.M)])
			except:
				pass
			obj.Y = np.asarray(obj.Y)
			obj.E = np.asarray(obj.E)
			try:
				obj.cvY = np.asarray(obj.E_covariance_variable)
			except:
				pass
			try:
				obj.sdY = np.asarray(obj.E_covariance_element.head(obj.N).iloc[:, int(obj.N):int(obj.N)+int(obj.M)])
			except:
				pass
			
			try:
				name = obj.name
			except:
				name = obj.dataset
			try:
				obj.dataset = obj.name
			except:
				pass
			try:
				l = []
				for e in range(len(obj.nodes)):	
					l.append(obj.nodes[e])
				obj.names = l
			except:
				pass
			try:
				obj.SNR_L = obj.get_SNR_L(obj)
			except:
				pass
			#all dictionary should correspond to origin after change the nodes, name
			try:
				obj.__dict__['lambda'] = list(obj.lamda)
				del obj.__dict__['lamda']
				del obj.__dict__['__model_eq__']
				del obj.name
				del obj.nodes
				del obj.E_covariance_variable
				del obj.F_covariance_variable
				del obj.E_covariance_element
				del obj.F_covariance_element
			except:
				pass
			if not isinstance(obj.P,list):
				obj.P = obj.P.tolist()
				obj.F = obj.F.tolist()
				try:
					obj.cvP = obj.cvP.tolist()
				except:
					pass
				try:			
					obj.sdP = obj.sdP.tolist()
				except:
					pass
				obj.Y = obj.Y.tolist()
				obj.E = obj.E.tolist()
				try:
					obj.cvY = obj.cvY.tolist()
				except:
					pass
				try:
					obj.sdY = obj.sdY.tolist()
				except:
					pass
				
			
			savevar = 'obj_data'
		if fending == '.json':
			a={}
			a['obj_data'] = obj.__dict__
			s = savepath + name + fending
			with open(s, 'w') as fp:
				jsondata = json.dump(a,fp)
		elif fending == '.ubj':
			a={}
			a['obj_data'] = obj.__dict__
			s = savepath + name + fending
			en = ubjson.dumpb(a)
			pickle_out = open(s,'wb')
			pickle.dump(en,pickle_out)
			pickle_out.close()	
		elif fending == '.pickle':
			a={}
			a['obj_data'] = obj.__dict__
			s = savepath + name + fending
			pickle_out = open(s,'wb')
			pickle.dump(obj,pickle_out)
			pickle_out.close()
		##can add .mat and .xml
	def load(self,savepath,name,fending,*args):
		if fending == '.json':
			s = savepath + name + fending
			with open(s) as fp:
				jsondata = json.load(fp)
				return jsondata
		elif fending == '.ubj':
			s = savepath + name + fending
			pickle_in = open(s,'rb')##s == path
			ubjdata = pickle.load(pickle_in)
			c = ubjson.loadb(ubjdata)
			return c
		elif fending == '.pickle':
			s = savepath + name + fending
			pickle_in = open(s,'rb')
			ubjdata = pickle.load(pickle_in)
			return ubjdata.__dict__
			
	'''		
	def load(*args):
		Ipath = os.getcwd()
		Ifile = []
		if len(args) == 1:
			if 1:##determine the type of args
				Ifile = args[0]
			else:##should change
				if 1:##check the file .m
					p = os.path.split(args[0])
					Ipath = p[0]
					Ifile = p[1]
				elif 0:#check the file
					Ipath = args[0]
				else:
					print('Unknown path or file')
		elif len(args) == 2:
			Ipath = args[0]
			if 1:##determine the type of args
				print('Unknown path: %s'%(Ipath))
			if 1:##detrmine the type of args
				Ifile = args[1]
			else:
				if 1:##dertermine the type of the args
					Ifile = args[1]
				else:
					print('Unknown file')
		elif len(args) > 2:
			print('wrong number of input arguments.')
		#from 151-208


		#if 0:##determine file type
			obj_datas =

				
	#from Exchange 230-244 
	'''

	def fetch(self,options,*args):
		if len(args) != 1:
			pass #db i don't know? from 244-267
		else:
		
			default_url1 = os.path.split(args[0])
			default_url2 = os.path.splitext(default_url1[1])
			options['directurl'] = default_url1[0]
			options['name'] = default_url2[0]
			options['filetype'] = default_url2[1]
			
	#		print(options['filetype'])
		a=os.path.split(options['name'])
		b=os.path.splitext(options['name'])
		junk = b[1]
		name = a[1]
		filetype = a[0]
		#return options['directurl'],options['name'],options['filetype'],junk,name,filetype
	#	print(junk)
	#	print(name)
	#	print(filetype)
	#	options['name'] #add the fileparts
		if len(options['filetype']) == 0:
		
			options['name'] =  name
			options['filetype'] = filetype
		else:

			options['name'] =  name
	#add the webread to add the function can load other type from 275-293
		if len(options['filetype']) != 0:
			if options['filetype'] =='.json':
				pass#add the webread
			elif options['filetype'] =='.xml':
				pass#add the webread
			elif options['filetype'] =='.ubj':
				pass#add the webread
			elif options['filetype'] =='.ubjson':
				pass#add the webread
			elif options['filetype'] =='.mat':
				pass#add the webread
		elif len(options['name']) == 0:
			pass#add the webread
		
	##should change 
		if len(args) != 1:
			try:
				if 'type' in options:
					tmpurl1 = options['baseurl']+options['version']+'/'+options['type']+'/'+'N'+str(options['N'])+'/'+options['name']+options['filetype']
				else:
					tmpurl1 = options['baseurl']+options['version']+'/'+'N'+str(options['N'])+'/'+options['name']+options['filetype']
				r_net = requests.get(tmpurl1)
				try:
					obj_data = json.loads(r_net.text)
				except:
					a1 = r_net._content
					a = a1.decode("utf-8")
			except:
				print('Could not fetch any data with the options')
					
		else:
			if len(options['directurl']) != 0:
				
				try:
					failed = 0
					b = input('choose the dataset or network\t')
					if b == 'network':
						a = input('input the gene number\t(10 or 50 or 100)\t')
						d = input('choose the type\t(random,scalefree,smallworld,small_scalefree)\t')
						tmpurl1 = options['directurl'][:-10]+'%s'%d+'/'+'N'+'%s'%a+'/'+options['name']+options['filetype']
						r_net = requests.get(tmpurl1)
					else:
						a = input('input the gene number\t(10 or 50 or 100)\t')
						tmpurl1 = options['directurl'][:-2]+'%s'%a+'/'+options['name']+options['filetype']
						
						r_net = requests.get(tmpurl1)
					try:				
						obj_data = json.loads(r_net.text)
					except:
						a1 =r_net._content
						a = a1.decode("utf-8")
				except:	
					failed = 1
				
				if failed:
					failed = 0
					try:
						tmpurl2 = options['baseurl']+options['directurl']+'/'+options['name']+options['filetype']
						r_net = requests.get(tmpurl2)
						try:
							obj_data = json.loads(r_net.text)
						except:
							a1 =r_net._content
							a = a1.decode("utf-8")
					except:
						failed = 1
				if failed:
					failed = 0
					try:
						tmpurl3 = options['baseurl']+options['version']+options['directurl']+options['name']+options['filetype']
						r_net = requests.get(tmpurl3)
						try:
							obj_data = json.loads(r_net.text)
						except:
							a1 =str(r_net._content)
							a = a1.decode("utf-8")
					except:
						failed = 1
						print('Remote URL does not seem to be correct\n%s\n%s\n%s\n'%(tmpurl1,tmpurl2,tmpurl3))
			else:
				
				N = re.findall('.N\d+',options['name'])
				options['N']=int(N[0][2:])
				try:
					if 'type' in options:
						type = re.findall('-[A-Za-z]+-',options['name'])
						if len(type) == 0:
							type = re.findall('-[A-Za-z]+_[A-Za-z]+-',options['name'])
						options['type'] = type[0][1:-1]
						tmpurl1 = options['baseurl']+options['version']+'/'+options['type']+'/'+'N'+str(options['N'])+'/'+options['name']+options['filetype']
	####I think not need to write this forloop in python
					else:
						tmpurl1 = options['baseurl']+options['version']+'/'+'N'+str(options['N'])+'/'+options['name']+options['filetype']
	####I think not need to write this forloop in python
					r_net = requests.get(tmpurl1)
					try:
						obj_data = json.loads(r_net.text)
					except:
						a1 = r_net._content
						a = a1.decode("utf-8")
				except:
					print('File with name %s does not seem to exist at the location %s'%(options['name'],tmpurl1))
		try:	
			if 'obj_data' in obj_data:
				return obj_data['obj_data']
		except:
			
			c=re.split('\n',a)
			for j in range(len(c)):
				e = j+1
				print('%d\t%s'%(e,c[j]))
			
	##I think the last one is not neccessary from 358-377

	

	def Load(uri=None, database=None, wildcard="*"):
		#if uri == "test":# Load default sample data
		#	uri = _uri
		#	database = _database
		E=Exchange()
		uribits = E.parse_uribits(uri,database)
		response = E.load_uri(uribits, wildcard)
		if "page" in response:# This might be bitbucket specific, more rules may have to be added for other databases
			response = E.iterate_remote_paths(response, wildcard)
		if 'obj_data' in response:
			return response['obj_data']		
		else:		
			return response

	def parse_uribits(self,URI,database):
		if database is None:
			location = urllib.parse.urlparse(URI)
		else:
			if URI is None:
				URI = ""

			if urllib.parse.urlparse(URI).scheme is not "":  # if database exist but a scheme is present in the URI, use the uri path
				database = URI
		
			location = urllib.parse.urlparse(database)
			location = location._replace(path=os.path.normpath(location.path + "/" + URI))
		if location.netloc == ".":
			URI = os.path.abspath(location.netloc + location.path)
			location = urllib.parse.urlparse(URI)
		return location


	def load_uri(self,uribits, wildcard):
		if uribits.scheme is '':
			local = Path(uribits.path)
			if local.is_dir():
				return sorted([str(d) for d in local.glob(wildcard)])

			else:
				full_uri = urllib.parse.urlunparse(uribits)
				# full_uri = Path(Path(full_uri).absolute()).as_uri()
				full_uri = Path(full_uri).absolute().as_uri()
		else:
			full_uri = urllib.parse.urlunparse(uribits)

	    # local = Path(urllib.parse.urlparse(full_uri)[2])

		try:
			if not full_uri.endswith(".json"):
				full_uri = full_uri + "/"

			with urllib.request.urlopen(full_uri) as URI:
				uri_string = URI.read().decode()

			return json.loads(uri_string)

		except urllib.error.URLError as e:
			#print("Path: {}\n".format(full_uri))
			#print(e.reason)
			return None


	def iterate_remote_paths(self,loaded, wildcard):
		if wildcard == "*":
			wildcard = ".*"
		paths = [p["path"] for p in loaded["values"] if ((p["path"].endswith(".json") and re.search(wildcard, p["path"])) or p["type"] == 'commit_directory')]

		while "next" in loaded:
			with urllib.request.urlopen(loaded["next"]) as URI:
				uri_string = URI.read().decode()
				loaded = json.loads(uri_string)

			paths.extend([p["path"] for p in loaded["values"] if ((p["path"].endswith(".json") and re.search(wildcard, p["path"])) or p["type"] == 'commit_directory')])

		return paths
			
	##I think the last one is not neccessary from 358-377

	

