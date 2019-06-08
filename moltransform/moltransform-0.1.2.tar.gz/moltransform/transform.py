"""
TODO: Add description.
"""

import numpy as np


def center(pos_matrix, verbose=False):
	"""Utility function to center a set of 3D coordinates.

	Parameters
	----------
	pos_matrix : numpy.ndarray
		A NumPy ndarray with centered molecules.
	verbose : bool
		A flag to print the transformation matrix to be used.

	Returns
	-------
	numpy.ndarray
		A NumPy ndarray with centered xyz positions.
	"""
	if verbose:
		print("(INFO) Molecule centering to be done.")
	min_x, max_x = np.min(pos_matrix[:, 0]), np.max(pos_matrix[:, 0])
	min_y, max_y = np.min(pos_matrix[:, 1]), np.max(pos_matrix[:, 1])
	min_z, max_z = np.min(pos_matrix[:, 2]), np.max(pos_matrix[:, 2])
	mean_x = (max_x + min_x) / 2
	mean_y = (max_y + min_y) / 2
	mean_z = (max_z + min_z) / 2
	t_vector = [-mean_x, -mean_y, -mean_z]
	t_matrix = translate(pos_matrix, t_vector, verbose)
	return t_matrix


def translate(pos_matrix, translation_vector=None, verbose=False):
	"""Utility function to translate a set of 3D coordinates.

	Parameters
	----------
	pos_matrix : numpy.ndarray
		A NumPy ndarray with centered molecules.
	translation_vector : numpy.array or list
		The translation vector to be used.
	verbose : bool
		A flag to print the transformation matrix to be used.

	Returns
	-------
	numpy.ndarray
		A NumPy ndarray with translated xyz positions.
	"""
	if translation_vector is None:
		if verbose:
			print("(INFO) No translation vector was defined.")
		return pos_matrix
	else:
		T = np.eye(4)
		T[:-1, 3] = translation_vector

		if verbose:
			print("(INFO) Transformation matrix to be used:")
			print(T)

		t_matrix = pos_matrix.copy()
		for row in range(len(pos_matrix)):
			t_matrix[row] = (T @ np.hstack((pos_matrix[row], [1])))[:-1]
		return t_matrix


def scale(pos_matrix, scaling_vector=None, verbose=False):
	"""Utility function to rotate a set of 3D coordinates.

	Parameters
	----------
	pos_matrix : numpy.ndarray
		A NumPy ndarray with centered molecules.
	scaling_vector : numpy.array or list
		The scaling vector to be used.
	verbose : bool
		A flag to print the transformation matrix to be used.

	Returns
	-------
	numpy.ndarray
		A NumPy ndarray with scaled xyz positions.
	"""
	if scaling_vector is None:
		if verbose:
			print("(INFO) No scaling vector was defined.")
		return pos_matrix
	else:
		T = np.eye(4)
		T[:-1, :-1] *= scaling_vector

		if verbose:
			print("(INFO) Transformation matrix to be used:")
			print(T)

		t_matrix = pos_matrix.copy()
		for row in range(len(pos_matrix)):
			t_matrix[row] = (T @ np.hstack((pos_matrix[row], [1])))[:-1]
		return t_matrix
