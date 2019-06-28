import skimage
import os as _os
import os.path as osp
from skimage import *

data_dir = osp.abspath(osp.dirname(__file__))


def load_infection_example_image():
    """Reads an example image classified with infection.

    Returns:
      An image classified with infection.
    """
    return skimage.io.imread(_os.path.join(data_dir, 'images/image_infection.png'))


def load_noinfection_example_image():
    """Reads an example image classified without infection.

    Returns:
      An image classified without infection.
    """
    return skimage.io.imread(_os.path.join(data_dir, 'images/image_noinfection.png'))
