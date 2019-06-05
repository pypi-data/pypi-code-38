import os

#: Get Filename with Context

def get_file(file, path=''):
	if path == '':
		return f'{os.getcwd()}/{file}'
	else:
		return f'{os.path.dirname(path)}/{file}'

#::: END PROGRAM :::
