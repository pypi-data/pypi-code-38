# -*- coding: utf-8 -*-
#cython: language_level=2

import os
import importlib
import traceback

from songfinder import globalvar

try:
	fileName = os.path.splitext( os.path.split(__file__)[1] )[0]
	module = importlib.import_module('lib.%s_%s'%(fileName, globalvar.arch))
	print("Using compiled version %s module"%fileName)
	globals().update(
		{n: getattr(module, n) for n in module.__all__} if hasattr(module, '__all__')
		else
		{k: v for (k, v) in module.__dict__.items() if not k.startswith('_')
	})
except (ImportError, NameError):
	# print(traceback.format_exc())

	# Fall back
	def simplifyChar(text):
		text = text\
			.replace('(e)','')\
			.replace('(h)','')\
			.replace('(f)','')\
			.replace('~','')\
			.replace('.','')\
			.replace(',','')\
			.replace(';','')\
			.replace(':','')\
			.replace('!',' ')\
			.replace("'",' ')\
			.replace('?',' ')\
			.replace('"','')\
			.replace('(',' ')\
			.replace(')',' ')\
			.replace('[v',' ')\
			.replace(']','')\
			.replace('/','')\
			.replace('\n',' ')\
			.replace('\r',' ')\
			.replace('\t',' ')\
			.replace('_',' ')\
			.replace('-',' ')\
			.replace(' bis ',' ')\
			.replace(' ter ',' ')\
			.replace(' x2 ',' ')\
			.replace(' x3 ',' ')\
			.replace(' x4 ',' ')

		for i in range(10):
			text = text.replace(str(i),'')

		return text

	def cleanupSpace(text):
		text = text\
			.replace('    ',' ')\
			.replace('   ',' ')\
			.replace('  ',' ')
		return text

	def cleanupChar(text):
		text = text\
			.replace(" \n", "\n")\
			.replace("\n ", "\n")\
			.replace("\r\n", "\n")\
			.replace("\t", "")\
			.replace("\n\n\n\n", "\n")\
			.replace("\n\n\n", "\n")\
			.replace("\n\n", "\n")
		return text
