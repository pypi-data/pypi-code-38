import os

#: Get Filename with Context

def get_file(file, path=''):
	if path == '':
		return f'{os.getcwd()}/{file}'
	else:
		return f'{os.path.dirname(path)}/{file}'

#: Lines Generator, adds newline to all lines but last line

def lines_gen(lines=[], newline='\n'):
	for count, line in enumerate(lines):
		if count != len(lines) - 1:
			yield f'{line}{newline}'
		else:
			yield line

#::: END PROGRAM :::
