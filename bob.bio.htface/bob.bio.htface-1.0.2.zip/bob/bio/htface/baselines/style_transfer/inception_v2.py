#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


from bob.bio.base.baseline import Baseline
import pkg_resources

# IMPORTING THE NECESSARY MODULES

# Siamese

class StyleTransfer(Baseline):
    """
    This baseline has the following features:
      - The prior uses batch norm in all layers
      - Siamese net
      - Adapt the 1-4 layers
    """

    def __init__(self, **kwargs):
    
        name              = "style_transfer_inceptionv2"
        extractor       = pkg_resources.resource_filename("bob.bio.htface", "configs/extractor/style_transfer.py")
        
        preprocessors   = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm         = "distance-cosine"

        self.baseline_type     = "Siamese BN"
        self.reuse_extractor   = False        

        # train cnn
        self.estimator         = None
        self.preprocessed_data = pkg_resources.resource_filename("bob.bio.htface", "configs/tensorflow/siamese_transfer_learning/inception_resnet_v2_databases/")

        super(StyleTransfer, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)



# Entry points
style_transfer_inception_v2 = StyleTransfer()



