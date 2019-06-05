"""This is code taken from https://github.com/sjawhar/focus-stacking
which implements the methods described in http://www.ece.drexel.edu/courses/ECE-C662/notes/LaplacianPyramid/laplacian2011.pdf"""
from multiprocessing import Queue, Process, Pool

import numpy as np

import logging

from CrystalMatch.dls_focusstack.focus.pyramid import Pyramid
from CrystalMatch.dls_imagematch import logconfig

from pyramid_level import PyramidLevel

def entropy_diviation(parameters):
    """On the top level of the pyramid (the one with the lowest resolution) two fusion operators:
    entropy and deviation are used"""
    pyramid_layer = parameters[0]
    kernel_size = parameters[1]

    gray_image = pyramid_layer
    gray_image.entropy(kernel_size)
    gray_image.deviation(kernel_size)

    log = logging.getLogger(".".join([__name__]))
    log.addFilter(logconfig.ThreadContextFilter())
    log.debug("Calculated entropy/div for top level of layer: " + str(gray_image.get_layer_number()))
    return gray_image

def fused_laplacian(parameters):
    """On other levels of the pyramid one fusion operator: region energy is used"""
    laplacians = parameters[0]
    region_kernel = parameters[1]
    level = parameters[2]

    layers = laplacians.shape[0]
    region_energies = np.zeros(laplacians.shape[:3], dtype=np.float64)

    for layer in range(layers):
        gray_lap = PyramidLevel(laplacians[layer], layer, level)
        region_energies[layer] = gray_lap.region_energy(region_kernel)

    best_re = np.argmax(region_energies, axis=0)
    fused = np.zeros(laplacians.shape[1:], dtype=laplacians.dtype)

    for layer in range(layers):
        fused += np.where(best_re[:, :] == layer, laplacians[layer], 0)

    log = logging.getLogger(".".join([__name__]))
    log.addFilter(logconfig.ThreadContextFilter())
    log.debug("Level: " + str(level) + " fused!")

    fused_level = PyramidLevel(fused,0,level)
    return fused_level

class PyramidCollection:
    """Pyramid collection: collection of pyramids."""
    def __init__(self):
        self.collection = []

    def get_number_of_layers(self):
        return len(self.collection)

    def add_pyramid(self, pyramid):
        self.collection.append(pyramid)

    def get_pyramid(self, layer_number):
        return self.collection[layer_number]

    def get_region_kernel(self):
        a = 0.4
        kernel = np.array([0.25 - a / 2.0, 0.25, a, 0.25, 0.25 - a / 2.0])
        return np.outer(kernel, kernel)

    def fuse(self, kernel_size):
        """Function which fuses each level of the pyramid using appropriate fusion operators
        the output is one pyramid containing fused levels"""
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())

        base_level_fused = self.get_fused_base(kernel_size)
        depth = self.collection[0].get_depth()
        fused = Pyramid(0,depth)
        fused.add_lower_resolution_level(base_level_fused)
        layers = len(self.collection)
        region_kernel = self.get_region_kernel()
        parameters = []
        for level in range(depth - 2, -1, -1):
            sh = self.collection[0].get_level(level).get_array().shape
            laplacians = np.zeros((layers, sh[0], sh [1]), dtype=np.float64)
            for layer in range(0, layers):
                new_level = self.collection[layer].get_level(level).get_array()
                laplacians[layer] = new_level
            param = (laplacians, region_kernel,level)
            parameters.append(param)
        pool = Pool()
        results = pool.map_async(fused_laplacian, parameters)
        bunch = results.get()
        pool.close()
        pool.join()

        fused.add_bunch_of_levels(bunch)

        fused.sort_levels()
        return fused

    def get_fused_base(self, kernel_size):
        """Fuses the base of the pyramid - the one with the lowest resolution."""

        layers = len(self.collection)
        sh = self.collection[0].get_top_level().get_array().shape
        pyramid = self.collection[0]
        top_level_number = pyramid.get_depth() - 1
        entropies = np.zeros((layers, sh[0], sh[1]), dtype=np.float64)
        deviations = np.copy(entropies)
        parameters = []
        for layer in range(layers):
            pyramid = self.collection[layer]
            top_pyramid_level = pyramid.get_top_level()
            layer = PyramidLevel(top_pyramid_level.get_array(), layer, top_level_number)
            param = (layer, kernel_size)
            parameters.append(param)
        pool = Pool()
        results = pool.map_async(entropy_diviation, parameters)
        result_layers = results.get()
        pool.close()
        pool.join()
        for l in result_layers:
            entropies[l.get_layer_number()] = l.get_entropies()
            deviations[l.get_layer_number()] = l.get_deviations()

        best_e = np.argmax(entropies, axis=0) #keeps the layer numbers
        best_d = np.argmax(deviations, axis=0)
        fused = np.zeros(best_d.shape, dtype=np.float64)

        for layer in range(layers):
            array_tmp = self.collection[layer].get_top_level().get_array()
            fused += np.where(best_e[:, :] == layer, array_tmp, 0)
            fused += np.where(best_d[:, :] == layer, array_tmp, 0)

        new_array = (fused / 2)
        return PyramidLevel(new_array,0,top_level_number) # layer 0 ???

