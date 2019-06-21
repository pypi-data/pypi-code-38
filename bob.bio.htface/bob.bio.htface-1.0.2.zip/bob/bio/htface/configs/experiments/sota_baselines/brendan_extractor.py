#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

from bob.bio.htface.extractor import MLBPHS

extractor =  MLBPHS(block_size=(32, 32),
                    block_overlap=(16, 16),
                    lbp_radius=[1, 3, 5, 7],
                    lbp_uniform=True,
                    lbp_circular=True)


