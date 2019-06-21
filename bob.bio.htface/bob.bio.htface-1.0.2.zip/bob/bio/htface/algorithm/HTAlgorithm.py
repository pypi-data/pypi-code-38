#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


from bob.bio.base.algorithm import Algorithm


class HTAlgorithm(Algorithm):
    """
    This is the base class for Heterogeneous face recognition algorithms
    """

    def __init__(
      self,
      performs_projection = False, # enable if your tool will project the features
      requires_projector_training = True, # by default, the projector needs training, if projection is enabled
      split_training_features_by_client = False, # enable if your projector training needs the training files sorted by client
      split_training_features_by_modality = False, # enable if your projector training needs the training files sorted by modality      
      use_projected_features_for_enrollment = True, # by default, the enroller used projected features for enrollment, if projection is enabled.
      requires_enroller_training = False, # enable if your enroller needs training
      **kwargs                            # parameters from the derived class that should be reported in the __str__() function    
    ):
        
        Algorithm.__init__(self,
            performs_projection=performs_projection,
            requires_projector_training=requires_projector_training,
            split_training_features_by_client=split_training_features_by_client,
            use_projected_features_for_enrollment=use_projected_features_for_enrollment,
            requires_enroller_training=requires_enroller_training,
            **kwargs)

        self.split_training_features_by_modality=split_training_features_by_modality

