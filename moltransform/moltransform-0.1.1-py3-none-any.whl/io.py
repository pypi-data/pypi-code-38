"""
TODO: Add description.
"""

import numpy as np


def read_xyz(filename):
	"""Utility function to read a xyz file.
	
	Parameters
	----------
	filename : str
		Path to xyz file to open.

	Returns
	-------
	numpy.ndarray
		A NumPy ndarray object for a posterior transformation.
    """
	with open(filename, 'r') as xyz:
		total_lines = int(xyz.readline())
		position_matrix = np.zeros((total_lines, 3))
		for line in range(total_lines + 1):
			pos = xyz.readline().split(" ")
			if line > 0:
				pos[-1] = pos[-1][:-1]
				pos = list(filter(lambda x: x != "" and x != "\n", pos))
				pos_line = [float(pos[1]), float(pos[2]), float(pos[3])]
				position_matrix[line - 1] = np.array(pos_line)
	return position_matrix


def write_xyz(filename, pos_matrix):
	"""Utility function to write a xyz file.

	Parameters
	----------
	filename : str
		Path to xyz file to save.
	pos_matrix : numpy.ndarray
		A NumPy ndarray object to save into a file.
	"""
	with open(filename, 'w') as xyz:
		xyz.write("{}\n".format(len(pos_matrix)))
		xyz.write("\n")
		for line in range(len(pos_matrix)):
			xyz.write("C\t\t {: .5f}\t {: .5f}\t {: .5f}\n".format(
				pos_matrix[line, 0], pos_matrix[line, 1], pos_matrix[line, 2]))
	return