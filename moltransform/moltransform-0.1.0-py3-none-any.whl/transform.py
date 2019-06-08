"""
TODO: Add description.
"""

import numpy as np


def center(p_mat):
    """
    Utility function to center a set of 3D coordinates.
    """
    print("(WARNING) Not single transformation selected.")
    print("(INFO) Molecule centering to be done.")
    min_x, max_x = np.min(p_mat[:, 0]), np.max(p_mat[:, 0])
    min_y, max_y = np.min(p_mat[:, 1]), np.max(p_mat[:, 1])
    min_z, max_z = np.min(p_mat[:, 2]), np.max(p_mat[:, 2])
    mean_x = (max_x + min_x) / 2
    mean_y = (max_y + min_y) / 2
    mean_z = (max_z + min_z) / 2
    t_vec = [-mean_x, -mean_y, -mean_z]
    t_mat = translate(p_mat, t_vec)
    return t_mat


def translate(p_mat, translation_vec=None):
    """
    Utility function to translate a set of 3D coordinates.
    """
    T = np.eye(4)
    T[:-1, 3] = translation_vec
    print("(INFO) Transformation matrix to be used:")
    print(T)
    t_mat = p_mat.copy()
    for row in range(len(p_mat)):
        t_mat[row] = (T @ np.hstack((p_mat[row], [1])))[:-1]
    return t_mat


def scale(p_mat, scaling_vec=None):
    """
    Utility function to rotate a set of 3D coordinates.
    """
    T = np.eye(4)
    if scaling_vec is None:
        return p_mat
    else:
        T[:-1, :-1] *= scaling_vec
        print("(INFO) Transformation matrix to be used:")
        print(T)
    t_mat = p_mat.copy()
    for row in range(len(p_mat)):
        t_mat[row] = (T @ np.hstack((p_mat[row], [1])))[:-1]
    return t_mat
