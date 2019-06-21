from __future__ import print_function
import sys


def pre_list(strain_list_file):
	strain_info = dict()
	with open(strain_list_file, 'r') as f:
		for line in f.readlines():
			line = line.replace('\n', '')
			tmp = line.split('\t')
			columns = len(tmp)

			if (columns < 2) or (columns > 2 and columns < 4):
				print('Error: 2 or 4 tab-delimited columns : barcodes strain_name [reads1 path] [reads2 path]')
				sys.exit(-1)

			if tmp[0] not in strain_info.keys():
				strain_info[tmp[0]] = []

			strain_info[tmp[0]].extend(tmp)

	return strain_info, columns

