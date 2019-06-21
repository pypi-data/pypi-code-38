#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

####### PREPROCESSOR #########

from bob.bio.face.preprocessor import FaceCrop, TanTriggs
from bob.bio.htface.preprocessor import DoG_Pyramid
import numpy

#CROPPED_IMAGE_HEIGHT = 80
#CROPPED_IMAGE_WIDTH = 64
CROPPED_IMAGE_HEIGHT = 120
CROPPED_IMAGE_WIDTH = 120


# eye positions for frontal images
#RIGHT_EYE_POS = (CROPPED_IMAGE_HEIGHT // 5, CROPPED_IMAGE_WIDTH // 4 - 1)
#LEFT_EYE_POS = (CROPPED_IMAGE_HEIGHT // 5, CROPPED_IMAGE_WIDTH // 4 * 3)

#RIGHT_EYE_POS = (34, 40)
#LEFT_EYE_POS = (34, 80)

RIGHT_EYE_POS = (30, 30)
LEFT_EYE_POS = (30, 90)


cropper = FaceCrop(
                        cropped_image_size=(CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH),
                        cropped_positions={'leye': LEFT_EYE_POS, 'reye': RIGHT_EYE_POS}
             )
             
             
sigmas = list(numpy.arange(1, 2.1, 0.5))
scales = [2,3] 

filters = []
for s in sigmas:
    for c in scales:
        filters.append(TanTriggs(cropper, size=c, alpha=0.1, sigma0=s, sigma1=s+1))

             
preprocessor = DoG_Pyramid(filters)



####### EXTRACTOR #########
import bob.ip.base
from bob.bio.htface.extractor import HoG, MLBPHS, ParallelConcatenatedExtractor

hog = HoG(bob.ip.base.HOG(image_size = (CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH), block_size=(32, 32), cell_size=(32, 32)))
lbp = MLBPHS(block_size=(32, 32), block_overlap=(16, 16), lbp_radius=[1, 3],
             lbp_uniform=True, lbp_circular=True)
    
extractor = ParallelConcatenatedExtractor([hog, lbp])

#extractor =  HoG(bob.ip.base.HOG(image_size = (CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH)))


### MATCHER

import bob.bio.base                    
import scipy
algorithm = algorithm = bob.bio.base.algorithm.LDA(
    pca_subspace_dimension = 0.95,
    distance_function = scipy.spatial.distance.euclidean,
    use_pinv = True,
    is_distance_function = True)

