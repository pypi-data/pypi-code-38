#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import bob.bio.face
from bob.bio.base.preprocessor import SequentialPreprocessor, CallablePreprocessor
from bob.bio.face.preprocessor import FaceCrop
import bob.ip.color

# This is the size of the image that this model expects
CROPPED_IMAGE_HEIGHT = 224
CROPPED_IMAGE_WIDTH = 224
# eye positions for frontal images
RIGHT_EYE_POS = (65, 74)
LEFT_EYE_POS = (65, 150)


# Detects the face and crops it without eye detection
facecrop = FaceCrop(
    cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
    cropped_positions={'leye': LEFT_EYE_POS, 'reye': RIGHT_EYE_POS},
    color_channel='rgb'
)


class GraytoRGB(object):
    def __call__(self, data, annotations=None):
        """
        Light CNN needs to be [0-1] normalized 
        """

        if(data.ndim==2):
            return bob.ip.color.gray_to_rgb(data)
        return data

preprocessor = SequentialPreprocessor([CallablePreprocessor(GraytoRGB()), facecrop])

