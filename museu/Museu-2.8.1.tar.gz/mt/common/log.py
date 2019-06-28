#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-04-19 09:57:58
# @Author  : Blackstone
# @to      :
import logging,colorlog,os

class lu(logging.RootLogger):


	_switch=True#

	_filelog=False
	_logfile="log.txt"

	@classmethod
	def getLogger(cls,name=None):
		if name is None:
			name=__name__
		logger=logging.getLogger(name)
		logger.setLevel(logging.DEBUG)

		console=logging.StreamHandler()
		console.setFormatter(cls.color_formatter())
		#console.setLevel(logging.DEBUG)
		logger.addHandler(console)


		if cls._filelog:
			logger.addHandler(cls.fileHandler())

		return logger



	@classmethod 
	def file_log(cls,bool_,path=None):
		cls._filelog=bool_
		cls._logfile=path


	@classmethod
	def file_handler(cls):
		handler=logging.FileHandler(cls._logfile)
		handler.setFormatter(cls.text_formatter())
		return handler

	@classmethod
	def color_scheme(cls):
		return{
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red',
}


	@classmethod
	def text_formatter(cls):
		return logging.Formatter('%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')

	@classmethod
	def color_formatter(cls):
		return colorlog.ColoredFormatter("%(log_color)s%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",log_colors=cls.color_scheme())






if __name__=="__main__":

	lu.color_scheme=lambda:{
	"INFO":"blue"
	}
	log=lu.getLogger()

	log.info("f","f")
	log.info