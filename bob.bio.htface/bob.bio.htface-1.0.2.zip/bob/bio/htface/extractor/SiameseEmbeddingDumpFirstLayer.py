import numpy
from bob.bio.base.extractor import Extractor
import bob.io.image
import tensorflow as tf
import os

class SiameseEmbeddingDumpFirstLayer(Extractor):


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
        prelogits_left, endpoints_left = graph_function(tf.stack([tf.image.per_image_standardization(i) for i in tf.unstack(self.input_left)]),
                                                    mode=tf.estimator.ModeKeys.PREDICT, is_left=True, is_siamese=False)

        prelogits_right, endpoints_right = graph_function(tf.stack([tf.image.per_image_standardization(i) for i in tf.unstack(self.input_right)]),
                                           mode=tf.estimator.ModeKeys.PREDICT, is_left=False, reuse=True, is_siamese=False)

        #self.embedding_left = tf.nn.l2_normalize(endpoints_left["Conv2d_1a_3x3_left"], dim=1, name="embedding")
        #self.embedding_right = tf.nn.l2_normalize(endpoints_right["Conv2d_1a_3x3_right"], dim=1, name="embedding")

        #self.embedding_left = tf.nn.l2_normalize(endpoints_left["Conv2d_3b_1x1_left"], dim=1, name="embedding")
        #self.embedding_right = tf.nn.l2_normalize(endpoints_right["Conv2d_3b_1x1_right"], dim=1, name="embedding")


        #self.embedding_left = tf.nn.l2_normalize(endpoints_left["Conv2d_4a_3x3_left"], dim=1, name="embedding")
        #self.embedding_right = tf.nn.l2_normalize(endpoints_right["Conv2d_4a_3x3_right"], dim=1, name="embedding")

        self.embedding_left = tf.nn.l2_normalize(endpoints_left["Conv2d_4a_3x3_anchor"], dim=1, name="embedding")
        self.embedding_right = tf.nn.l2_normalize(endpoints_right["Conv2d_4a_3x3_positive-negative"], dim=1, name="embedding")


        #self.embedding_left = tf.nn.l2_normalize(endpoints_left["Mixed_5b_left"], dim=1, name="embedding")
        #self.embedding_right = tf.nn.l2_normalize(endpoints_right["Mixed_5b_right"], dim=1, name="embedding")

        #import ipdb; ipdb.set_trace()
        #self.embedding_left = tf.nn.l2_normalize(endpoints_left["Mixed_6a"], dim=1, name="embedding")
        #self.embedding_right = tf.nn.l2_normalize(endpoints_right["Mixed_6a"], dim=1, name="embedding")

        #self.embedding_left = tf.nn.l2_normalize(endpoints_left["Mixed_7a"], dim=1, name="embedding")
        #self.embedding_right = tf.nn.l2_normalize(endpoints_right["Mixed_7a"], dim=1, name="embedding")

        #self.embedding_left = tf.nn.l2_normalize(endpoints_left["Conv2d_7b_1x1"], dim=1, name="embedding")
        #self.embedding_right = tf.nn.l2_normalize(endpoints_right["Conv2d_7b_1x1"], dim=1, name="embedding")

        #self.embedding_left = tf.nn.l2_normalize(endpoints_left["PreLogitsFlatten"], dim=1, name="embedding")
        #self.embedding_right = tf.nn.l2_normalize(endpoints_right["PreLogitsFlatten"], dim=1, name="embedding")


        #self.embedding_left = tf.nn.l2_normalize(prelogits_left, dim=1, name="embedding")
        #self.embedding_right = tf.nn.l2_normalize(prelogits_right, dim=1, name="embedding")


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

        # Returning the embidding according to the modality
        #import ipdb; ipdb.set_trace()
        if metadata.db.modalities[0] == metadata.modality:
            return features_left[0]
        else:
            return features_right[0]


    # re-define the train function to get it non-documented
    def train(*args, **kwargs): raise NotImplementedError("This function is not implemented and should not be called.")

    def load(*args, **kwargs): pass
