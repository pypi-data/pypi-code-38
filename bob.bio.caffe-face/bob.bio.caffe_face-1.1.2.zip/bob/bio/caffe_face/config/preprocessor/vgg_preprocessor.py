#!/usr/bin/env python

import bob.bio.face

# This is the size of the image that this model expects
CROPPED_IMAGE_HEIGHT = 224
CROPPED_IMAGE_WIDTH = 224
# eye positions for frontal images
RIGHT_EYE_POS = (65, 74)
LEFT_EYE_POS = (65, 150)

# Detects the face and crops it with eye detection
preprocessor = bob.bio.face.preprocessor.FaceDetect(
  face_cropper=bob.bio.face.preprocessor.FaceCrop(
      cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
      cropped_positions={'leye': LEFT_EYE_POS, 'reye': RIGHT_EYE_POS},
      color_channel='rgb'),
  use_flandmark=True,
  color_channel='rgb'
 )

# uses the eye annotations to crop the image
preprocessor_eyes = bob.bio.face.preprocessor.FaceCrop(
  cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
  cropped_positions={'leye': LEFT_EYE_POS, 'reye': RIGHT_EYE_POS},
  color_channel='rgb'
)


TOP_LEFT_POS = (0, 0)
BOTTOM_RIGHT_POS = (CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH)
# define the preprocessor
preprocessor_head = bob.bio.face.preprocessor.FaceCrop(
  cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
  cropped_positions={'topleft': TOP_LEFT_POS, 'bottomright': BOTTOM_RIGHT_POS},
  color_channel='rgb' 
)

