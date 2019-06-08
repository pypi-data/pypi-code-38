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
		A numpy ndarray object for a posterior transformation.
    """
	with open(filename, 'r') as xyz:
		n_lns = int(xyz.readline())
		p_mat = np.zeros((20, 3))
		for l in range(n_lns + 1):
			ps = xyz.readline().split(" ")
			if l > 0:
				ps[-1] = ps[-1][:-1]
				ps = list(filter(lambda x: x != "" and x != "\n", ps))
				p_mat[l - 1] = np.array([float(ps[1]), float(ps[2]), float(ps[3])])
	return p_mat


def write_xyz(filename, pos_mat):
	"""Utility function to write a xyz file.

	Parameters
	----------
	filename : str
		Path to xyz file to save.
	pos_mat : numpy.ndarray
		A numpy ndarray object to save into a file.

	Returns
	-------
	numpy.ndarray
		A numpy ndarray object for a posterior transformation.
	"""
	with open(filename, 'w') as xyz:
		xyz.write("{}\n".format(len(pos_mat)))
		xyz.write("\n")
		for line in range(len(pos_mat)):
			xyz.write("C\t\t {: .5f}\t {: .5f}\t {: .5f}\n".format(
				pos_mat[line, 0], pos_mat[line, 1], pos_mat[line, 2]))
	return