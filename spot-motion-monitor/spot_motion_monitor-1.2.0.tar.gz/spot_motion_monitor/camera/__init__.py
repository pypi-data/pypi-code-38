#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
names = ['Vimba', 'Gaussian']

from .base_camera import BaseCamera
from .camera_status import CameraStatus
from .gaussian_camera import GaussianCamera
try:
    from .vimba_camera import VimbaCamera
except AssertionError:
    pass
