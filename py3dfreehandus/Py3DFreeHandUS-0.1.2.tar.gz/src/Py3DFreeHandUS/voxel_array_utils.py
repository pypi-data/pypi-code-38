# -*- coding: utf-8 -*-
"""
.. module:: voxel_array_utils
   :synopsis: helper module for voxel-array

"""

import numpy as np
from scipy.interpolate import griddata
from scipy import ndimage as nd
import vtk
from vtk.util import numpy_support as nps
import SimpleITK as sitk


class VoxelArray3D(object):
    """
    """
    
    def __init__(self, dataType=np.uint8, dims=(0,0,0), scales=(1.,1.,1.)):
        """Constructor
        """
        self.dataType = dataType
        self.xl = dims[0]
        self.yl = dims[1]
        self.zl = dims[2]
        self.fx = scales[0]
        self.fy = scales[1]
        self.fz = scales[2]
        self.V = np.zeros(int(self.xl*self.yl*self.zl), dtype=self.dataType)
        
    def getDims(self):
        return self.xl, self.yl, self.zl

    def getDataByIdx(self, idx):
        return self.V[idx]
        
    def getDataByEdges(self, x0, x1, y0, y1, z0, z1):
        V = self.getNumpyArray3D()
        return V[x0:x1, y0:y1, z0:z1]
        
    def getSubVoxelArray(self, x0, x1, y0, y1, z0, z1):
        V = self.getDataByEdges(x0, x1, y0, y1, z0, z1)
        newV = VoxelArray3D(dataType=self.dataType, dims=V.shape, scales=(self.fx,self.fy,self.fz))
        newV.setAllDataByNumpy3D(V)
        return newV
        
    def setDataByIdx(self, idx, data):
        self.V[idx] = data
        
    def addConstByIdx(self, idx, c):
        self.V[idx] += c
        
    def setAllDataByNumpy1D(self, data):
        self.V = data
        self.dataType = self.V.dtype
    
    def setAllDataByNumpy3D(self, data):
        self.setAllDataByNumpy1D(data.ravel(order='F'))
        
    def getNumpyArray1D(self):
        return self.V
        
    def getNumpyArray3D(self):
        return np.reshape(self.getNumpyArray1D(), (self.xl,self.yl,self.zl), order='F')
        
    def extend(self, xMin, xMax, yMin, yMax, zMin, zMax):
        if xMin < 0 or xMax > self.xl-1 or yMin < 0 or yMax > self.yl-1 or zMin < 0 or zMax > self.zl-1: 
            xa, ya, za = np.min((0, xMin)), np.min((0, yMin)), np.min((0, zMin))
            xb, yb, zb = np.max((self.xl-1, xMax)), np.max((self.yl-1, yMax)), np.max((self.zl-1, zMax))
            xl, yl, zl = xb - xa + 1, yb - ya + 1, zb - za + 1
            dx, dy, dz = self.xl, self.yl, self.zl
            x, y, z = -xa, -ya, -za
            newV = np.zeros((xl,yl,zl), dtype=self.dataType)
            tempV = self.getNumpyArray3D()
            newV[x:x+dx,y:y+dy,z:z+dz] = tempV
            self.xl = xl
            self.yl = yl
            self.zl = zl
            self.setAllDataByNumpy3D(newV)
        
    def fillGaps(self, contVA, internalVA, method='VNN', blocksN=1, blockDir='X', distTh=None, maxS=3, minPct=0.):
        V = self.getNumpyArray1D()
        usedV = contVA.getNumpyArray1D() > 0
        internalV = internalVA.getNumpyArray1D()
        print 'Filling empty voxels ({0}), when possible ...'.format(method)
        if blockDir == 'X':
            bxl = np.ceil(self.xl / blocksN)
            byl = self.yl
            bzl = self.zl
        elif blockDir == 'Y':
            bxl = self.xl
            byl = np.ceil(self.yl / blocksN)
            bzl = self.zl
        elif blockDir == 'Z':
            bxl = self.xl
            byl = self.yl
            bzl = np.ceil(self.zl / blocksN)
        bxl, byl, bzl = int(bxl), int(byl), int(bzl)
