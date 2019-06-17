import os
import sys
import threading
import time
import traceback

import superjson

from ExperimentManager.utils import pprint_dict, timestamp


class Run():
	''' A simple container class. Used to capture basic information about a run. 
	
	The actual run metrics and saving utilities are managed globally by an ExperimentManager.	
	'''

	def __init__(self,run_id, name,command, logger, info_logger, run_dir, save_dir, metrics_dir, tb_dir):
	
		self.command = command
		"""The command that should be run"""
	
		self.id = run_id
		"""The ID of this run as assigned by the experiment Manager"""

		self.name = name
		
		self.run_dir = run_dir
		
		self.save_dir = save_dir
		
		self.metrics_dir = metrics_dir

		self.tb_dir = tb_dir
		
		self.logger = logger

		self.info_logger = info_logger

		self.results = {}

		self.status = None

		self.calls_info = {}
		self.calls_lock = threading.Lock()
		
	def increment_calls(self):
		''' A safe way of increment the number of calls that this run performed. Will return the increment value.
		'''
		try:
			self.calls_lock.acquire()
			id = len(self.calls_info)
			self.calls_info[id] = {'start_time':None,'stop_time':None,'duration':None}

		except Exception as err:
			traceback.print_tb(err.__traceback__)
			print('Error type {} : {}'.format(sys.exc_info()[0],sys.exc_info()[1]))
			raise Exception('')
		
		finally:
			self.calls_lock.release()

		return id
		
		
	def __call__(self,*args,**kwargs):
		''' Call the run's command while keeping track of the run time and automatically logging the event.
		'''

		# Initiating the run
		self.status = 'Running'
		call_id = self.increment_calls()
		self.calls_info[call_id]['start_time'] = timestamp()
		self.logger.info('({}) Starting call number {} with *args {} and **kwargs {}'.format(self.calls_info[call_id]['start_time'],call_id,args,kwargs))

		# Performing the actual run
		_start_time = time.time()
		self.results[call_id] = self.command(*args,**kwargs)
		_stop_time = time.time()

		# Logging stats and info
		self.calls_info[call_id]['stop_time'] = timestamp()
		self.logger.info('({}) Finished call number {}'.format(self.calls_info[call_id]['stop_time'],call_id))
		self.calls_info[call_id]['duration'] = round(_stop_time - _start_time,3)
		self.status = 'Finished'
		self.info_logger.info('({}) Starting call number {} with *args {} and **kwargs {}'.format(self.calls_info[call_id]['start_time'],call_id,args,kwargs))
		self.info_logger.info(pprint_dict(self.get_config(),output='return',name='Run config after call {}'.format(call_id)))
			
		# Useful to have for the caller!
		return call_id
		
	def get_config(self):
		''' Get a config file describing the current state of the Run instance.
		'''
		config = { key : getattr(self,key) for key in self.__dict__  if key not in ['logger','command']}
		config['logger'] = self.logger.name
		config['command'] = self.command.__name__
		return config
