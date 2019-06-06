
import numpy as np
from scipy.ndimage.morphology import binary_erosion


def spherality(region):
    eroded = binary_erosion(region)
    surface = region ^ eroded

    S = np.sum(surface)
    V = np.sum(region)

    mult = 4.5 * np.sqrt(np.pi)

    return mult * V / np.power(S, 1.5)
