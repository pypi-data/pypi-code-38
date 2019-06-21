#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

from bob.bio.base.baseline import Baseline
import pkg_resources
import bob.bio.htface

# IMPORTING THE NECESSARY MODULES

# Siamese
import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_first_layer.estimator_nonshared_batch_norm
import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_first_layer.estimator_nonshared_betas_batch_norm

# TRiplet
import bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_first_layer.estimator_nonshared_batch_norm
import bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_first_layer.estimator_nonshared_betas_batch_norm


class SiameseAdaptFirstBatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the first layer only
    """

    def __init__(self, **kwargs):
    
        name            = "siamese_inceptionv2_first_layer_nonshared_batch_norm"
        extractor       = pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v2_adapt_first_layer/extractor_nonshared_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm       = "distance-cosine"

        self.reuse_extractor   = False        
        self.baseline_type     = "Siamese BN"

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_first_layer.estimator_nonshared_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptFirstBatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)


class SiameseAdaptFirstBetasBatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the first layer only
      - ADAPT ONLY THE BETAS
    """

    def __init__(self, **kwargs): 
    
        name              = "siamese_inceptionv2_first_layer_betas_nonshared_batch_norm"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v2_adapt_first_layer/extractor_nonshared_betas_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"
        
        self.baseline_type     = "Siamese BN adapt betas"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_first_layer.estimator_nonshared_betas_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptFirstBetasBatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)


class TripletAdaptFirstBatchNorm(Baseline):

    def __init__(self, **kwargs): 
    
        name              = "triplet_inceptionv2_first_layer_nonshared_batch_norm"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/triplet_transfer_learning/inception_resnet_v2_adapt_first_layer/extractor_nonshared_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Triplet BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_first_layer.estimator_nonshared_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(TripletAdaptFirstBatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)



class TripletAdaptFirstBetasBatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the first layer only
      - ADAPT ONLY THE BETAS
    """

    def __init__(self, **kwargs):
    
        name              = "triplet_inceptionv2_first_layer_betas_nonshared_batch_norm"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/triplet_transfer_learning/inception_resnet_v2_adapt_first_layer/extractor_nonshared_betas_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"


        self.baseline_type     = "Triplet BN adapt betas"
        self.reuse_extractor   = False

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_first_layer.estimator_nonshared_betas_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")
        
        super(TripletAdaptFirstBetasBatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
        
        
inception_resnet_v2_siamese_adapt_first = SiameseAdaptFirstBatchNorm()
inception_resnet_v2_siamese_adapt_first_betas = SiameseAdaptFirstBetasBatchNorm()

inception_resnet_v2_triplet_adapt_first = TripletAdaptFirstBatchNorm()
inception_resnet_v2_triplet_adapt_first_betas = TripletAdaptFirstBetasBatchNorm()
