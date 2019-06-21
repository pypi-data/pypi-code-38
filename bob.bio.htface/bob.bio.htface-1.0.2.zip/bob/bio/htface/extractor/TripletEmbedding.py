import numpy
from bob.bio.base.extractor import Extractor
import bob.io.image
import tensorflow as tf
import os

class TripletEmbedding(Extractor):


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
        self.input_anchor = tf.placeholder(tf.float32, shape=shape, name="anchor")
        self.input_positive = tf.placeholder(tf.float32, shape=shape, name="positive")
        self.input_negative = tf.placeholder(tf.float32, shape=shape, name="negative")

        # Taking the embedding
        prelogits_anchor,_ = graph_function(tf.stack([tf.image.per_image_standardization(i) for i in tf.unstack(self.input_anchor)]),
                                                      mode=tf.estimator.ModeKeys.PREDICT, is_left=True, is_siamese=False)

        prelogits_positive,_ = graph_function(tf.stack([tf.image.per_image_standardization(i) for i in tf.unstack(self.input_positive)]),
                                              mode=tf.estimator.ModeKeys.PREDICT, is_left=False, reuse=True, is_siamese=False)

        prelogits_negative,_ = graph_function(tf.stack([tf.image.per_image_standardization(i) for i in tf.unstack(self.input_negative)]),
                                              mode=tf.estimator.ModeKeys.PREDICT, is_left=False, reuse=True, is_siamese=False)


        self.embedding_anchor = tf.nn.l2_normalize(prelogits_anchor, dim=1, name="embedding_anchor")
        self.embedding_positive = tf.nn.l2_normalize(prelogits_positive, dim=1, name="embedding_positive")
        self.embedding_negative = tf.nn.l2_normalize(prelogits_negative, dim=1, name="embedding_negative")        


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
        

        features_anchor, features_positive,_ = self.session.run([self.embedding_anchor, self.embedding_positive, self.embedding_negative ], 
                                               feed_dict={self.input_anchor: image, self.input_positive:image, self.input_negative:image})

        # Returning the embidding according to the modality
        if metadata.db.modalities[0] == metadata.modality:
            return features_anchor
        else:
            return features_positive


    # re-define the train function to get it non-documented
    def train(*args, **kwargs): raise NotImplementedError("This function is not implemented and should not be called.")

    def load(*args, **kwargs): pass
