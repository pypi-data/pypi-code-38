#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import pkg_resources
from bob.bio.base.baseline import Baseline


class RankONE(Baseline):
    """
    RankONE Baseline
    """

    def __init__(self, **kwargs):

        name              = "rank-one"
        extractor         = "rank-one"
        preprocessors      = dict()
        preprocessors["default"] = "rank-one"
        algorithm = "rank-one"

        self.baseline_type     = "Standard FaceRec"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None

        super(RankONE, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
       

rank_one = RankONE()

