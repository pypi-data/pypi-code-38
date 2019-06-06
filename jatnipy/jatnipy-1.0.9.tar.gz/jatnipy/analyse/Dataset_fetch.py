import json, requests
from datastruct.Exchange_fetch import fetch
def fetch2(*args):
	options={
		'directurl':'',
		'baseurl':'https://bitbucket.org/api/1.0/repositories/sonnhammergrni/gs-datasets/raw/',
		'version':'master',
		'N':'10',
		'name':'Nordling-ID1446937-D20150825-N10-E15-SNR3291-IDY15968',
		'filetype':'.json',
		}
	if len(args) != 0:
		try:
			default_file = args[0]
			obj_data = fetch(options,default_file)		
			return obj_data
		except:
			default_file = 'Nordling-ID1446937-D20150825-N10-E15-SNR3291-IDY15968.json'
			obj_data = fetch(options,default_file)
			data = obj_data
			return data
	else:
		default_url =  options['baseurl']+options['version']+'/'+'N'+str(options['N'])+'/'
		obj_data = fetch(options,default_url)		
		data = obj_data		
		return data
