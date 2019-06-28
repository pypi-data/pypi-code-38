import time
import pandas as pd
import lgblkb_tools.log_support as logsup
import multiprocessing as mp
import types
from typing import List
import uuid
import lgblkb_tools.scheduling.dbader_schedule as schedule


# region scheduled_task:
class ConveyorPosition:
	
	def __init__(self,job_func,max_process_count=1):
		self.job_func=job_func
		self.max_process_count=max_process_count
		self.current_process_count=0
		self.processes=list()
	
	def check_for_completed_processes(self):
		for p in self.processes:
			if not p.is_alive():
				p.join()
				p.terminate()
				self.processes.remove(p)
				self.current_process_count-=1
	
	def start_process(self,target,*args,name=None,**kwargs):
		if self.current_process_count<self.max_process_count:
			# simple_logger.info('Starting process...')
			p=mp.Process(target=target,args=args,kwargs=kwargs,name=name)
			p.start()
			self.processes.append(p)
			self.current_process_count+=1

def queue_generator(queue: mp.Queue,func,control_desk,output=None):
	if output is None:
		resultant_status,data=func()
	else:
		resultant_status,data=output
	for i,row in control_desk.iterrows():
		if func==row.gen_func:
			if resultant_status==row.ret_stat or (type(row.ret_stat) is types.FunctionType and row.ret_stat(resultant_status)):
				logsup.logger.info('resultant_status: %s,data: %s',resultant_status,data)
				queue.put((row.name,data))

def queue_processor(queue: mp.Queue,control_desk):
	# simple_logger.info('control_desk: %s',control_desk)
	row_name,data=queue.get()
	logsup.logger.pop()
	try:
		func=control_desk.loc[row_name].doer_func
		output=func(data)
		if output is None: return
		queue_generator(queue,func,control_desk,output)
	
	except Exception as e:
		logsup.logger.error(str(e),exc_info=True)
		logsup.logger.inform(str(e),exc_info=True)
		ScheduledTask.on_process_error(data,e)
		raise
	pass

class Conveyor:
	
	def __init__(self,max_queue_size=1,name=''):
		self.control_desk=pd.DataFrame(columns=['gen_func','ret_stat','doer_func'])
		self.queue=mp.Queue()
		self.max_q_size=max_queue_size
		self.positions: List[ConveyorPosition]=list()
		self.funcs_to_run_at_start=set()
		self.has_doer=False
		self.name=name or uuid.uuid4()
	
	def add_control_row(self,*args):
		self.control_desk.loc[self.control_desk.shape[0]]=args
	
	def add_data_provider(self,scheduled_job: schedule.Job,func,run_at_start=True):
		if run_at_start: self.funcs_to_run_at_start.add(func)
		self.add_control_row(func,True,None)
		scheduled_job.do(queue_generator,self.queue,func,self.control_desk).tag(self.name)
		return self
	
	def add_return_status_info(self,some_func,returns_status=True):
		for i,row in self.control_desk.iterrows():
			if some_func==row.gen_func:
				if row.ret_stat is True:
					row.ret_stat=returns_status
					return
		self.add_control_row(some_func,returns_status,None)
	
	def add_doer_func(self,doer_func,max_workers=1):
		# self.control_desk.loc[self.control_desk['doer_func'].isnull() & (self.control_desk['ret_stat'].notnull()),'doer_func']=doer_func
		check1=(self.control_desk['doer_func'].isnull()&self.control_desk['ret_stat'].notnull())
		if check1.any():
			self.control_desk.loc[check1,'doer_func']=doer_func
		else:
			self.control_desk.loc[self.control_desk['doer_func'].isnull()&
			                      (self.control_desk['ret_stat'].isnull()),
			                      ['ret_stat','doer_func']]=True,doer_func
		# print(self.control_desk)
		# raise NotImplementedError
		# for i,row in self.control_desk.iterrows():
		# 	if row.ret_stat is None:
		# 		self.add_return_status_info(row.gen_func)
		# if row.doer_func is None:
		# 	if row.ret_stat is not None:
		# 		row.doer_func=doer_func
		
		#
		# if self.has_doer:
		# 	if row.doer_func is None and row.ret_stat is None:
		# 		row.doer_func=doer_func
		# 		row.ret_stat=True
		# else:
		# 	if row.doer_func is None and row.ret_stat is not None:
		# 		row.doer_func=doer_func
		self.__add_position(doer_func,max_workers=max_workers)
		self.has_doer=True
	
	def __add_position(self,worker_func,max_workers=1):
		conv_position=ConveyorPosition(job_func=worker_func,max_process_count=max_workers)
		self.positions.append(conv_position)
	
	def run_start_funcs(self):
		for func in self.funcs_to_run_at_start:
			queue_generator(self.queue,func,self.control_desk)
	
	def run_pending(self):
		# simple_logger.info('conveyor: %s, qsize: %s',self.name,self.queue.qsize())
		for conv_pos in self.positions:
			conv_pos.check_for_completed_processes()
			conv_pos.start_process(queue_processor,self.queue,self.control_desk)
		if self.queue.qsize()<self.max_q_size:
			schedule.run_pending(self.name)
		pass