#        blockSize = bxl * byl * bzl
#        if len(self.getDims()) > 1:
#            sliceMethod = 'fast'
#        else:
#            sliceMethod = 'slow'
        sliceMethod = 'slow'
        for b in xrange(0, blocksN):
            print 'Block {0} ...'.format(b+1)
            # Initialize block indices
            cLims = [None] * 3
            if blockDir == 'X':
                cLims[0] = [b*bxl, np.min([(b+1)*bxl,self.xl])]
                cLims[1] = [0, self.yl]
                cLims[2] = [0, self.zl]
                if (b+1)*bxl > self.xl:
                    bxl = int(self.xl - b * bxl)
            elif blockDir == 'Y':
                cLims[0] = [0, self.xl]
                cLims[1] = [b*byl, np.min([(b+1)*byl,self.yl])]
                cLims[2] = [0, self.zl]
                if (b+1)*byl > self.yl:
                    byl = int(self.yl - b * byl)
            elif blockDir == 'Z':
                cLims[0] = [0, self.xl]
                cLims[1] = [0, self.yl]
                cLims[2] = [b*bzl, np.min([(b+1)*bzl,self.zl])]
                if (b+1)*bzl > self.zl:
                    bzl = int(self.zl - b * bzl)
            if sliceMethod == 'slow':
                xc, yc, zc = getCubeCoords(cLims)
                ind = xyz2idx(xc, yc, zc, self.xl, self.yl, self.zl)
                idxBlock = np.zeros(int(np.prod(self.getDims())), dtype=np.bool)
                idxBlock[ind] = True
            if method == 'VNN':
                # Apply VNN
#                bzl = np.sum(idxBlock) / (bxl * byl)
                if sliceMethod == 'slow':
                    reshV = np.reshape((~usedV & internalV)[idxBlock], (bzl,byl,bxl))
                    reshV2 = np.reshape(V[idxBlock], (bzl,byl,bxl))
                elif sliceMethod == 'fast':
                    reshV = (~usedV & internalV)[cLims[2][0]:cLims[2][1],cLims[1][0]:cLims[1][1],cLims[0][0]:cLims[0][1]]
                    reshV2 = V[cLims[2][0]:cLims[2][1],cLims[1][0]:cLims[1][1],cLims[0][0]:cLims[0][1]]
                np.set_printoptions(threshold=np.nan)
                if distTh is None:
                    idxV = nd.distance_transform_edt(reshV, return_distances=False, return_indices=True)
                else:
                    edt, idxV = nd.distance_transform_edt(reshV, return_distances=True, return_indices=True)
                    idxTh = np.nonzero(edt > distTh)
                    idxV[0][idxTh] = idxTh[0]
                    idxV[1][idxTh] = idxTh[1]
                    idxV[2][idxTh] = idxTh[2]
                    del edt, idxTh
                if sliceMethod == 'slow':
                    V[idxBlock] = reshV2[tuple(idxV)].ravel()
                    usedV[idxBlock] = True
                    del idxBlock
                elif sliceMethod == 'fast':
                    V[cLims[2][0]:cLims[2][1],cLims[1][0]:cLims[1][1],cLims[0][0]:cLims[0][1]] = reshV2[tuple(idxV)]
                    usedV[cLims[2][0]:cLims[2][1],cLims[1][0]:cLims[1][1],cLims[0][0]:cLims[0][1]] = True
                del reshV, reshV2, idxV
                # Print some info
                pctInternalEmpty = 100.0 * np.sum(internalV & ~usedV) / np.sum(internalV)
                print '\tEstimate of pct of internal empty voxels: ({0}% internal)'.format(pctInternalEmpty) 
            elif method == 'AVG_CUBE':
                for S in np.arange(3, maxS+1, 2):
                    if b == 0:
                        # Generate voxel coordinates for the search cube
                        xCube, yCube, zCube = getCubeCoords(S)
                        # Remove central voxel of the cube
                        idxCentral = np.nonzero((xCube == 0) & (yCube == 0) & (zCube == 0))[0]
                        xCube = np.delete(xCube, idxCentral)[:, None]
                        yCube = np.delete(yCube, idxCentral)[:, None]
                        zCube = np.delete(zCube, idxCentral)[:, None]
                        # Calculate distance from each vixel to central voxel
                        distNeighs = (xCube**2 + yCube**2 + zCube**2)**(0.5)
                        idxSort = np.argsort(distNeighs)
                        distNeighs = 1. / distNeighs[idxSort,:]
                    idxEmpty = np.nonzero((~usedV) & idxBlock & internalV)[0]   # time bottleneck
                    # Get coordinates of empty voxels
                    xn, yn, zn = idx2xyz(idxEmpty, self.xl, self.yl, self.zl)
                    xn = np.tile(xn, (S**3-1,1))
                    yn = np.tile(yn, (S**3-1,1))
                    zn = np.tile(zn, (S**3-1,1))
                    idxNeighs = xyz2idx(xn+xCube,yn+yCube,zn+zCube, self.xl, self.yl, self.zl)
                    # Get values for neigbour voxels, empty or not
                    neighsV = V[idxNeighs]
                    neighsUsedV = usedV[idxNeighs]
                    del idxNeighs
                    # Sort by distance
                    neighsV = neighsV[idxSort,:]
                    neighsUsedV = neighsUsedV[idxSort,:]
                    # Fill some empty voxels
                    idxFillable = (np.sum(neighsUsedV, axis=0) >= np.round(minPct * (S**3-1)) ).squeeze()
                    wMeanNum = np.sum(neighsUsedV * neighsV * distNeighs, axis=0).squeeze()
                    wMeanDen = np.sum(neighsUsedV * distNeighs, axis=0).squeeze()
                    V[idxEmpty[idxFillable]] = (wMeanNum[idxFillable] / wMeanDen[idxFillable]).round().astype(np.uint8)  
                    usedV[idxEmpty[idxFillable]] = True   
                    # Print some info
                    pctInternalEmpty = 100.0 * np.sum(internalV & ~usedV) / np.sum(internalV)
                    print '\tEstimate of pct of internal empty voxels after filling with cube of side {0}: ({1}% internal)'.format(S, pctInternalEmpty)              
                    # Delete biggest arrays in inner loop                
                    del idxEmpty, neighsV, neighsUsedV, idxFillable, wMeanNum, wMeanDen
        
        print 'Empty voxels filled when possible'
        return pctInternalEmpty
        
        
    def getVtkImageData(self, scales, vtkDataType):
        vtkV = nparray2vtkImageData(self.getNumpyArray1D(), (self.xl,self.yl,self.zl), scales, vtkDataType)        
        return vtkV
        
    def getCoordsSmallestWrappingParallelepipedon(self, toExclude=0):
        V = self.getNumpyArray3D()
        x, y, z = np.nonzero(V <> toExclude)
        xa, xb = x.min(), x.max()
        ya, yb = y.min(), y.max()
        za, zb = z.min(), z.max()
        return xa, xb, ya, yb, za, zb
        
