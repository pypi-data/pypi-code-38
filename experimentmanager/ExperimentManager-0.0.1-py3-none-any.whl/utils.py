import copy
import inspect
import logging
from datetime import datetime

import numpy as np

formatter = logging.Formatter('%(asctime)s - %(levelname)s -- %(message)s')

def setup_logger(name, log_file = None, level=logging.INFO, format = True):
	''' Create a logger with an optional file to save to.
	
	Format bool specifies wether the logs should be formatted or not.
	'''

	if log_file is not None:
		handler = logging.FileHandler(log_file)
		logger = logging.Logger(name)
		if format:
			handler.setFormatter(formatter)
			logger.setLevel(level)
		logger.addHandler(handler)

	else:
		logger = logging.Logger(name)
		
	return logger
	
def _get_options(main_dict, run_dict = None, prefixes = None):
	''' Merge a main_dict and a specific run_dic using prefixes. 
	
	The run_dict has precendence over the main_dict in case of equal keys.	
	
	This version keeps the structure of the original options dict when applying prefixes. We chose to keep the version that erases structure.
	'''
	
	options = {}
	if run_dict is not None:
		options = copy.deepcopy(run_dict)
	insert_queue = [(options,main_dict)]
	while len(insert_queue)>0:
		host, guest = insert_queue.pop(0)
		for key in guest:
			if not key in host:
				host[key] = copy.deepcopy(guest[key])
			elif isinstance(host[key],dict) and isinstance(guest[key],dict):
				insert_queue.append((host[key],guest[key]))
			else:
				# types do not match, the host should have precedence
				pass
				
	if prefixes is None:
		return options
	
	# We need to pop the unwanted options
	
	# Depth-first search to clean out the unwanted options
	queue = [ (None,options) ]
	while len(queue)>0:
	
		current_prefix,current = queue.pop(0)
	
		print('entering current : {}'.format(current))
		keys_to_pop = []
		
		for key in current:
			
			child_prefix = key if current_prefix is None else '.'.join([current_prefix,str(key)])
			print('child prefix for key {} : {}'.format(key,child_prefix))
		
			keep = False
			for prefix in prefixes:
				if prefix[:len(child_prefix)] == child_prefix:
					keep = True
					break
					
			if keep and isinstance(current[key],dict):
				queue.append( (child_prefix,current[key]) )
			if not keep:
				keys_to_pop.append(key)
		
		print('keys to pop {} for current {}'.format(keys_to_pop,current))
		for key in keys_to_pop:
			current.pop(key)
				
				
	return options

def get_options(main_dict, run_dict = None, prefixes = None):
	''' Merge a main_dict and a specific run_dic using prefixes. 
	
	The run_dict has precendence over the main_dict in case of equal keys.	
	
	This version keeps the structure of the original options dict when applying prefixes. We chose to keep the version that erases structure.
	'''
	
	options = {}
	if run_dict is not None:
		options = copy.deepcopy(run_dict)
	insert_queue = [(options,main_dict)]
	while len(insert_queue)>0:
		host, guest = insert_queue.pop(0)
		for key in guest:
			if not key in host:
				host[key] = copy.deepcopy(guest[key])
			elif isinstance(host[key],dict) and isinstance(guest[key],dict):
				insert_queue.append((host[key],guest[key]))
			else:
				# types do not match, the host should have precedence
				pass
				
	if prefixes is None:
		return options
	
	# We need to recover the requested elements
	new_options = {}
	prefixes = [ prefix.split('.') for prefix in prefixes ]
	# CLEAN FOR REDUNDANT PREFIXES ?
	# This version should check that there will not be two same keys in the newdict
	for prefix in prefixes:
		current = options
		for key in prefix:
			if key == '':
				if prefix.index('')!=len(prefix)-1:
					raise Exception('Double points (..) in the a prefix, does not make sense')
				for subkey in current[key]:
					new_options[subkey] = current[subkey]
				current = None
				break
			elif key in current:
				current = current[key]
		if current is not None:
			new_options[prefix[-1]] = current
			
	return new_options
	
	
	
	

def pprint_dict(d,limit = 2,indent = 4, output = 'print', name = None):
	''' Pretty print (or return the pretty print string of) a dictionary with the option to limit the displaed length of arrays and lists
	'''
	cout = ''
	indent = ' '*indent
	root_name = name if name is not None else 'root'
	print_queue = [(root_name,d,0)]
	while len(print_queue)>0:
		name,value,depth = print_queue.pop(-1)
		if isinstance(value,dict):
			for key in value:
				print_queue.append((key,value[key],depth+1))
			cout += indent*depth + '{} :'.format(name) + '\n'
			continue
		if isinstance(value,list):
			value = np.array(value)
		if isinstance(value,np.ndarray):
			if value.ndim > 1:
				value = value[ tuple([slice(0,limit) for i in range(value.ndim)]) ]
			value = value.tolist()
		cout += indent*depth + '{} : {}'.format(name,value) + '\n'
	if output == 'print':
		print(cout)
	elif output == 'return':
		return cout
	else:
		raise Exception('Output mode was not understood')

def default_args(function):
	''' Inspect the default arguments of a function.	
	'''
	pars = inspect.signature(function).parameters
	return {key : pars[key].default for key in pars.keys()}

def timestamp():
	''' Generate a custom timestamp.
	'''
	return datetime.now().strftime("%Hh%M  %d %m %Y")

def datestamp():
	''' Generate a custom timestamp.
	'''
	return datetime.now().strftime("%d %m %Y")


if __name__ == "__main__":

		main_dict = {
			"name" : "Victor",
			"value" : 100,
			"towns": {
				"0" : "Paris",
				"1" : "Bxls"
			},
			"info":{
				"rd":{
					"fav number" : 5,
					"fav place":None
				},
				"rd2":{
					"I am here?" : True
				}
			}
		}

		run_dict = {
			"info" : {
				"rd" :{
					"fav place": "Paris"
				}
			}
		}

		prefixes = None

		pprint_dict(get_options(main_dict, run_dict, prefixes))

		prefixes = ['name','info.rd','info','towns.0']

		pprint_dict(get_options(main_dict, run_dict, prefixes))