# endregion

class ScheduledTask:
	
	def __init__(self,parent_task=None,filename=None,log_timing_opts=None,**setup_kwargs):
		self.parent_task: ScheduledTask=parent_task
		self.filename=filename  # or self.parent_task.filename
		if not self.filename is None:
			# self.create_log_file(level=logsup.INFORM,**(log_timing_opts or {}))
			logsup.logger.create(self.filename,self.__class__.__name__)\
				.get_filepath('main',include_depth=1,include_datetime=2)\
				.add_timed_handler(level=logsup.INFORM,**(log_timing_opts or {}),
			                       log_format=logsup.simple_fmt_no_level)
		else: self.filename=self.parent_task.filename
		# super(scheduled_task,self).__init__(self.__class__.__name__,logsup.log_folder.create(self.__class__.__name__),level=logsup.INFORM,**(log_timing_opts or {}))
		# self.get_filepath('main',include_depth=1,include_datetime=2).add_handler()
		if parent_task is not None: parent_task.child_tasks.append(self)
		self.child_tasks=list()
		self.conveyors: List[Conveyor]=list()
		self.current_conveyor: Conveyor=None
		self.setup(**setup_kwargs)
	
	def setup(self,**kwargs):
		pass
	
	# def create_log_file(self,**kwargs):
	# 	assert self.filename is not None
	# 	logsup.logger.create_log_file(self.filename,process=self.__class__.__name__,**kwargs)
	def log_create(self,*child_folders,**info_kwargs):
		return logsup.logger.create(self.filename,self.__class__.__name__,*child_folders,**info_kwargs)
	
	def check_for(self,func,scheduler,check_at_start=True,**kwargs):
		if self.current_conveyor is None or self.current_conveyor.has_doer:
			c=Conveyor(**dict(dict(name=f"Conveyor-{len(self.conveyors)}"),**kwargs))
			self.conveyors.append(c)
			self.current_conveyor=c
		# self.checker_functions.append(func)
		# self.checker_functions[q]=func
		# self.conveyor_queues[self.current_conveyor].append(q)
		self.current_conveyor.add_data_provider(scheduled_job=scheduler,func=func,run_at_start=check_at_start)
		return self
	
	def when(self,some_func=None,return_status=True):
		if some_func is None: some_funcs=self.current_conveyor.control_desk['gen_func'].tolist()
		else: some_funcs=[some_func]
		if self.current_conveyor.has_doer:
			for some_func in some_funcs:
				self.current_conveyor.add_control_row(some_func,return_status,None)
		else:
			for func in some_funcs:
				# assert func in gen_funcs,"The function should be in the current conveyor's list of generator functions"
				self.current_conveyor.add_return_status_info(some_func=func,returns_status=return_status)
		return self
	
	def do(self,func,workers_count=1):
		self.current_conveyor.add_doer_func(func,max_workers=workers_count)
		self.current_conveyor.add_control_row(func,None,None)
		return self
	
	def run(self,*tasks,sleep_time=1):
		all_tasks=[self,*tasks,*self.child_tasks]
		for task in all_tasks:
			for conveyor in task.conveyors: conveyor.run_start_funcs()
		logsup.logger.info('Start of the main loop.')
		while True:
			for task in all_tasks:
				for conveyor in task.conveyors:
					conveyor.run_pending()
			time.sleep(sleep_time)
	
	@staticmethod
	def on_process_error(data,exception):
		logsup.logger.exception("Exception caught when processing data:\n%s\nException text:\n%s",data,str(exception))

def main():
	pass

if __name__=='__main__':
	main()
