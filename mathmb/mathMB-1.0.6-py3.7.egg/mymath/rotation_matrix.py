import numpy as np


def rotation_matrix(theta, axis):
    # Compute the rotation matrix for a rotation of theta about axis
    l = axis/np.linalg.norm(axis)
    lx, ly, lz = l[0], l[1], l[2]
    c, s = np.cos(theta), np.sin(theta)
    R = np.array([[lx**2+(1-lx**2)*c, lx*ly*(1-c)-lz*s, lx*lz*(1-c)+ly*s],
                  [lx*ly*(1-c)+lz*s, ly**2+(1-ly**2)*c, ly*lz*(1-c)-lx*s],
                  [lx*lz*(1-c)-ly*s, ly*lz*(1-c)+lx*s, lz**2+(1-lz**2)*c]])

    return R
