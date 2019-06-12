from file_tools.utils.functions import get_file

#: Get File String

def get_file_string(file, path=''):
	with open(get_file(file, path=path), 'r') as f:
		return f.read()

#: Get File Lines

def get_file_lines(file, path='', newline='\n'):
	with open(get_file(file, path=path), 'r') as f:
		return [l.rstrip(newline) for l in f]

#: Write File String

def write_file_string(file, path='', text=''):
	with open(get_file(file, path=path), 'w') as f:
		f.write(text)
		return True

#: Append File String

def append_file_string(file, path='', text=''):
	with open(get_file(file, path=path), 'a') as f:
		f.write(text)
		return True

#: Write File Lines

def write_file_lines(file, path='', lines=[]):
	with open(get_file(file, path=path), 'a') as f:
		f.writelines(lines)
		return True

#: Append File Lines

def append_file_lines(file, path='', lines=[]):
	with open(get_file(file, path=path), 'a') as f:
		f.writelines(lines)
		return True

#::: END PROGRAM :::