class VoxelArray3DFrom2DImages(VoxelArray3D):
    """
    """
    
    def __init__(self, **kwargs):
        """Constructor
        """
        super(self.__class__, self).__init__(**kwargs)
        # Create voxel array for grey values
        #self.V = VoxelArray3D(dataType=np.uint8, dims=(self.xl,self.yl,self.zl), scales=(self.fx,self.fy,self.fz))
        
        # Create voxel array for grey values indicating hox many times a voxel
        # has been written
        self.contV = VoxelArray3D(dataType=np.uint8, dims=self.getDims())
        
        # Create voxel array for bool values indicating if the voxel contains
        # raw data
        #self.usedV = self.contV
        
        # Create voxel array for bool values indicating if the voxel belongs
        # to the sequence of slices
        self.internalV = VoxelArray3D(dataType=np.bool, dims=self.getDims())
        
        # Create corner coordinates for previously written images
        self.xcPrev, self.ycPrev, self.zcPrev = None, None, None
        
    def getCounterVoxelArray(self):
        return self.contV
        
    def getSilhouetteVoxelArray(self):
        return self.internalV
        
    def setCounterVoxelArray(self, contV):
        self.contV = contV
        
    def setSilhouetteVoxelArray(self, internalV):
        self.internalV = internalV
        
    def getSubVoxelArray(self, x0, x1, y0, y1, z0, z1):
        V = self.getDataByEdges(x0, x1, y0, y1, z0, z1)
        contV = self.contV.getSubVoxelArray(x0, x1, y0, y1, z0, z1)
        internalV = self.internalV.getSubVoxelArray(x0, x1, y0, y1, z0, z1)
        newV = VoxelArray3DFrom2DImages(dataType=self.dataType, dims=V.shape, scales=(self.fx,self.fy,self.fz))
        newV.setAllDataByNumpy3D(V)
        newV.setCounterVoxelArray(contV)
        newV.setSilhouetteVoxelArray(internalV)
        return newV

    def extend(self, xMin, xMax, yMin, yMax, zMin, zMax):
        parent = super(self.__class__, self)
        parent.extend(xMin, xMax, yMin, yMax, zMin, zMax)
        self.contV.extend(xMin, xMax, yMin, yMax, zMin, zMax)
        self.internalV.extend(xMin, xMax, yMin, yMax, zMin, zMax)
        
    def writeImageByIdx(self, idxV, I, fillVoxMethod):
        parent = super(self.__class__, self)
        if fillVoxMethod == 'avg':
            parent.setDataByIdx(idxV, parent.getDataByIdx(idxV) * (self.contV.getDataByIdx(idxV) / (self.contV.getDataByIdx(idxV) + 1)) + I.ravel() * (1. / (self.contV.getDataByIdx(idxV) + 1)) )
        elif fillVoxMethod == 'last':
            parent.setDataByIdx(idxV, I.ravel())
        elif fillVoxMethod == 'max':
            parent.setDataByIdx(idxV, np.maximum(parent.getDataByIdx(idxV), I.ravel()) )
        self.contV.addConstByIdx(idxV, 1)
        self.internalV.setDataByIdx(idxV, True)
        
    def writeImageByCoords(self, coords, I, fillVoxMethod):
        x, y, z = coords
        idxV = xyz2idx(x, y, z, self.xl, self.yl, self.zl)
        self.writeImageByIdx(idxV, I, fillVoxMethod)
        
    def fillGaps(self, **kwargs):
        parent = super(self.__class__, self)
        parent.fillGaps(self.contV, self.internalV, **kwargs)
        
    def updateWrapper(self, wrapper, corners, cornersPrev=None):
        xc, yc, zc = corners
        if self.xcPrev is None or self.ycPrev is None or self.zcPrev is None:
            self.xcPrev, self.ycPrev, self.zcPrev = corners
        if cornersPrev is None:
            xcPrev, ycPrev, zcPrev = self.xcPrev, self.ycPrev, self.zcPrev
        else:
            xcPrev, ycPrev, zcPrev = cornersPrev
        if wrapper == 'parallelepipedon':
            print 'Creating parallelepipedon ...'
            xcMin, xcMax = np.min((xc.min(),xcPrev.min())), np.max((xc.max(),xcPrev.max()))
            ycMin, ycMax = np.min((yc.min(),ycPrev.min())), np.max((yc.max(),ycPrev.max()))
            zcMin, zcMax = np.min((zc.min(),zcPrev.min())), np.max((zc.max(),zcPrev.max()))
            xcInternal, ycInternal, zcInternal = getCubeCoords(([xcMin,xcMax],[ycMin,ycMax],[zcMin,zcMax]))
        elif wrapper == 'convex_hull':
            print 'Creating convex hull ...'
            cCurrent = np.array((xc,yc,zc)).T
            cPrev = np.array((xcPrev,ycPrev,zcPrev)).T
            if not np.array_equal(cCurrent,cPrev):
                cHull = np.vstack((cCurrent,cPrev))
                try:
                    cInternal = getCoordsInConvexHull(cHull)
                    xcInternal, ycInternal, zcInternal = cInternal[:,0], cInternal[:,1], cInternal[:,2]
                    idxInternal = xyz2idx(xcInternal, ycInternal, zcInternal, self.xl, self.yl, self.zl)
                    self.internalV.setDataByIdx(idxInternal, True)
                except:
                    print 'Error in creating convex hull coordinates'
            else:
                print 'The 2 slices are exactly overlapped. Impossible to create convex hull'
        self.xcPrev = xc.copy()
        self.ycPrev = yc.copy()
        self.zcPrev = zc.copy()
    

