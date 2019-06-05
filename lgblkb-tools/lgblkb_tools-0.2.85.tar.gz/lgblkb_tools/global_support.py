import hashlib
import multiprocessing as mp
import signal
import subprocess
import sys
import time
import types
from datetime import date,timedelta,datetime
from enum import Enum
from functools import partial
from pprint import pformat
from typing import Iterable,Sized

import dateutil.parser
import numpy as np
import pandas as pd
import ruamel.yaml as raml
from sklearn.preprocessing import MinMaxScaler

from . import log_support as logsup
from .helpers import constrained_sequence
from .locations import *
from .folder_utils import Folder

# pd.set_option('max_colwidth',40)
# pd.set_option('expand_frame_repr',False)
pd.set_option('display.max_colwidth',-1)

def func_has_classarg(func,args):
	has_classarg=False
	if args:
		funcattr=getattr(args[0],func.__name__,None)
		if funcattr is not None and hasattr(funcattr,'__self__'):
			has_classarg=True
	return has_classarg

def reprer(obj):
	if isinstance(obj,dict): d=obj
	else: d=obj.__dict__
	body=[f"{k:<20}: {('None' if v is None else v)}" for k,v in d.items() if k[0]!='_']
	if body: delim="\n"
	# else: body,delim=["Expired!"]," "
	else: body,delim=['Empty']," "
	return f'"{obj.__class__.__name__}" item:'+delim+"\n".join(body)

class AutoName(Enum):
	
	def _generate_next_value_(name,start,count,last_values):
		return name

def run_shell(*args,non_blocking=False,chdir=None,with_popen=False,ret_triggers=None,**kwargs):
	chdir=chdir or os.getcwd()
	normal_dir=os.getcwd()
	os.chdir(chdir)
	
	if non_blocking:
		subprocess.Popen(args,stdout=subprocess.PIPE,**kwargs)
	else:
		#output=subprocess.run(args,stdout=subprocess.PIPE,**kwargs).stdout.decode()
		#output=subprocess.run(args,stdout=subprocess.PIPE,**kwargs).stdout.decode()
		if with_popen:
			process=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=os.setsid)
			regular_termination=True
			nextline=''
			while regular_termination:
				nextline=process.stdout.readline().decode()
				# print('nextline:',nextline)
				if nextline=='' and process.poll() is not None:
					break
				if ret_triggers:
					for ret_trigger in ret_triggers:
						if ret_trigger in nextline:
							regular_termination=False
							break
				logsup.logger.debug(nextline)
				# sys.stdout.write(nextline)
				sys.stdout.flush()
			if regular_termination:
				output=process.communicate()[0]
				exitCode=process.returncode
				if exitCode!=0:
					raise Exception(args,exitCode,output)
			else:
				logsup.logger.info(r'Manual process termination triggered with line:\n%s',nextline)
				logsup.logger.debug('Killing process: %s',process.pid)
				os.killpg(os.getpgid(process.pid),signal.SIGTERM)
				raise Exception('Manual process termination.')
		else:
			subprocess.run(args,stdout=subprocess.PIPE,**kwargs).stdout.decode()
	os.chdir(normal_dir)

def period_within(days=None,start_date=None,end_date=None):
	if isinstance(start_date,str): start_date=dateutil.parser.parse(start_date)
	if isinstance(end_date,str): end_date=dateutil.parser.parse(end_date)
	if days is not None:
		if start_date is not None:
			end_date=start_date+timedelta(days=days)
		elif end_date is not None:
			start_date=end_date-timedelta(days=days)
		else:
			end_date=date.today()
			start_date=end_date-timedelta(days=days)
	else:
		end_date=end_date or date.today()
	return start_date,end_date

def datetime_within(start=None,end=None,**timedelta_opts):
	if timedelta_opts:
		if start is not None:
			end=start+timedelta(**timedelta_opts)
		elif end is not None:
			start=end-timedelta(**timedelta_opts)
		else:
			end=datetime.now()
			start=end-timedelta(**timedelta_opts)
	else:
		end=end or datetime.now()
	return start,end

