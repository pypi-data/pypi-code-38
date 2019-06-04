import os

#: Get Filename with Context

def get_file(file, relative=False):
	if not relative:
		return f'{os.getcwd()}/{file}'
	else:
		return f'{os.path.dirname(os.path.abspath(__file__))}/{file}'

#::: END PROGRAM :::
