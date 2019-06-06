#from Exchange 230-244 
import os 
import re
import json
import requests
import re
def fetch(options,*args):
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
	junk = a[0]	
	name = a[1]
	filetype = b[1]
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
				tmpurl1 = options['directurl']+options['name']+options['filetype']
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
					tmpurl2 = options['baseurl']+options['directurl']+options['name']+options['filetype']
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
			N = re.findall('.N\d\d',options['name'])
			options['N']=int(N[0][2:])
			try:
				if 'type' in options:
					type = re.findall('-\w\w\w\w\w\w-',options['name'])
					if len(type) == 0:
						type = re.findall('-\w\w\w\w\w\w-',options['name'])
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
		return a
##I think the last one is not neccessary from 358-377

	

