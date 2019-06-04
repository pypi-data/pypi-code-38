from file_tools.utils.functions import get_file, get_caller_path

#: Get File String

def get_file_string(file, relative=False):
	file = get_file(file) if not relative else get_file(f'{get_caller_path()}/{file}', relative)
	with open(file, 'r') as f:
		return f.read()

#: Get File Lines

def get_file_lines(file, newline='\n', relative=False):
	file = get_file(file) if not relative else get_file(f'{get_caller_path()}/{file}', relative)
	with open(file, 'r') as f:
		return [l.rstrip(newline) for l in f]

#::: END PROGRAM :::
