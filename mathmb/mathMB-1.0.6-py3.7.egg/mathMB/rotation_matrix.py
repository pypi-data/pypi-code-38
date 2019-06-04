"""``rotation_matrix()``: Compute the rotation matrix about an axis."""
import numpy as np


def rotation_matrix(theta, axis):
    """Compute the rotation matrix for a rotation of theta about axis."""
    unit_vec = axis/np.linalg.norm(axis)
    lx, ly, lz = unit_vec[0], unit_vec[1], unit_vec[2]
    c, s = np.cos(theta), np.sin(theta)
    rot_mat = np.asmatrix([[lx**2+(1-lx**2)*c, lx*ly*(1-c)+lz*s, lx*lz*(1-c)-ly*s],
                          [lx*ly*(1-c)-lz*s, ly**2+(1-ly**2)*c, ly*lz*(1-c)+lx*s],
                          [lx*lz*(1-c)+ly*s, ly*lz*(1-c)-lx*s, lz**2+(1-lz**2)*c]])

    return rot_mat
