#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


from bob.bio.base.baseline import Baseline
import pkg_resources

# IMPORTING THE NECESSARY MODULES

# Siamese
import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_5.estimator_nonshared_batch_norm
import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_5.estimator_nonshared_betas_batch_norm

# Triplet
import bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_layers_1_5.estimator_nonshared_batch_norm
import bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_layers_1_5.estimator_nonshared_betas_batch_norm


class SiameseAdaptLayers1_5_BatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1-5 layers
    """

    def __init__(self, **kwargs):
    
        name              = "siamese_inceptionv2_adapt_1_5_betas_nonshared_batch_norm"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v2_adapt_layers_1_5/extractor_nonshared_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Siamese BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_5.estimator_nonshared_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptLayers1_5_BatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)


class SiameseAdaptLayers1_5_BatchNorm_PLDA(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1-5 layers
    """

    def __init__(self, **kwargs):
    
        name              = "siamese_inceptionv2_adapt_1_5_betas_nonshared_batch_norm_plda"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v2_adapt_layers_1_5/extractor_nonshared_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm = pkg_resources.resource_filename("bob.bio.htface", "configs/algorithm/plda_short.py")


        self.baseline_type     = "Siamese BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_5.estimator_nonshared_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptLayers1_5_BatchNorm_PLDA, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)




class SiameseAdaptLayers1_5_BetasBatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1-5 layers
      - Adapt betas
    """

    def __init__(self, **kwargs):
    
        name              = "siamese_inceptionv2_adapt_1_5_betas_nonshared_batch_norm"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v2_adapt_layers_1_5/extractor_nonshared_betas_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Siamese BN adapt betas"
        self.reuse_extractor   = False

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_5.estimator_nonshared_betas_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptLayers1_5_BetasBatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)


class TripletAdaptLayers1_5_BatchNorm(Baseline):

    def __init__(self, **kwargs):
    
        name              = "triplet_inceptionv2_layers_1_5_nonshared_batch_norm"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/triplet_transfer_learning/inception_resnet_v2_adapt_layers_1_5/extractor_nonshared_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Triplet BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_layers_1_5.estimator_nonshared_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(TripletAdaptLayers1_5_BatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)


        
class TripletAdaptLayers1_5_BetasBatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - ADAPT ONLY THE BETAS
    """

    def __init__(self, **kwargs):
            
        name              = "triplet_inceptionv2_layers_1_5_betas_nonshared_batch_norm"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/triplet_transfer_learning/inception_resnet_v2_adapt_layers_1_5/extractor_nonshared_betas_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Triplet BN adapt betas"        
        self.reuse_extractor   = False

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_layers_1_5.estimator_nonshared_betas_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")        

        super(TripletAdaptLayers1_5_BetasBatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
        
        
# Entry points
inception_resnet_v2_siamese_adapt_1_5_plda = SiameseAdaptLayers1_5_BatchNorm_PLDA()

inception_resnet_v2_siamese_adapt_1_5 = SiameseAdaptLayers1_5_BatchNorm()
inception_resnet_v2_siamese_adapt_1_5_betas = SiameseAdaptLayers1_5_BetasBatchNorm()

inception_resnet_v2_triplet_adapt_1_5 = TripletAdaptLayers1_5_BatchNorm()
inception_resnet_v2_triplet_adapt_1_5_betas = TripletAdaptLayers1_5_BetasBatchNorm()