def getCoordsInConvexHull(p):
    """Create the convex hull for a list of points and the list of coorindates internal to it.
    
    Parameters
    ----------
    p : np.ndarray
        N x 3 list of coordinates for which to calculate the cinvex hull. Coordinates should be integer.
        
    Returns
    -------
    np.ndarray
        M x 3 array of coordinates, where M is the number of points internal to the convex hull.
    
    """
    # Get minimum and maximum coordinates
    xMin, yMin, zMin = p.min(axis=0)
    xMax, yMax, zMax = p.max(axis=0)
    # Create coordinates between maximim and minimum
    xCube, yCube, zCube = getCubeCoords(([xMin,xMax],[yMin,yMax],[zMin,zMax]))
    ci = np.array((xCube, yCube, zCube)).T
    # Linear interpolation 
    vi = griddata(p, np.ones((p.shape[0],)), ci, method='linear', fill_value=0)
    # Delete points outside the convex hull
    idx = np.nonzero(vi == 0)[0]
    cInternal = np.delete(ci, idx, axis=0)
    return cInternal

def getCubeCoords(S):
    """Create cube or parallelepipedon coordinates.
    
    Parameters
    ----------
    S : mixed
        Parallelepipedon or cube size.
        If int, it represents the cube side, and must be an odd number. 
        The coordinates origin is in the center of the cube.
        If list, it must contain 3 lists (for x, y and z), each one containing mininum and maximum coordinate values.
    
    Returns
    -------
    list
        List of 3 ``np.ndarray`` objects (for x, y and z), containing coordinate values into the parallelepipedon / cube.
    
    """
    if hasattr(S,'__len__') == False:
        l1, l2 = -(S-1)/2, (S-1)/2
        xx, yy, zz = np.mgrid[l1:l2,l1:l2,l1:l2]
    else:
        xx, yy, zz = np.mgrid[S[0][0]:S[0][1],S[1][0]:S[1][1],S[2][0]:S[2][1]]
    cx = xx.flatten()
    cy = yy.flatten()
    cz = zz.flatten()
    return cx, cy, cz
    
