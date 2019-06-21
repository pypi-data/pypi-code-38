#!/usr/bin/env python

import bob.bio.base
import scipy.spatial

#algorithm = bob.bio.base.algorithm.PLDA(
#    subspace_dimension_of_f = 16, # Size of subspace F
#    subspace_dimension_of_g = 16, # Size of subspace G
#    subspace_dimension_pca=0.99
#)

algorithm = bob.bio.base.algorithm.LDA(
    pca_subspace_dimension = 0.95,
    distance_function = scipy.spatial.distance.cosine,
    is_distance_function = True
)


