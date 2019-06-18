from file_tools.utils.functions import get_file, lines_gen

#: Get File String

def get_file_string(file, path='', encoding='utf-8'):
	with open(get_file(file, path=path), 'r', encoding=encoding) as f:
		return f.read()

#: Get File Lines

def get_file_lines(file, path='', newline='\n', encoding='utf-8'):
	with open(get_file(file, path=path), 'r', encoding=encoding) as f:
		return [l.rstrip(newline) for l in f]

#: Write File String

def write_file_string(file, path='', text='', encoding='utf-8'):
	with open(get_file(file, path=path), 'w', encoding=encoding) as f:
		f.write(text)
		return True

#: Append File String

def append_file_string(file, path='', text='', encoding='utf-8'):
	with open(get_file(file, path=path), 'a', encoding=encoding) as f:
		f.write(text)
		return True

#: Write File Lines

def write_file_lines(file, path='', lines=[], newline='\n', encoding='utf-8'):
	with open(get_file(file, path=path), 'w', encoding=encoding) as f:
		f.writelines(lines_gen(lines=lines, newline=newline))
		return True

#: Append File Lines

def append_file_lines(file, path='', lines=[], newline='\n', encoding='utf-8'):
	with open(get_file(file, path=path), 'a', encoding=encoding) as f:
		f.writelines(lines_gen(lines=lines, newline=newline))
		return True

#::: END PROGRAM :::
