#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


from bob.bio.base.baseline import Baseline
import pkg_resources


class ISV_g512_u50_LBP(Baseline):
    """
    Baseline from:
    
    Freitas Pereira, Tiago, and Sébastien Marcel. "Heterogeneous Face Recognition using Inter-Session Variability Modelling." Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition Workshops. 2016.    
    
    """

    def __init__(self, **kwargs):
    
        name              = "isv-g512-u50-LBP"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_extractor_lbp.py")
        preprocessors     = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_preprocessor_lbp.py")}
        algorithm         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_g512u50.py")

        self.baseline_type     = "SOTA baselines"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None
        
        super(ISV_g512_u50_LBP, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
        

isv_g512_u50_LBP = ISV_g512_u50_LBP()


class ISV_g256_u50_LBP(Baseline):
    """
    Baseline from:
    
    Freitas Pereira, Tiago, and Sébastien Marcel. "Heterogeneous Face Recognition using Inter-Session Variability Modelling." Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition Workshops. 2016.    
    
    """

    def __init__(self, **kwargs):
    
        name              = "isv-g256-u50-LBP"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_extractor_lbp.py")
        preprocessors     = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_preprocessor_lbp.py")}
        algorithm         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_g256u50.py")

        self.baseline_type     = "SOTA baselines"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None
        
        super(ISV_g256_u50_LBP, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
        
isv_g256_u50_LBP = ISV_g256_u50_LBP()


class ISV_g128_u50_LBP(Baseline):
    """
    Baseline from:
    
    Freitas Pereira, Tiago, and Sébastien Marcel. "Heterogeneous Face Recognition using Inter-Session Variability Modelling." Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition Workshops. 2016.    
    
    """

    def __init__(self, **kwargs):
    
        name              = "isv-g128-u50-LBP"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_extractor_lbp.py")
        preprocessors     = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_preprocessor_lbp.py")}
        algorithm         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_g128u50.py")

        self.baseline_type     = "SOTA baselines"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None
        
        super(ISV_g128_u50_LBP, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
        
isv_g128_u50_LBP = ISV_g128_u50_LBP()


class ISV_g64_u50_LBP(Baseline):
    """
    Baseline from:
    
    Freitas Pereira, Tiago, and Sébastien Marcel. "Heterogeneous Face Recognition using Inter-Session Variability Modelling." Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition Workshops. 2016.    
    
    """

    def __init__(self, **kwargs):
    
        name              = "isv-g64-u50-LBP"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_extractor_lbp.py")
        preprocessors     = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_preprocessor_lbp.py")}
        algorithm         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/sota_baselines/isv_g64u50.py")

        self.baseline_type     = "SOTA baselines"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None
        
        super(ISV_g64_u50_LBP, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
        
isv_g64_u50_LBP = ISV_g64_u50_LBP()

