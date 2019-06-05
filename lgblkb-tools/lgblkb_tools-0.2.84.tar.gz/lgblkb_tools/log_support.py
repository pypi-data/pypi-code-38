from typing import Union
import sys
from timeit import default_timer as timer
import logging
from logging.handlers import TimedRotatingFileHandler as TimedHandler
import logging.handlers as loghandlers
import functools
from python_log_indenter import IndentedLoggerAdapter
from datetime import datetime


from .locations import get_name,create_path,InfoDict
from colorlog import ColoredFormatter

def create_filter(filter_func,*args,filter_name='',**kwargs):
	class CustomFilter(logging.Filter):
		
		def filter(self,record):
			return filter_func(record.getMessage(),*args,**kwargs)
	
	return CustomFilter(filter_name)

logging.INFORM=INFORM=369
logging.addLevelName(INFORM,"INFORM")

def inform(self,message,*args,**kws):
	# Yes, logger takes its '*args' as 'args'.
	if self.isEnabledFor(INFORM):
		self._log(INFORM,message,args,**kws)

logging.Logger.inform=inform

# region level_mapper:
level_mapper=dict()
level_mapper[logging.DEBUG]=lambda some_logger:some_logger.debug
level_mapper[logging.INFO]=lambda some_logger:some_logger.info
level_mapper[logging.WARNING]=lambda some_logger:some_logger.warning
level_mapper[logging.ERROR]=lambda some_logger:some_logger.error
level_mapper[logging.CRITICAL]=lambda some_logger:some_logger.critical
level_mapper[logging.INFORM]=lambda some_logger:some_logger.inform

# endregion
#todo:Group log files into folder. After expiration, delete folder (if left empty after cleaning).