def try_to_do(func,*args,check_success=None,max_attempts=5,max_wait_seconds=0,**kwargs):
	def success_checker(x):
		assert x is not None
		return x
	
	if check_success is None: check_success=success_checker
	max_attempts=max(max_attempts,1)
	if max_wait_seconds:
		waiting_times=constrained_sequence(max_attempts,lambda x:np.exp(x/4))
		waiting_times=MinMaxScaler((0,max_wait_seconds))\
			.fit_transform(np.array(waiting_times).reshape(-1,1))
	else: waiting_times=[0]*max_attempts
	logsup.logger.debug('Trying to accomplish "%s" ...',func.__name__)
	wait_time=iter(waiting_times)
	for i in range(max_attempts):
		time_to_wait=next(wait_time)
		if time_to_wait!=0:
			logsup.logger.info('Sleeping for %s sec.',time_to_wait)
			time.sleep(time_to_wait)
		logsup.logger.debug('Attempt #%s.',i+1)
		out=func(*args,**kwargs)
		# simple_logger.debug('check_success:')
		if check_success(out):
			logsup.logger.debug('Succeeded.')
			return out
		else:
			logsup.logger.info('Attempt #%s failed.',i+1)
	return False

def run_until_victory(func,retry_timeout,*args,**kwargs):
	manager=mp.Manager()
	res_dict=manager.dict()
	args=[res_dict,*args]
	count=0
	while not res_dict:
		count+=1
		logsup.logger.info(f'Starting "{func.__name__}". Counter: {count}')
		p=mp.Process(target=func,args=args,kwargs=kwargs)
		p.start()
		p.join(retry_timeout)
		p.terminate()
	return res_dict

def run_processes_with_map_async(proc_func,payload: list,proc_count=None):
	proc_count=proc_count or (mp.cpu_count()-1)
	with mp.Pool(proc_count) as p:
		results=list()
		p.map_async(proc_func,payload,callback=lambda x:results.extend(x))
		p.close()
		p.join()
	return results

# def run_reactive_worker(listening_func,job_func,output_func=None,worker_count=1,interval=10):
# 	with concurrent.futures.ProcessPoolExecutor(worker_count) as executor:
# 		rx.Observable.interval(interval).from_iterable(listening_func()).flat_map(
# 			lambda *args,**kwargs:executor.submit(job_func,*args,**kwargs)
# 			).subscribe(output_func)

# class ReactiveTask(ABC):
#
# 	def __init__(self,filename,interval=10):
# 		self.filename=filename
# 		self.interval=interval
#
# 	def sleep(self):
# 		time.sleep(self.interval)
#
# 	# def create_log_file(self,info_opts=None,**kwargs):
# 	# 	logsup.logger.create_log_file(self.filename,dict(process=self.__class__.__name__,**(info_opts or {})),**kwargs)
#
# 	def data_generator(self):
# 		raise NotImplementedError
#
# 	def data_processor(self,data):
# 		raise NotImplementedError
#
# 	def post_processor(self,output_data):
# 		pass
#
# 	def run(self,worker_count=1):
# 		with concurrent.futures.ThreadPoolExecutor(worker_count) as executor:
# 			# timing_observable=rx.Observable.interval(int(self.interval*1e3))
# 			# timing_observable.from_(self.data_generator()).flat_map(lambda data:executor.submit(run_processes_with_map_async,self.data_processor,payload=[data],proc_count=1))\
# 			# 	.subscribe(self.post_processor)
# 			rx.Observable.from_iterable(iter(self.data_generator()))\
# 				.flat_map(lambda data:executor.submit(
# 				run_processes_with_map_async,self.data_processor,payload=[data],proc_count=1))\
# 				.subscribe(self.post_processor)
# 			# rx.Observable\
# 			# 	.zip(timing_observable,processor_observable,lambda t,output_data:output_data)\
# 			# 	.flat_map(lambda data:executor.submit(run_processes_with_map_async,self.data_processor,payload=[data],proc_count=1))\
# 			# 	.subscribe(self.post_processor)
# 			input('The run finished. Give any input: ')

