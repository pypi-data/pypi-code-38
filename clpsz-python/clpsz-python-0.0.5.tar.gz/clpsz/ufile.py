import os


def read_file_as_list(file_path):
	"""
	read_file_as_list(file_path) -> list of string

	read a file and convert to a lis tof string, split the file content by new line,
	remove the last line break.
	"""
	res = []
	with open(file_path, 'r') as f:
		for line in f:
			if line[-1] == os.linesep:
				line = line[:-1]
			res.append(line)
	return res


def get_file_line_count(file_path):
	count = 0
	with open(file_path, 'r') as f:
		for _ in f:
			count += 1
	return count
