#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.bio.htface

algorithm = bob.bio.htface.algorithm.GFK_GaborJet(number_of_subspaces=40,
                                                  source_subspace_dimension=19,
                                                  target_subspace_dimension=19,
                                                  use_lda=False)
