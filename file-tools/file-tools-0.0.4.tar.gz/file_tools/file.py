from file_tools.utils.functions import get_file

#: Get File String

def get_file_string(file, relative=False, path=''):
	with open(get_file(file, relative), 'r') as f:
		return f.read()

#: Get File Lines

def get_file_lines(file, newline='\n', relative=False, path=''):
	with open(get_file(file, relative), 'r') as f:
		return [l.rstrip(newline) for l in f]

#::: END PROGRAM :::
