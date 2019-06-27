import skimage
import os as _os
import os.path as osp
from skimage import *

data_dir = osp.abspath(osp.dirname(__file__))


def load_infection_example_image():
    return skimage.io.imread(_os.path.join(data_dir, 'images/image_infection.png'))


def load_noinfection_example_image():
    return skimage.io.imread(_os.path.join(data_dir, 'images/image_noinfection.png'))
