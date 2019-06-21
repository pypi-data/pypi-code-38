#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.io.base
import scipy
algorithm = bob.bio.base.algorithm.LDA(pca_subspace_dimension = 0.95, distance_function = scipy.spatial.distance.euclidean, 
                                       is_distance_function = True, use_pinv=True)

