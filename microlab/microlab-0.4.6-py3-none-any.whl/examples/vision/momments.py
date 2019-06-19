from microlab.io.images import read_image
from microlab.vision.momments import cv2_momments

import os

mask_path = os.path.join(os.getcwd(),'8.jpg')
mask = read_image(path=mask_path)

