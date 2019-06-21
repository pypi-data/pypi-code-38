import numpy as np
from mdio.fastrmsd import kabsch2

def kabsch(xa, xb, w=None):
    """
    Fit xa to xb, with optional weights w

    Args:
        xa ([N, 3] array): coordinates to fit
        xb ([N, 3] array): coordinates of reference
        w ([N] array): weights

    Returns:
        R: [3,3] rotation marix
        T: [3] translation vector
        rmsd: rms error (float)
    """
    if w is None:
        xa = np.array(xa).astype(np.float32, copy=False)
        xb = np.array(xb).astype(np.float32, copy=False)
        return kabsch2(xa, xb)

    cma = np.zeros(3)
    cmb = np.zeros(3)
    umat = np.zeros((3, 3))
    if w is None:
        w = np.ones(len(xa)) / len(xa)
    w = np.array([w, w, w]).T
    xasq = 0.0
    xbsq = 0.0
    iw = 3.0 /w.sum()
    n = len(xa)
    for i in range(3):
        for j in range(n):
            for k in range(3):
                umat[i, k] += xa[j, i] * xb[j, k] * w[j, i]
    cma = (xa * w).sum(axis=0)
    cmb = (xb * w).sum(axis=0)
    xasq = (xa * xa * w).sum() - (cma * cma).sum() * iw
    xbsq = (xb * xb * w).sum() - (cmb * cmb).sum() * iw
    umat = (umat - np.outer(cma, cmb) * iw) * iw
    C = umat
    V, S, W = np.linalg.svd(C)
    d = (np.linalg.det(V) * np.linalg.det(W)) < 0.0

    if d:
        S[-1] = -S[-1]
        V[:, -1] = -V[:, -1]

    # Create Rotation matrix U
    U = np.dot(V, W)
    rmse = (xasq + xbsq) * iw - 2.0 * S.sum()
    if rmse < 0.0:
        rmse = 0.0
    rmse = np.sqrt(rmse)
    v = np.zeros(3)
    for i in range(3):
        t = (U[i,:] * cmb).sum()
        v[i] = (cma[i] - t)
    v = v * iw
    return U, v, rmse
def kabsch_fit(xa, xb, w=None, rmsd=False):
    """
    Fit xa to xb, with optional weights w

    Args:
        xa ([N, 3] array): coordinates to fit
        xb ([N, 3] array): coordinates of reference
        w ([N] array): weights

    Returns:
        xanew: [N,3] array, xa after fitting to xb
        rms: optional, rms error (float)
    """

    R, T, rms = kabsch(xb, xa, w)
    xanew = np.dot(xa, R.T) + T
    if rmsd:
        return xanew, rms
    else:
        return xanew

def kabsch_rmsd(xa, xb, w=None):
    """
    Calculate rmsd between xa and xb, with optional weights w

    Args:
        xa ([N, 3] array): coordinates to fit
        xb ([N, 3] array): coordinates of reference
        w ([N] array): weights

    Returns:
        rmsd: rms error (float)
    """

    R, T, rmsd = kabsch(xa, xb, w)
    return rmsd