class TheLogger(IndentedLoggerAdapter):
	
	def __init__(self,name,folder_path='',level=logging.DEBUG,log_format: str = None,to_stream=True,**kwargs):
		
		self.base_log_folder: Folder=Folder(folder_path) if folder_path else None
		super(TheLogger,self).__init__(logging.Logger(name,level),**dict(dict(spaces=1,indent_char='|--'),**kwargs))
		
		# IndentedLoggerAdapter.__init__(self,logging.Logger(name,level),**dict(dict(spaces=1,indent_char='|---')))
		# Folder.__init__(self)
		
		# super(IndentedLoggerAdapter,self).__init__(logging.Logger(name,level),**dict(dict(spaces=1,indent_char='|---')))
		# super(Folder,self).__init__()
		# super(TheLogger,self).__init__(**kwargs))
		# Folder.__init__(TheLogger,self.base_log_folder.path)
		# self.formatter=logging.Formatter(log_format or color_log_format)
		# IndentedLoggerAdapter.__init__(self,logging.Logger(name,level),**dict(dict(spaces=1,indent_char='|---'),**kwargs))
		# super(Folder,self).__init__()
		
		_log_format=(log_format or nocolor_log_format).replace(color_info,'')
		self.formatter=logging.Formatter(_log_format)
		if to_stream:
			stream_format=(log_format or color_log_format)  #.replace(color_info,'')
			stream_formatter=ColoredFormatter(stream_format)
			stream_handler=logging.StreamHandler()
			# stream_handler.setLevel(level)
			# stream_handler.setFormatter(logging.Formatter(stream_format))
			self.add_handler(stream_handler,formatter=stream_formatter)
		self.current_log_folder: Folder=self.base_log_folder
		self.log_path=''
	
	def add_handler(self,logHandler=None,level=None,log_format=None,filepath=None,formatter=None):
		if logHandler is None:
			filepath=filepath or self.log_path
			if not filepath:
				raise KeyError("Provide the filepath or log_path.")
			logHandler=logging.FileHandler(filepath)
			self.debug('log_filepath=%s',filepath)
		logHandler.setLevel(level or self.logger.level)
		
		if formatter is None:
			if log_format is None: formatter=self.formatter
			else: formatter=logging.Formatter(log_format)
		logHandler.setFormatter(formatter)
		self.logger.addHandler(logHandler)
		
		self.pop()
		return logHandler
	
	def add_timed_handler(self,when='d',interval=1,backupCount=14,level=None,log_format=None,filepath=None,**other_opts):
		filepath=filepath or self.log_path
		if filepath is None: raise KeyError("Provide the filepath or log_path.")
		log_handler=self.add_handler(loghandlers.TimedRotatingFileHandler(
			filename=filepath,when=when,interval=interval,backupCount=backupCount,**other_opts),
			level=level,log_format=log_format)
		return log_handler
	
	def add_rotating_handler(self,maxBytes=2e6,backupCount=14,level=None,log_format=None,filepath=None,**other_opts):
		filepath=filepath or self.log_path
		if filepath is None: raise KeyError("Provide the filepath or log_path.")
		log_handler=self.add_handler(loghandlers.RotatingFileHandler(
			maxBytes=int(maxBytes),filename=filepath,backupCount=backupCount,**other_opts),level=level,log_format=log_format)
		return log_handler
	
	def create(self,*child_folders,**info_kwargs):
		self.current_log_folder=self.base_log_folder.create(*[get_name(x) for x in child_folders],**info_kwargs)
		return self
	
	def get_filepath(self,*name_portions,ext='.log',delim='__',include_depth=2,include_datetime=True,**name_kwargs):
		datetime_loc_index=None
		if type(include_datetime) is bool:
			if include_datetime: datetime_loc_index=include_depth
		else: datetime_loc_index=include_datetime
		
		# self.info('datetime_loc_index: %s',datetime_loc_index)
		self.log_path=self.current_log_folder.get_filepath(*name_portions,ext=ext,delim=delim,include_depth=include_depth,
		                                                   datetime_loc_index=datetime_loc_index,**name_kwargs)
		return self
	
	# def create_logpath(self,*name_portions,ext='',delim='_',include_depth=None,datetime_loc_index=None,**name_kwargs):
	# 	fp=self.current_log_folder.get_filepath(*name_portions,ext=ext,delim=delim,include_depth=include_depth,
	# 	                                       datetime_loc_index=datetime_loc_index,**name_kwargs)
	# 	self.add_timed_handler(fp,**(timing_opts or {}))
	# 	# self.info('log_filepath=%s',fp)
	# 	self.inform('log_filepath=%s',fp)
	# 	self.pop()
	# 	return self
	
	# def create_log_file(self,filename,include_depth=2,timing_opts=None,folder_parts=None,file_parts=None,**kwargs):
	# 	fp=self.base_log_folder.create(file=get_name(filename),**(folder_parts or {}))\
	# 		.get_filepath(include_depth=include_depth,include_datetime=-include_depth,**(file_parts or {}),**kwargs,pid=os.getpid())
	# 	self.add_timed_handler(fp,**(timing_opts or {}))
	# 	# self.info('log_filepath=%s',fp)
	# 	self.inform('log_filepath=%s',fp)
	# 	self.pop()
	# 	return self
	
	def __getitem__(self,item):
		return level_mapper[item](self)
	
	def inform(self,msg,*args,**kwargs):
		self.logger.inform(msg,*args,**kwargs)
	
	def with_logging(self,log_level=logging.DEBUG,atomic_print=False,show_inputs=False):
		# if logger is None: logger=simple_logger
		# assert logger is not None
		logger_say=level_mapper[log_level](self)
		
		def second_wrapper(func):
			@functools.wraps(func)
			def wrapper(*args,**kwargs):
				if not atomic_print:
					if show_inputs:
						logger_say('Running "%s" with args=%s and kwargs=%s:',func.__name__,args,kwargs)
					else:
						logger_say('Running "%s":',func.__name__)
				self.add()
				
				start=timer()
				try:
					result=func(*args,**kwargs)
				except KeyboardInterrupt:
					logger_say('KeyboardInterrupt within %s. Duration: %s',
					           func.__name__,timer()-start)
					sys.exit()
				except Exception as e:
					self.error(str(e),exc_info=True)
					raise e
				self.sub()
				logger_say('Done "%s". Duration: %.3f sec.',func.__name__,timer()-start)
				return result
			
			return wrapper
		
		return second_wrapper

