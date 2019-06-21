#!/usr/bin/env python

import bob.bio.face

# preprocessor
# This is the size of the image that this model expects
CROPPED_IMAGE_HEIGHT = 128
CROPPED_IMAGE_WIDTH = 128
# eye positions for frontal images
RIGHT_EYE_POS = (32, 44)
LEFT_EYE_POS = (32, 84)

# Detects the face and crops it with eye detection
preprocessor = bob.bio.face.preprocessor.FaceDetect(
    face_cropper=bob.bio.face.preprocessor.FaceCrop(
        cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
        cropped_positions={'leye': LEFT_EYE_POS, 'reye': RIGHT_EYE_POS}),
    use_flandmark=True,
)

# Detects the face and crops it using eye annotations
preprocessor_eyes = bob.bio.face.preprocessor.FaceCrop(
    cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
    cropped_positions={'leye': LEFT_EYE_POS, 'reye': RIGHT_EYE_POS},
)
