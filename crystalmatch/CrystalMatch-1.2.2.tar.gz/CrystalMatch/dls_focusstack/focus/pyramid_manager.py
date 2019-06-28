#This is code based upon https://github.com/sjawhar/focus-stacking
#which implements the methods described in http://www.ece.drexel.edu/courses/ECE-C662/notes/LaplacianPyramid/laplacian2011.pdf

import cv2
import numpy as np

from CrystalMatch.dls_focusstack.focus.pyramid import Pyramid
from CrystalMatch.dls_focusstack.focus.pyramid_level import PyramidLevel

from CrystalMatch.dls_focusstack.focus.pyramid_collection import PyramidCollection


class PyramidManager:
    """This is a pyramid manages class."""

    def __init__(self, aligned_images, config):
        self.images = aligned_images
        self.config = config

    def get_pyramid_fusion(self):
        """This is the function which maintains the steps of pyramid processing.
        It creates the laplacian pyramid,
        starts the fusion process which flattens the pyramid along layers and finally collapses the pyramid."""
        smallest_side = min(self.images[0].shape[:2])
        cfg = self.config
        min_size = cfg.pyramid_min_size.value()
        depth = int(np.log2(smallest_side / min_size))+1
        kernel_size = cfg.kernel_size.value()
        #create pyramid
        pyramid_collection = self.laplacian_pyramid(depth)
        #fuse pyramid
        fusion = pyramid_collection.fuse(kernel_size)
        #collaps pyramid
        return fusion.collapse()

    #this is only used by the laplacian pyramid function
    def _gaussian_pyramid(self, depth):
        """Creates the gaussian pyramid of a certain depth"""
        pyramid_collection = PyramidCollection()
        for layer_number, image in enumerate(self.images):
            pyramid = Pyramid(layer_number, depth)
            level = PyramidLevel(image.astype(np.float64), layer_number, 0)
            pyramid.add_lower_resolution_level(level)
            for level_number in range(1, depth): #check the depth
                image = cv2.pyrDown(image.astype(np.float64))
                next_level = PyramidLevel(image, layer_number, level_number)
                pyramid.add_lower_resolution_level(next_level)
            pyramid_collection.add_pyramid(pyramid)
        return pyramid_collection

    def laplacian_pyramid(self, depth):
        """Create laplacian pyramid of a certain depth."""
        laplacian_collection = PyramidCollection()
        gaussian_collection = self._gaussian_pyramid(depth)
        for layer_number, image in enumerate(self.images):
            gaussian_pyramid = gaussian_collection.get_pyramid(layer_number)
            gaussian_top_level = gaussian_pyramid.get_top_level() # the lowest resolution
            laplacian_pyramid = Pyramid(layer_number, depth)
            laplacian_pyramid.add_higher_resolution_level(gaussian_top_level)
            for level_number in range(depth-1, 0, -1):
                to_expand = gaussian_pyramid.get_level(level_number).get_array()
                expanded = cv2.pyrUp(to_expand)
                lower_level = gaussian_pyramid.get_level(level_number-1).get_array()
                if expanded.shape != lower_level.shape:
                    expanded = expanded[:lower_level.shape[0], :lower_level.shape[1]]
                difference = lower_level - expanded
                difference_level = PyramidLevel(difference, layer_number, level_number)
                laplacian_pyramid.add_higher_resolution_level(difference_level)
            laplacian_collection.add_pyramid(laplacian_pyramid)
        return laplacian_collection