log_fmt="%(asctime)s -- %(levelname)s -- %(name)s -- %(funcName)s -- %(filename)s -- %(lineno)d -- %(message)s"
# color_log_format="[%(asctime)s] [pid:%(process)5s] [%(levelname)8s]: %(message)s"
# color_log_format="[%(asctime)s] [%(levelname)-8s%(reset)s]: %(message)s"
color_info='%(log_color)s'
aligner=lambda n,_type='s':f'{n}{_type}'
color_log_format=f"{color_info}%(asctime)s pid:%(process){aligner(5,'d')} %(levelname){aligner(8)} {color_info}%(message)s"
# nocolor_log_format=f"%(asctime)s %(levelname){aligner(8)} %(message)s"
nocolor_log_format=f"%(asctime)s pid:%(process){aligner(5,'d')} %(levelname){aligner(8)} %(message)s"
# simple_fmt_without_color=f"%(asctime)s %(levelname){aligner(8)} %(message)s"
simple_fmt_no_level="%(asctime)s|||: %(message)s"
#log_folder=None  #Folder('~').create('backend_logs')
logger=TheLogger('simple_logger')

def with_logging(log_level=logging.DEBUG,atomic_print=False,show_inputs=False):
	# if logger is None: logger=simple_logger
	# assert logger is not None
	def second_wrapper(func):
		@functools.wraps(func)
		def wrapper(*args,**kwargs):
			logger_say=level_mapper[log_level](logger)
			if not atomic_print:
				if show_inputs:
					logger_say('Running "%s" with args=%s and kwargs=%s:',func.__name__,args,kwargs)
				else:
					logger_say('Running "%s":',func.__name__)
			logger.add()
			
			start=timer()
			try:
				result=func(*args,**kwargs)
			except KeyboardInterrupt:
				logger_say('KeyboardInterrupt within %s. Duration: %s',
				           func.__name__,timer()-start)
				sys.exit()
			except Exception as e:
				logger.error(str(e),exc_info=True)
				raise e
			finally:
				logger.sub()
			logger_say('Done "%s". Duration: %.3f sec.',func.__name__,timer()-start)
			return result
		
		return wrapper
	
	return second_wrapper

# def with_logging(log_level=logging.INFO,atomic_print=False,show_inputs=False):
# 	# global log_folder,logger
# 	# if log_folder is None: log_folder=Folder('~').create('backend_logs')
# 	# if logger is None: logger=TheLogger('simple_logger',log_folder)
# 	assert logger is not None,"Please, first create logger using create_logger(folder_path) method."
# 	return logger.with_logging(log_level,atomic_print=atomic_print,show_inputs=show_inputs)



# def get_logger_filepath(info: dict,dir_depth=1):
# 	kv_pairs=[f'{k}={v}' for k,v in info.items()]
# 	log_filename="___".join([*kv_pairs[dir_depth:],*kv_pairs[:dir_depth]])
# 	log_filepath=create_path(1,logs_folder.path,*kv_pairs[:dir_depth],log_filename+'.log')
# 	return log_filepath2

# simple_logger=TheLogger('simple_logger',)  #create_process_logger(__file__,collections.OrderedDict(pid=os.getpid()))

def create_logger(folder_path,name='default_logger',level=logging.DEBUG,**kwargs):
	from .folder_utils import Folder
	logger.base_log_folder=logger.current_log_folder=Folder(folder_path)
	logger.logger.name=name
	logger.logger.level=level
	# global logger
	# logger=TheLogger(name,folder_path,level=level,**kwargs)
	# log_folder=logger.base_log_folder
	return logger

def main():
	return

if __name__=='__main__':
	main()
	pass
