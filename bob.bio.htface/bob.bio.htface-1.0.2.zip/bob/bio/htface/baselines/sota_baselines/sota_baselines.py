#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


from bob.bio.base.baseline import Baseline
import pkg_resources


class MLBPHS(Baseline):
    """
    Baseline from:
    
    MLBP
    
    """

    def __init__(self, **kwargs):

        name              = "mlbphs-r1357"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/brendan_extractor.py")
        preprocessors     = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/brendan_preprocessor.py")}
        algorithm         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/brendan_algorithm.py")

        self.baseline_type     = "SOTA baselines"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None
        
        super(MLBPHS, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)

htface_mlbphs = MLBPHS()


class ClassicLBP(Baseline):
    """
    Baseline from:

    """

    def __init__(self, **kwargs):

        name              = "classic_lbp"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/classic_LBP.py")
        preprocessors     = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/classic_LBP.py")}
        algorithm         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/classic_LBP.py")

        self.baseline_type     = "SOTA baselines"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None
        
        super(ClassicLBP, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)

htface_classic_lbp = ClassicLBP()


class MultiScaleFeatures(Baseline):
    """
    Baseline from:

    """

    def __init__(self, **kwargs):

        name              = "multiscale_features"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/multiscale_features.py")
        preprocessors     = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/multiscale_features.py")}
        algorithm         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/multiscale_features.py")

        self.baseline_type     = "SOTA baselines"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None
        
        super(MultiScaleFeatures, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)

htface_multiscale_features = MultiScaleFeatures()


class GFKGabor(Baseline):
    """
    Baseline from:
    
    MLBP
    
    """

    def __init__(self, **kwargs):

        name              = "gfk_gabor"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/gfk_extractor.py")
        preprocessors     = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/gfk_preprocessor.py")}
        algorithm         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/gfk_algorithm.py")

        self.baseline_type     = "SOTA baselines"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None

        super(GFKGabor, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
        
htface_gfkgabor = GFKGabor()