def infiterate(iter_obj,max_iter_count=None,next_getter=None,inform_count=8,on_inform=None):
	if on_inform is None: on_inform=lambda *args,**kwargs:True
	if isinstance(iter_obj,int):
		an_iterable,iter_count=range(iter_obj),iter_obj
	else:
		an_iterable=iter_obj
		if isinstance(iter_obj,Sized):
			iter_count=len(iter_obj)
		else:
			assert max_iter_count
			iter_count=max_iter_count
	max_iter_count=max_iter_count or iter_count
	if next_getter is None: next_getter=lambda _obj:_obj
	for i,obj in enumerate(an_iterable):
		if i%(max_iter_count//inform_count)==0:
			on_inform()
			logsup.logger.info('%d%%, i=%d',i/(max_iter_count-1)*100,i)
		
		obj=next_getter(obj)
		yield obj
		if i==max_iter_count-1:
			on_inform()
			logsup.logger.info('%d%%, i=%d',i/(max_iter_count-1)*100,i)
			return

class ParallelTasker:
	
	def __init__(self,func,*args,**kwargs):
		self.partial_func=partial(func,*args,**kwargs)
		self.queue=mp.Queue()
		self._total_proc_count=0
		pass
	
	def set_run_params(self,**kwargs):
		val_lengths={len(v) for v in kwargs.values()}
		assert len(val_lengths)==1
		val_length=val_lengths.pop()
		
		for i in range(val_length):
			self.queue.put((i,{k:v[i] for k,v in kwargs.items()}))
			self._total_proc_count+=1
		# logsup.logger.info('self._total_proc_count: %s',self._total_proc_count)
		
		return self
	
	def __process_func(self,queue,common_list):
		i,kwargs=queue.get()
		result=self.partial_func(**kwargs)
		common_list.append([i,result])
	
	@staticmethod
	def __join_finished_processes(active_procs,sleep_time):
		while True:
			# simple_logger.info('Process queue is full. Searching for finished processes.')
			for p in active_procs:
				if not p.is_alive():
					# logsup.logger.info('Finished process found. Joining it.')
					active_procs.remove(p)
					p.join()
					# p.terminate()
					# logsup.logger.info('Process successfully removed.')
					return
			time.sleep(sleep_time)
	
	def run(self,workers_count=None,sleep_time=1.0):
		workers_count=min(mp.cpu_count()-1,workers_count or self._total_proc_count)
		manager=mp.Manager()
		common_list=manager.list()
		processes=[mp.Process(target=self.__process_func,args=(self.queue,common_list)) for _ in range(self.queue.qsize())]
		active_procs=list()
		while True:
			# logsup.logger.info('loop begins')
			if len(processes)==0:
				# logsup.logger.info('Waiting for the last jobs to finish.')
				for active_p in active_procs:
					active_p.join()
				break
			if len(active_procs)<workers_count:
				# logsup.logger.info('Adding a process')
				proc=processes.pop()
				proc.start()
				active_procs.append(proc)
			else:
				self.__join_finished_processes(active_procs,sleep_time)
			time.sleep(sleep_time)
		return [item[1] for item in sorted(common_list,key=lambda x:x[0])]

def try_wrapper(max_tries=12,max_sleep_time=600,pass_error=True,on_pass_return=None):
	# if pass_error: assert on_pass_return is not None
	if max_tries in [None,'inf']: max_tries=float('inf')
	
	def decorator(func):
		def wrapper(*args,**kwargs):
			try_count=1
			while True:
				try:
					out=func(*args,**kwargs)
					if try_count!=1:
						logsup.logger.info('Succeeded at try #%d',try_count)
					break
				except Exception as e:
					if max_tries and max_tries<=try_count:
						logsup.logger.info('Reached max. number of tries (%d).',try_count)
						if pass_error: return on_pass_return
						else: raise
					try_count+=1
					if max_tries==float('inf'): sleep_time=max_sleep_time
					else: sleep_time=max_sleep_time/(1+np.exp(-(try_count-1-max_tries/2)))
					
					logsup.logger.error('error: %s',str(e),exc_info=True)
					logsup.logger.info('Sleeping for %.3f seconds.',sleep_time)
					time.sleep(sleep_time)
					logsup.logger.info('Try #%d',try_count)
			
			return out
		
		return wrapper
	
	return decorator

_try_wrapper_attrs="_obj _try_wrapper_args _try_wrapper_kwargs".split(' ')

class TryWrapper:
	
	def __init__(self,obj,*try_wrapper_args,**try_wrapper_kwargs):
		self._obj=obj
		self._try_wrapper_args=try_wrapper_args
		self._try_wrapper_kwargs=try_wrapper_kwargs
	
	def _func_wrapper(self,func):
		return func
	
	def __getattr__(self,item):
		if item in _try_wrapper_attrs: return self.__dict__[item]
		else:
			attr=getattr(self._obj,item)
			if type(attr) is types.MethodType:
				return try_wrapper(*self._try_wrapper_args,**self._try_wrapper_kwargs)(self._func_wrapper(attr))
			else: return attr

class GenericObjContainer:
	
	def __init__(self,obj):
		self.obj=obj

class ReactiveObj(GenericObjContainer):
	
	def apply(self,func):
		if isinstance(self.obj,Iterable):
			return list(map(func,self.obj))
		else: return func(self.obj)

class Mapper(GenericObjContainer):
	
	def map(self,func):
		return list(map(func,self.obj))

class AttributeItemGetterSetter:
	
	def __init__(self,obj):
		self.obj=obj
	
	def __getattr__(self,item):
		return AttributeItemGetterSetter(self.obj[item])
	
	def __getitem__(self,item):
		return AttributeItemGetterSetter(self.obj[item])
	
	def __setitem__(self,key,value):
		self.obj[key]=value
	
	def __repr__(self):
		return f"AttributeItemGetterSetter({pformat(self.obj)})"
	
	def __call__(self,*args,**kwargs):
		return self.obj

class AttributeItemSetter:
	
	def __init__(self,obj):
		self.obj=obj
	
	def __setattr__(self,key,value):
		self.obj[key]=value
	
	def __setitem__(self,key,value):
		self.obj[key]=value
	
	def __repr__(self):
		return f"AttributeItemSetter({pformat(self.obj)})"

class ConfigReader(AttributeItemGetterSetter):
	
	def __init__(self,config_path):
		self.config_path=config_path
		self.yaml=raml.YAML()
		self.yaml.default_flow_style=False
		super(ConfigReader,self).__init__(self.__load())
	
	def __load(self):
		return self.yaml.load(open(self.config_path))
	
	def update(self):
		self.yaml.dump(self.obj,open(self.config_path,'w'))
		return self.__load()

def md5(filepath):
	hash_md5=hashlib.md5()
	with open(filepath,"rb") as f:
		for chunk in iter(lambda:f.read(4096),b""):
			hash_md5.update(chunk)
	return hash_md5.hexdigest()

def get_md5(text):
	return hashlib.md5(str(text).encode('utf-8')).hexdigest()

def run_command(cmd):
	logsup.logger.debug('cmd:\n%s',cmd)
	process=subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
	for c in iter(lambda:process.stdout.read(1),b''):  # replace '' with b'' for Python 3
		sys.stdout.write(c.decode(sys.stdout.encoding,errors='ignore'))

if __name__=='__main__':
	pass
