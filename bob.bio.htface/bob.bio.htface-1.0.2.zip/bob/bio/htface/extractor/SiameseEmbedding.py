import numpy
from bob.bio.base.extractor import Extractor
import bob.io.image
import tensorflow as tf
import os

class SiameseEmbedding(Extractor):


    def __init__(self, checkpoint_filename, graph_function, shape=(1, 160, 160, 1)):
        """Loads the tensorflow model

        Parameters
        ----------
        checkpoint_filename: str
            Path of your checkpoint. If the .meta file is providede the last checkpoint will be loaded.

        graph_function :
                        
        """
        Extractor.__init__(self, skip_extractor_training=True)

        # Building the graph
        self.input_left = tf.placeholder(tf.float32, shape=shape, name="left")
        self.input_right = tf.placeholder(tf.float32, shape=shape, name="right")

        # Taking the embedding
        prelogits_left,_ = graph_function(tf.stack([tf.image.per_image_standardization(i) for i in tf.unstack(self.input_left)]),
                                                    mode=tf.estimator.ModeKeys.PREDICT, is_left=True)

        prelogits_right,_ = graph_function(tf.stack([tf.image.per_image_standardization(i) for i in tf.unstack(self.input_right)]),
                                           mode=tf.estimator.ModeKeys.PREDICT, is_left=False, reuse=True)

        self.embedding_left = tf.nn.l2_normalize(prelogits_left, dim=1, name="embedding")
        self.embedding_right = tf.nn.l2_normalize(prelogits_right, dim=1, name="embedding")


        # Initializing the variables of the current graph
        self.session = tf.Session()
        #from tensorflow.python import debug as tf_debug
        #self.session = tf_debug.LocalCLIDebugWrapperSession(self.session)
        self.session.run(tf.global_variables_initializer())
                
        # Loading the last checkpoint and overwriting the current variables
        saver = tf.train.Saver()

        if os.path.isdir(checkpoint_filename):
            saver.restore(self.session, tf.train.latest_checkpoint(checkpoint_filename))
        else:
            saver.restore(self.session, checkpoint_filename)


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

        if image.ndim>2:
            image = bob.io.image.to_matplotlib(image)
            image = numpy.reshape(image, tuple([1] + list(image.shape)) )
            image = image.astype("float32")            
        else:
            image = numpy.reshape(image, tuple([1] + list(image.shape) + [1]) )
        

        features_left, features_right = self.session.run([self.embedding_left, self.embedding_right], 
                                        feed_dict={self.input_left: image, self.input_right:image})

        #import ipdb; ipdb.set_trace()
        # Returning the embidding according to the modality
        if metadata.db.modalities[0] == metadata.modality:
            return features_left
        else:
            return features_right


    # re-define the train function to get it non-documented
    def train(*args, **kwargs): raise NotImplementedError("This function is not implemented and should not be called.")

    def load(*args, **kwargs): pass