def getSphereCoords(r):
    """Create sphere coordinates.
    
    Parameters
    ----------
    r : int
        Radius.
    
    Returns
    -------
    list
        List of 3 ``np.ndarray`` objects (for x, y and z), containing coordinate values into sphere.
    
    """
    x, y, z = getCubeCoords(2*r+1)
    points = np.vstack((x, y, z)).T
    distance = np.power(np.sum(np.power(points,2),axis=1),.5)
    spherePoints = points[distance<=r]
    cx = spherePoints[:,0].squeeze()
    cy = spherePoints[:,1].squeeze()
    cz = spherePoints[:,2].squeeze()
    return cx, cy, cz    
    
def createRandomSpheresIn3DVA(xl, yl, zl, N=100, rMax='small'):
    """Create voxel array containing spheres with random position and radius.
    Spheres voxels have maximun gray level, the rest has minumum grey level.
    There is no internal check about spheres physically nesting into each other.
    
    Parameters
    ----------
    xl : int
        Voxel array size along x.
        
    yl : int
        Voxel array size along y.
        
    zl : int
        Voxel array size along z.
        
    N : int
        Number of spheres.
        
    rMax : mixed
        Maximum radius of the sphere.
        If 'small', it is equivalent to 5% of the largest voxel array dimension.
        If int, it is manually indicated.
    
    Returns
    -------
    np.array(uint8)
        Voxel array created.
    
    """
    V = np.zeros((xl,yl,zl), dtype=np.uint8)
    if rMax == 'small':
        rMax = 0.05 * np.max((xl,yl,zl))
    centers = np.random.uniform(0., high=1., size=(N,3)) * (xl,yl,zl)
    radii = np.random.uniform(1, high=rMax, size=N)
    for i in xrange(centers.shape[0]):
        c = (getSphereCoords(radii[i]) + centers[i,:][:,None]).astype(np.int32)
        x = c[0,:].squeeze()
        y = c[1,:].squeeze()
        z = c[2,:].squeeze()
        idx = (x >= 0) & (x < xl) & (y >= 0) & (y < yl) & (z >= 0) & (z < zl)
        V[x[idx], y[idx], z[idx]] = 255
    return V


def idx2xyz(idx, xl, yl, zl):
    """Transform a list of indices of 1D array into coordinates of a 3D volume of certain sizes.
    
    Parameters
    ----------
    idx : np.ndarray
        1D array to be converted. An increment of ``idx``
        corresponds to a an increment of x. When reaching ``xl``, x is reset and 
        y is incremented of one. When reaching ``yl``, x and y are reset and z is
        incremented.
    
    xl, yl, zl : int 
        Sizes for 3D volume.
    
    Returns
    -------
    list 
        List of 3 ``np.ndarray`` objects (for x, y and z), containing coordinate value.

    """
    
    z = np.floor(idx / (xl*yl))
    r = np.remainder(idx, xl*yl)
    y = np.floor(r / xl)
    x = np.remainder(r, xl)
    return x, y, z

