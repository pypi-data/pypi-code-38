import cv2
import numpy as np
from scipy import ndimage

class PyramidLevel:
    """Pyramid layer - part of a pyramid of a particular level and layer.
    Operators used in the laplacian pyramid fusion process(flattening pyramid along layers)
    are implemented in this class"""

    def __init__(self, array, layer_number, level_number):
        self.array = array
        self.layer_number = layer_number
        self.level_number = level_number
        self.deviations = []
        self.entropies = []

    def get_layer_number(self):
        return self.layer_number

    def get_level_number(self):
        return self.level_number

    def get_array(self):
        return self.array


    def region_energy(self,kernel):
        """Region energy operator used during laplacian pyramid fusion on all but the base level."""
        conv = ndimage.convolve(np.square(self.array).astype(np.float64), kernel, mode='mirror')
        return conv

    def get_probabilities(self):
        """Probabilities show how many points of a given color (grayscale level) there is in an input image/array."""
        levels, counts = np.unique(self.array.astype(np.uint8), return_counts=True)
        probabilities = np.zeros((256,), dtype=np.float64)
        probabilities[levels] = counts.astype(np.float64) / counts.sum()
        return probabilities

    @staticmethod
    def _area_entropy(area, probabilities):
        levels = area.astype(np.uint8).flatten()
        return -1. * (levels * np.log(probabilities[levels])).sum()

    def entropy(self, kernel_size):
        """Entropy operator used during laplacian pyramid fusion on the base level."""
        probabilities = self.get_probabilities()
        entropies = np.zeros(self.array.shape[:2], dtype=np.float64)
        pad_amount, padded_image, offset = self.padding(kernel_size)
        for row in range(entropies.shape[0]):
            for column in range(entropies.shape[1]):
                area = padded_image[row + pad_amount + offset[:, np.newaxis], column + pad_amount + offset]
                entropies[row, column] = self._area_entropy(area, probabilities)

        self.entropies = entropies

    def get_entropies(self):
        return self.entropies

    @staticmethod
    def _area_deviation(area):
        average = np.average(area).astype(np.float64)
        return np.square(area - average).sum() / area.size

    def deviation(self, kernel_size):
        """Deviation operator used during laplacian pyramid fusion on the base level."""
        deviations = np.zeros(self.array.shape[:2], dtype=np.float64)
        pad_amount, padded_image, offset = self.padding(kernel_size)
        for row in range(deviations.shape[0]):
            for column in range(deviations.shape[1]):
                area = padded_image[row + pad_amount + offset[:, np.newaxis], column + pad_amount + offset]
                deviations[row, column] = self._area_deviation(area)

        self.deviations = deviations

    def get_deviations(self):
        return self.deviations

    def padding(self, kernel_size):
        pad_amount = int((kernel_size - 1) / 2)
        padded_image = cv2.copyMakeBorder(self.array, pad_amount, pad_amount, pad_amount, pad_amount,
                                          cv2.BORDER_REFLECT101)
        offset = np.arange(-pad_amount, pad_amount + 1)
        return pad_amount, padded_image, offset