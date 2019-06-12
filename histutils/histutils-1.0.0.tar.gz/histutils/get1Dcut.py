from pathlib import Path
from numpy import logspace
import h5py
from typing import List
#
from pymap3d import ecef2aer
from .plots import plotLOSecef
from .camclass import Cam


def get1Dcut(cam: List[Cam], odir: Path = None, verbose: bool = False) -> List[Cam]:
    """
    i.   get az/el of each pixel (rotated/transposed as appropriate)
    ii.  get cartesian ECEF of each pixel end, a point outside the grid (to create rays to check intersections with grid)
    iii. put cameras in same frame, getting az/el to each other's pixel ends
    iv.  find the indices corresponding to those angles
    now the cameras are geographically registered to pixel indices
    """

# %% determine slant range between other camera and magnetic zenith to evaluate at
    # 4.5 had zero discards for hst0 #6.8 didn't quite get to zenith
    srpts = logspace(4.3, 6.9, 25)
# %% (i) load az/el data from Astrometry.net
    for C in cam:
        if C.usecam:
            C.doorient()
            C.toecef(srpts)

    # optional: plot ECEF of points between each camera and magnetic zenith (lying at az,el relative to each camera)
    if verbose:
        plotLOSecef(cam, odir)
# %% (2) get az,el of these points from camera to the other camera's points
    cam[0].az2pts, cam[0].el2pts, cam[0].r2pts = ecef2aer(cam[1].x2mz, cam[1].y2mz, cam[1].z2mz,
                                                          cam[0].lat, cam[0].lon, cam[0].alt_m)
    cam[1].az2pts, cam[1].el2pts, cam[1].r2pts = ecef2aer(cam[0].x2mz, cam[0].y2mz, cam[0].z2mz,
                                                          cam[1].lat, cam[1].lon, cam[1].alt_m)
# %% (3) find indices corresponding to these az,el in each image
    # and Least squares fit line to nearest points found in step 3
    for C in cam:
        if C.usecam:
            C.findClosestAzel(odir)
# %%
    if verbose and odir:
        dbgfn = odir / 'debugLSQ.h5'
        print('writing', dbgfn)
        with h5py.File(dbgfn, 'w') as f:
            for C in cam:
                f[f'/cam{C.name}/cutrow'] = C.cutrow
                f[f'/cam{C.name}/cutcol'] = C.cutcol
                f['/cam{C.name}/xpix'] = C.xpix
    return cam


#
# def findClosestAzel(cam, discardEdgepix,dbglvl):
#    for c in cam:
#        azImg,elImg,azVec,elVec = cam[c].az, cam[c].el, cam[c].az2pts,cam[c].el2pts,
#
#        ny,nx = cam[c].ypix, cam[c].xpix
#
#        assert azImg.shape ==  elImg.shape
#        assert azVec.shape == elVec.shape
#        assert azImg.ndim == 2
#
#        npts = azVec.size  #numel
#        nearRow = empty(npts,dtype=int)
#        nearCol = empty(npts,dtype=int)
#        for ipt in range(npts):
#            #we do this point by point because we need to know the closest pixel for each point
#            errdist = absolute( hypot(azImg - azVec[ipt],
#                                       elImg - elVec[ipt]) )
#
# ********************************************
# THIS UNRAVEL_INDEX MUST BE ORDER = 'C'
#            nearRow[ipt],nearCol[ipt] = unravel_index(errdist.argmin(),(ny,nx),order='C')
# ************************************************
#
#
#        if discardEdgepix:
#            edgeind = logical_or(logical_or(nearCol==0,nearCol == nx-1),
#                               logical_or(nearRow==0,nearRow==ny-1))
#            nearRow = delete(nearRow,edgeind)
#            nearCol = delete(nearCol,edgeind)
#            if dbglvl>0: print('deleted',edgeind.size, 'edge pixels ')
#
#        cam[c].findLSQ(nearRow, nearCol)
#
#        if dbglvl>0:
#            clr = ['b','r','g','m']
#            ax = figure().gca()
#            ax.plot(nearCol,nearRow,color=clr[int(c)],label='cam'+c+'preLSQ',
#                    linestyle='None',marker='.')
#            ax.legend()
#            ax.set_xlabel('x'); ax.set_ylabel('y')
#            #ax.set_title('pixel indices (pre-least squares)')
#            ax.set_xlim([0,cam[c].az.shape[1]])
#            ax.set_ylim([0,cam[c].az.shape[0]])
#
#    return cam
