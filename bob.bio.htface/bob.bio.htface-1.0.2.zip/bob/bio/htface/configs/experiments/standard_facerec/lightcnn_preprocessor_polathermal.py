#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import bob.bio.face
from bob.bio.base.preprocessor import SequentialPreprocessor, CallablePreprocessor

CROPPED_IMAGE_HEIGHT = 128
CROPPED_IMAGE_WIDTH = 128

# eye positions for frontal images
#RIGHT_EYE_POS = (32, 44)
#LEFT_EYE_POS = (32, 84)
RIGHT_EYE_POS = (35, 35)
LEFT_EYE_POS = (35, 71)


# Detects the face and crops it without eye detection
facecrop = bob.bio.face.preprocessor.FaceCrop(
  cropped_image_size = (CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
  cropped_positions = {'leye' : LEFT_EYE_POS, 'reye' : RIGHT_EYE_POS},
  color_channel='gray'
)


class Normalizer(object):
    def __call__(self, data, annotations=None):
        """
        Light CNN needs to be [0-1] normalized 
        """

        return data/65536.

preprocessor = SequentialPreprocessor([facecrop, CallablePreprocessor(Normalizer())])