def xyz2idx(x, y, z, xl, yl, zl, idx='counter'):
    """Transform coordinates of a 3D volume of certain sizes into a list of indices of 1D array.
    This is the opposite of function ``idx2xyz()``.
    
    Parameters
    ----------
    x, y, z : np.ndarray
        Coordinates to be converted.
        
    xl, yl, zl : int
        Sizes for 3D volume.
        
    idx: str
        Str ing indicating output type.
        If 'counter', the output is an array of voxel IDs, incrementing while x coordinate is incrementing.
        If 'list', a list (z,y,x) is created.
    
    Returns
    -------
    np.ndarray or list
        Voxel indices.

    """
    
    x[x >= xl] = xl-1
    y[y >= yl] = yl-1
    z[z >= zl] = zl-1
    x[x < 0] = 0
    y[y < 0] = 0
    z[z < 0] = 0
    if idx == 'counter':
        idx = (x + y * xl + z * (xl * yl)).astype(np.int32)
    elif idx == 'list':
        idx = (z.astype(np.int32), y.astype(np.int32), x.astype(np.int32))
    return idx

def nparray2vtkImageData(v, d, s, vtkScalarType):
    """Transform a 1D ``numpy`` array into ``vtk.vtkImageData`` object.
    The object contains only one scalar component.

    Parameters
    ----------
    v : np.ndarray
        1D array to convert.

    d : list
        3-elem list of sizes of the ``vtk.vtkImageData``.

    s : list
        3-elem list of spacing factors of the ``vtk.vtkImageData`` (see `here <http://www.vtk.org/doc/nightly/html/classvtkImageData.html#ab3288d13810266e0b30ba0632f7b5b0b>`_).

    vtkScalarType :
        Scalar type to be allocated (e.g. ``vtk.VTK_UNSIGNED_CHAR``).

    Returns
    -------
    vtk.vtkImageData
        object.

    """

    # Create source
    source = vtk.vtkImageData()
    source.SetDimensions(int(d[0]), int(d[1]), int(d[2]))
    if vtk.VTK_MAJOR_VERSION <= 5:
        source.SetNumberOfScalarComponents(1)
        source.SetScalarType(vtkScalarType)
        source.AllocateScalars()
    else:
        source.AllocateScalars(vtkScalarType, 1);
    source.SetSpacing(s[0], s[1], s[2])
    # Copy numpy voxel array to vtkDataArray
    dataArray = nps.numpy_to_vtk(v, deep=0, array_type=None)
    source.GetPointData().GetScalars().DeepCopy(dataArray)
    return source

def vtkImageData2vti(filePath, source):
    """Export a ``vtk.vtkImageData`` object to VTI file.

    Parameters
    ----------
    filePath : str
        Full path for the VTI to be created.

    source : vtk.vtkImageData
        object.

    """
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(filePath)
    if vtk.VTK_MAJOR_VERSION <= 5:
        writer.SetInput(source)
    else:
        writer.SetInputData(source)
    writer.Write()    
    
def compound3D(V1, V2, S1, S2, O):
    
    # Show raw volumes
    
    image1 = sitk.GetImageFromArray(V1)
    image2 = sitk.GetImageFromArray(V2)
    
    # Show raw solhouettes
    
    content1 = sitk.GetImageFromArray(S1)
    content2 = sitk.GetImageFromArray(S2) 
    
    # Set the 3D rigid registration framework
    
    fixed = sitk.Cast(image1, sitk.sitkFloat32)
    moving = sitk.Cast(image2, sitk.sitkFloat32)
    fixedContent = sitk.Cast(content1, sitk.sitkFloat32)
    movingContent = sitk.Cast(content2, sitk.sitkFloat32)
    
    def command_iteration(method) :
        print("{0:3} = {1:10.5f} : {2}".format(method.GetOptimizerIteration(),
                                       method.GetMetricValue(),
                                       method.GetOptimizerPosition()))
    
    R = sitk.ImageRegistrationMethod()
    
    #R.SetMetricAsCorrelation()
    #R.SetMetricAsJointHistogramMutualInformation()
    R.SetMetricAsMattesMutualInformation()
    R.SetOptimizerAsRegularStepGradientDescent(learningRate=1.0,
                                               minStep=1e-4,
                                               numberOfIterations=500,
                                               gradientMagnitudeTolerance=1e-3
                                               )
    R.SetOptimizerScalesFromJacobian() 
    #R.SetOptimizerScalesFromPhysicalShift()
    
