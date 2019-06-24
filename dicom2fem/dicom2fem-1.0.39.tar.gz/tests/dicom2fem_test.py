# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
import unittest
import dicom2fem

import os.path as op
import numpy as np

def donut():
    """
    Generate donut like shape with stick inside

    :return: datap with keys data3d, segmentation and voxelsize_mm
    """
    import numpy as np
    segmentation = np.zeros([20, 30, 40])
    # generate test data
    segmentation[6:10, 7:24, 10:37] = 1
    segmentation[6:10, 7, 10] = 0
    segmentation[6:10, 23, 10] = 0
    segmentation[6:10, 7, 36] = 0
    segmentation[6:10, 23, 36] = 0
    segmentation[2:18, 12:19, 18:28] = 2

    data3d = segmentation * 100 + np.random.random(segmentation.shape) * 30
    voxelsize_mm=[3,2,1]

    import io3d
    datap = {
        'data3d': data3d,
        'segmentation': segmentation,
        'voxelsize_mm': voxelsize_mm
    }
    # io3d.write(datap, "donut.pklz")
    return datap

class MyTestCase(unittest.TestCase):
    def test_mc(self):

        import dicom2fem.seg2fem
        output_fn = "donut.vtk"
        datap = donut()
        segmentation = datap["segmentation"] == 1
        voxelsize_mm = datap["voxelsize_mm"]
        segmentation = np.zeros([100,121,122])
        segmentation[50:73,50:73,50:73]=1
        mesh_data = dicom2fem.seg2fem.gen_mesh_from_voxels_mc(segmentation, voxelsize_mm)
        # if smoothing:
        #     mesh_data.coors = smooth_mesh(mesh_data)
            # mesh_data.coors = seg2fem.smooth_mesh(mesh_data)

        # else:
        #     pass
        #     # mesh_data = gen_mesh_from_voxels_mc(segmentation, voxelsize_mm * 1.0e-2)
        #     # mesh_data.coors +=
        mesh_data.write(op.expanduser(output_fn))
        op.exists(output_fn)


    def test_mc_skimage(self):
        import dicom2fem.seg2fem
        import skimage.measure
        datap = donut()
        segmentation = datap["segmentation"] == 1
        voxelsize_mm = datap["voxelsize_mm"]
        segmentation = np.zeros([100,121,122])
        segmentation[50:73,50:73,50:73]=1

        # verts, faces, normals, values = skimage.measure.marching_cubes(segmentation, level=1, spacing=voxelsize_mm)
        verts, faces = skimage.measure.marching_cubes(segmentation, level=0)#, spacing=voxelsize_mm)
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        mesh_data = Poly3DCollection(verts[faces])
        # mesh_data = dicom2fem.seg2fem.gen_mesh_from_voxels_mc(segmentation, voxelsize_mm)
        # if smoothing:
        #     mesh_data.coors = smooth_mesh(mesh_data)
        # mesh_data.coors = seg2fem.smooth_mesh(mesh_data)

        # else:
        #     pass
        #     # mesh_data = gen_mesh_from_voxels_mc(segmentation, voxelsize_mm * 1.0e-2)
        #     # mesh_data.coors +=
        import vtk.util.numpy_support
        vtkim = vtk.util.numpy_support.numpy_to_vtk(segmentation)
        mesh_data.write(op.expanduser("donut.vtk"))


    def test_mc_skimage_orig_example(self):
        import numpy as np
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection

        from skimage import measure
        from skimage.draw import ellipsoid


        # Generate a level set about zero of two identical ellipsoids in 3D
        ellip_base = ellipsoid(6, 10, 16, levelset=True)
        ellip_double = np.concatenate((ellip_base[:-1, ...],
                                       ellip_base[2:, ...]), axis=0)

        # Use marching cubes to obtain the surface mesh of these ellipsoids
        # outs = measure.marching_cubes(ellip_double, 0)
        # verts, faces, normals, values = measure.marching_cubes(ellip_double, 0)
        verts, faces = measure.marching_cubes(ellip_double, 0)

        # Display resulting triangular mesh using Matplotlib. This can also be done
        # with mayavi (see skimage.measure.marching_cubes docstring).
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')

        # Fancy indexing: `verts[faces]` to generate a collection of triangles
        mesh = Poly3DCollection(verts[faces])
        mesh.set_edgecolor('k')
        ax.add_collection3d(mesh)

        ax.set_xlabel("x-axis: a = 6 per ellipsoid")
        ax.set_ylabel("y-axis: b = 10")
        ax.set_zlabel("z-axis: c = 16")

        ax.set_xlim(0, 24)  # a = 6 (times two for 2nd ellipsoid)
        ax.set_ylim(0, 20)  # b = 10
        ax.set_zlim(0, 32)  # c = 16

        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    unittest.main()
