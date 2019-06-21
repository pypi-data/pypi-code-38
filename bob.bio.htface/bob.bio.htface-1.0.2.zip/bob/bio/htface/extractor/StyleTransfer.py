import numpy
from bob.bio.base.extractor import Extractor
import bob.io.image
import os
from bob.learn.tensorflow.style_transfer import do_style_transfer
import tensorflow as tf
import copy

class StyleTransfer(Extractor):


    def __init__(self, style_images, 
                       architecture, checkpoint_dir, scopes,
                       content_end_points, style_end_points,
                       preprocess_fn=None, un_preprocess_fn=None, pure_noise=False,
                       iterations=1000, learning_rate=0.1,
                       content_weight=5., style_weight=500., denoise_weight=500.):
        """
        Apply style transfer

        Parameters
        ----------
        checkpoint_filename: str
            Path of your checkpoint. If the .meta file is providede the last checkpoint will be loaded.

        graph_function :
                        
        """
        Extractor.__init__(self, skip_extractor_training=True)

        self.style_images = style_images
        self.architecture = architecture
        self.checkpoint_dir = checkpoint_dir 
        self.scopes = scopes
        self.content_end_points = content_end_points
        self.style_end_points = style_end_points

        self.preprocess_fn = preprocess_fn
        self.un_preprocess_fn = un_preprocess_fn
        self.pure_noise = pure_noise
        self.iterations = iterations
        self.learning_rate = learning_rate
        self.content_weight = content_weight
        self.style_weight = style_weight
        self.denoise_weight = denoise_weight


    def __call__(self, image, metadata=None):
        """__call__(image) -> feature

        Extract features

        **Parameters:**

        image : 3D :py:class:`numpy.ndarray` (floats)
          The image to extract the features from.

        **Returns:**

        feature : 2D :py:class:`numpy.ndarray` (floats)
          The extracted features
        """
        tf.reset_default_graph()
        output = do_style_transfer(image, copy.deepcopy(self.style_images),
                                   self.architecture, self.checkpoint_dir, self.scopes,
                                   self.content_end_points, self.style_end_points,
                                   self.preprocess_fn, self.un_preprocess_fn,
                                   self.pure_noise,
                                   self.iterations, self.learning_rate,
                                   self.content_weight, self.style_weight,
                                   self.denoise_weight)
        tf.reset_default_graph()
        
        return output.flatten()

    # re-define the train function to get it non-documented
    def train(*args, **kwargs): raise NotImplementedError("This function is not implemented and should not be called.")

    def load(*args, **kwargs): pass