#    tx = sitk.VersorRigid3DTransform()
    
#    tx = sitk.AffineTransform(3)
    
#    transfromDomainMeshSize = (1,1,1)
#    tx = sitk.BSplineTransformInitializer(fixed, transfromDomainMeshSize)
    
    displacement_image = sitk.Image(fixed.GetSize(), sitk.sitkVectorFloat64)
    tx = sitk.DisplacementFieldTransform(displacement_image)
    
    R.SetInitialTransform(tx)
    
    R.SetInterpolator(sitk.sitkLinear)
    
    R.AddCommand( sitk.sitkIterationEvent, lambda: command_iteration(R) )
    
    # Run registration 
    
#    R.SetMetricFixedMask(content1)
#    R.SetMetricMovingMask(content2)
    content12 = sitk.GetImageFromArray(S1 & S2)
    R.SetMetricFixedMask(content12)
    R.SetMetricMovingMask(content12)
    try:
        outTx = R.Execute(fixed, moving)
    except Exception as e:
        print 'General error during registration'
        print e
        outTx = tx
    
    print("-------")
    print(outTx)
    print("Optimizer stop condition: {0}".format(R.GetOptimizerStopConditionDescription()))
    print(" Iteration: {0}".format(R.GetOptimizerIteration()))
    print(" Metric value: {0}".format(R.GetMetricValue()))
    
    # Run resampler for image compounding
    
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixed)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(0)
    resampler.SetTransform(outTx)    
    movingRes = resampler.Execute(moving)
    image2Res = sitk.Cast(movingRes, sitk.sitkUInt8)
    
    # Run resampler for silhouette compounding
    
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(fixedContent)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(0)
    resampler.SetTransform(outTx)    
    movingContentRes = resampler.Execute(movingContent)
    content2Res = sitk.Cast(movingContentRes, sitk.sitkUInt8)
    
    # Create other useful images
    V2r = sitk.GetArrayFromImage(image2Res)
    B1 = S1 > 0
    B2 = S2 > 0
    B2r = sitk.GetArrayFromImage(content2Res) > 0
    V12r = V1.copy()
    V12r[B2r] = V2r[B2r] # puts image 2 on top of image 1
    V2r1 = V2r.copy()
    V2r1[B1] = V1[B1]    # puts image 1 on top of image 2
    V12rMax = np.maximum(V1, V2r)
    V12 = V1.copy()
    V12[B2] = V2[B2]     # puts image 2 on top of image 1
    V21 = V2.copy()
    V21[B1] = V1[B1]     # puts image 1 on top of image 2
    V12Max = np.maximum(V1, V2)
    
    # Show all data
    I = sitk.Compose((
                      content1/2.+content2/2., # silhouettes overlapping
                      image1, # fixed
                      image2, # moving
                      image1, # fixed
                      image2Res, # result moving
                      sitk.GetImageFromArray(V12), # moving on top of fixed
                      sitk.GetImageFromArray(V12r), # result moving on top of fixed
                      sitk.GetImageFromArray(V21), # fixed on top of moving
                      sitk.GetImageFromArray(V2r1), # fixed on top of result moving
                      sitk.GetImageFromArray(V12Max), # element-wise max between fixed and moving
                      sitk.GetImageFromArray(V12rMax), # element-wise max between fixed and result moving
                    ))
    sitk.Show(I)
    
    # Get data
    tx = sitk.VersorRigid3DTransform(outTx.GetInverse())
#    tx = sitk.VersorRigid3DTransform(outTx)
    
#    tx = sitk.AffineTransform(outTx.GetInverse())
#    tx = sitk.AffineTransform(outTx)
    
    # See http://insightsoftwareconsortium.github.io/SimpleITK-Notebooks/22_Transforms.html#Global-Transformations    
    C = np.array(O)[:,None]
    A = np.array(tx.GetMatrix()).reshape((3,3))[::-1,::-1]
    t = np.array(tx.GetTranslation())[:,None][::-1]
    c = np.array(tx.GetCenter())[:,None][::-1] + C
    print A
    print t
    print c
    
    return A, t, c
    
    