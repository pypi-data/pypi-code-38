import os
import inspect

#: Get Filename with Context

def get_file(file, relative=False):
	if not relative:
		return f'{os.getcwd()}/{file}'
	else:
		return f'{get_caller_path()}/{file}'

#: Get Path of Caller

def get_caller_path():
	for item in inspect.stack():
		if item and __file__ not in item:
			if item.index == 0:
				return os.path.dirname(os.path.abspath(item.filename))

#::: END PROGRAM :::
