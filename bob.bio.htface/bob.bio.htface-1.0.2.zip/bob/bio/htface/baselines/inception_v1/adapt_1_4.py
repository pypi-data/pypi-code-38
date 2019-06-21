#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


from bob.bio.base.baseline import Baseline
import pkg_resources
import bob.bio.htface

# IMPORTING THE NECESSARY MODULES

# Siamese
import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v1_adapt_layers_1_4.estimator_nonshared_batch_norm
import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v1_adapt_layers_1_4.estimator_nonshared_betas_batch_norm

# Triplet
import bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v1_adapt_layers_1_4.estimator_nonshared_batch_norm
import bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v1_adapt_layers_1_4.estimator_nonshared_betas_batch_norm


class SiameseAdaptLayers1_4_BatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1_4 layers
    """

    def __init__(self, **kwargs):

        name              = "siamese_inceptionv1_adapt_1_4_nonshared_batch_norm"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v1_adapt_layers_1_4/extractor_nonshared_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm       = "distance-cosine"

        self.baseline_type     = "Siamese BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v1_adapt_layers_1_4.estimator_nonshared_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptLayers1_4_BatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)


class SiameseAdaptLayers1_4_BetasBatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1_4 layers
    """

    def __init__(self, **kwargs):

        name              = "siamese_inceptionv1_adapt_1_4_betas_nonshared_batch_norm"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v1_adapt_layers_1_4/extractor_nonshared_betas_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm       = "distance-cosine"

        self.baseline_type     = "Siamese BN adapt betas"
        self.reuse_extractor   = False

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v1_adapt_layers_1_4.estimator_nonshared_betas_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/") # Same as v2
        
        super(SiameseAdaptLayers1_4_BetasBatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
        
        
class TripletAdaptLayers1_4_BatchNorm(Baseline):
    """
    - Adapt the 1_4 layers
    """

    def __init__(self, **kwargs):
    
        name              = "triplet_inceptionv1_layers_1_4_nonshared_batch_norm"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/triplet_transfer_learning/inception_resnet_v1_adapt_layers_1_4/extractor_nonshared_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm       = "distance-cosine"

        self.baseline_type     = "Triplet BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v1_adapt_layers_1_4.estimator_nonshared_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")
        
        super(TripletAdaptLayers1_4_BatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)        
        

class TripletAdaptLayers1_4_BetasBatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1_4 layers
      - ADAPT ONLY THE BETAS
    """

    def __init__(self, **kwargs):

        name              = "triplet_inceptionv1_layers_1_4_betas_nonshared_batch_norm"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/triplet_transfer_learning/inception_resnet_v1_adapt_layers_1_4/extractor_nonshared_betas_batch_norm.py")
        
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"
            
        self.baseline_type     = "Triplet BN adapt betas"
        self.reuse_extractor   = False

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v1_adapt_layers_1_4.estimator_nonshared_betas_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")        

        super(TripletAdaptLayers1_4_BetasBatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
        
# Entry points
inception_resnet_v1_siamese_adapt_1_4 = SiameseAdaptLayers1_4_BatchNorm()
inception_resnet_v1_siamese_adapt_1_4_betas = SiameseAdaptLayers1_4_BetasBatchNorm()

inception_resnet_v1_triplet_adapt_1_4 = TripletAdaptLayers1_4_BatchNorm()
inception_resnet_v1_triplet_adapt_1_4_betas = TripletAdaptLayers1_4_BetasBatchNorm()
