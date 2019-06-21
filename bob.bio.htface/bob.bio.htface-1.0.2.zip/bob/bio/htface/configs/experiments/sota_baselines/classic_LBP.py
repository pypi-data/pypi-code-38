#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

####### PREPROCESSOR #########

from bob.bio.face.preprocessor import FaceCrop

CROPPED_IMAGE_HEIGHT = 250
CROPPED_IMAGE_WIDTH = 200

# eye positions for frontal images
RIGHT_EYE_POS = (CROPPED_IMAGE_HEIGHT // 5, CROPPED_IMAGE_WIDTH // 4 - 1)
LEFT_EYE_POS = (CROPPED_IMAGE_HEIGHT // 5, CROPPED_IMAGE_WIDTH // 4 * 3)

preprocessor = FaceCrop(
                        cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
                        cropped_positions={'leye': LEFT_EYE_POS, 'reye': RIGHT_EYE_POS}
             )


####### EXTRACTOR #########

from bob.bio.htface.extractor import MLBPHS

extractor =  MLBPHS(block_size=(32, 32),
                    block_overlap=(16, 16),
                    lbp_radius=[2],
                    lbp_uniform=True,
                    lbp_circular=True)



### MATCHER

import bob.bio.face                    
                    
algorithm = bob.bio.face.algorithm.Histogram( distance_function = bob.math.chi_square, is_distance_function = True)

