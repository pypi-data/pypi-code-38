#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

from bob.bio.face.preprocessor import FaceCrop
from bob.bio.face.preprocessor import TanTriggs

CROPPED_IMAGE_HEIGHT = 250
CROPPED_IMAGE_WIDTH = 200

# eye positions for frontal images
RIGHT_EYE_POS = (CROPPED_IMAGE_HEIGHT // 5, CROPPED_IMAGE_WIDTH // 4 - 1)
LEFT_EYE_POS = (CROPPED_IMAGE_HEIGHT // 5, CROPPED_IMAGE_WIDTH // 4 * 3)

face_cropper = FaceCrop(
                        cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
                        cropped_positions={'leye': LEFT_EYE_POS, 'reye': RIGHT_EYE_POS}
             )

preprocessor = TanTriggs(face_cropper=face_cropper)

