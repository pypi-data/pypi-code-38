import os, sys
import time
import argparse
import numpy as np

import bob.io.base
import bob.io.base.test_utils
import bob.io.image
import bob.io.video
import bob.ip.color

import bob.ip.facelandmarks as menpo
from bob.ip.facelandmarks.utils import detect_landmarks, draw_landmarks, save_landmarks, Result
from bob.ip.facelandmarks.utils import detect_landmarks_on_boundingbox

from PIL import Image, ImageDraw
from bob.ip.draw import box, cross, plus

import matplotlib
from matplotlib import pyplot
import pkg_resources

#1. load image
color_image = bob.io.base.load(bob.io.base.test_utils.datafile('lena.jpg', 'bob.ip.facelandmarks'))
gray_image = bob.ip.color.rgb_to_gray(color_image)
#2. extract feature-points
frameKeypoints = menpo.utils.detect_landmarks(gray_image, 1)
landmarks = frameKeypoints[0].landmarks
#3. plot landmarks on image
lmkImage = np.copy(gray_image)
menpo.utils.draw_landmarks(lmkImage, frameKeypoints)
pyplot.imshow(lmkImage.astype(np.uint8), cmap=matplotlib.cm.gray)         
pyplot.show()
