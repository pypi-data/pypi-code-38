#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


from bob.bio.base.baseline import Baseline
import pkg_resources

# IMPORTING THE NECESSARY MODULES

# Siamese
import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm
import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_betas_batch_norm

# Triplet
import bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm
import bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_betas_batch_norm

## siamese same modality

#import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm_same_modality

#import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm_random_pairs

#import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm_euclidean_loss

#import bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm_low_level_loss


class SiameseAdaptLayers1_4_BatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1-4 layers
    """

    def __init__(self, **kwargs):
    
        name              = "siamese_inceptionv2_adapt_1_4_nonshared_batch_norm"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v2_adapt_layers_1_4/extractor_nonshared_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Siamese BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptLayers1_4_BatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)


class SiameseAdaptLayers1_4_BetasBatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1-4 layers
      - Adapt betas
    """

    def __init__(self, **kwargs):
    
        name              = "siamese_inceptionv2_adapt_1_4_betas_nonshared_batch_norm"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v2_adapt_layers_1_4/extractor_nonshared_betas_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Siamese BN adapt betas"
        self.reuse_extractor   = False

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_betas_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptLayers1_4_BetasBatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)


class TripletAdaptLayers1_4_BatchNorm(Baseline):

    def __init__(self, **kwargs):
    
        name              = "triplet_inceptionv2_layers_1_4_nonshared_batch_norm"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/triplet_transfer_learning/inception_resnet_v2_adapt_layers_1_4/extractor_nonshared_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Triplet BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(TripletAdaptLayers1_4_BatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)


class SiameseAdaptLayers1_4_BatchNorm_PLDA(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1-5 layers
    """

    def __init__(self, **kwargs):
    
        name              = "siamese_inceptionv2_adapt_1_4_betas_nonshared_batch_norm_plda"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v2_adapt_layers_1_4/extractor_nonshared_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm = pkg_resources.resource_filename("bob.bio.htface", "configs/algorithm/plda_short.py")


        self.baseline_type     = "Siamese BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptLayers1_4_BatchNorm_PLDA, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)



        
class TripletAdaptLayers1_4_BetasBatchNorm(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - ADAPT ONLY THE BETAS
    """

    def __init__(self, **kwargs):
            
        name              = "triplet_inceptionv2_layers_1_4_betas_nonshared_batch_norm"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/triplet_transfer_learning/inception_resnet_v2_adapt_layers_1_4/extractor_nonshared_betas_batch_norm.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Triplet BN adapt betas"        
        self.reuse_extractor   = False

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.triplet_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_betas_batch_norm.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")        

        super(TripletAdaptLayers1_4_BetasBatchNorm, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
        


########## TRAINING SAME MODALITY

class SiameseAdaptLayers1_4_BatchNorm_same_modality(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1-4 layers
    """

    def __init__(self, **kwargs):
    
        name              = "siamese_inceptionv2_adapt_1_4_nonshared_batch_norm_same_modality"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v2_adapt_layers_1_4/extractor_nonshared_batch_norm_same_modality.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Siamese BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm_same_modality.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptLayers1_4_BatchNorm_same_modality, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)


################## RANDOM PAIRS

class SiameseAdaptLayers1_4_BatchNorm_random_pairs(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1-4 layers
    """

    def __init__(self, **kwargs):
    
        name              = "siamese_inceptionv2_adapt_1_4_nonshared_batch_norm_random_pairs"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v2_adapt_layers_1_4/extractor_nonshared_batch_norm_random_pairs.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Siamese BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm_random_pairs.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptLayers1_4_BatchNorm_random_pairs, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)


class SiameseAdaptLayers1_4_BatchNorm_euclidean_loss(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1-4 layers
    """

    def __init__(self, **kwargs):
    
        name              = "siamese_inceptionv2_adapt_1_4_nonshared_batch_norm_euclidean_loss"
        extractor         =  pkg_resources.resource_filename("bob.bio.htface", "configs/domain_specific_units/siamese_transfer_learning/inception_resnet_v2_adapt_layers_1_4/extractor_nonshared_batch_norm_euclidean_loss.py")
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Siamese BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = bob.bio.htface.configs.domain_specific_units.siamese_transfer_learning.inception_resnet_v2_adapt_layers_1_4.estimator_nonshared_batch_norm_euclidean_loss.get_estimator
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(SiameseAdaptLayers1_4_BatchNorm_euclidean_loss, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)



# Entry points
inception_resnet_v2_siamese_adapt_1_4_plda = SiameseAdaptLayers1_4_BatchNorm_PLDA()

inception_resnet_v2_siamese_adapt_1_4 = SiameseAdaptLayers1_4_BatchNorm()
inception_resnet_v2_siamese_adapt_1_4_betas = SiameseAdaptLayers1_4_BetasBatchNorm()

inception_resnet_v2_triplet_adapt_1_4 = TripletAdaptLayers1_4_BatchNorm()
inception_resnet_v2_triplet_adapt_1_4_betas = TripletAdaptLayers1_4_BetasBatchNorm()




#inception_resnet_v2_siamese_adapt_1_4_same_modality = SiameseAdaptLayers1_4_BatchNorm_same_modality()
#inception_resnet_v2_siamese_adapt_1_4_random_pairs = SiameseAdaptLayers1_4_BatchNorm_random_pairs()
#inception_resnet_v2_siamese_adapt_1_4_euclidean_loss = SiameseAdaptLayers1_4_BatchNorm_euclidean_loss()


