#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Wed 19 Oct 23:43:22 2016

from bob.pad.base.algorithm import Algorithm
import numpy

import os

import logging
logger = logging.getLogger("bob.pad.voice")


class TensorflowEval(Algorithm):
    """This class is for evaluating data stored in tensorflow tfrecord format using a pre-trained LSTM model."""

    def __init__(self,
                 architecture_name="mlp",
                 input_shape=[200, 81],  # [temporal_length, feature_size]
                 network_size=60,  # the output size of LSTM cell
                 normalization_file=None,  # file with normalization parameters from train set
                 **kwargs):
        """Generates a test value that is read and written"""

        # call base class constructor registering that this tool performs everything.
        Algorithm.__init__(
            self,
            performs_projection=True,
            requires_projector_training=False,
            **kwargs
        )

        self.architecture_name = architecture_name
        self.input_shape = input_shape
        self.num_time_steps = input_shape[0]
        self.network_size = network_size
        self.data_std = None

        features_length = input_shape[1]
        if normalization_file and os.path.exists(normalization_file):
            logger.info("Loading normalization file '%s' " % normalization_file)
            npzfile = numpy.load(normalization_file)
            self.data_mean = npzfile['data_mean']
            self.data_std = numpy.array(npzfile['data_std'])
            if not self.data_std.shape:  # if std was saved as scalar
                self.data_std = numpy.ones(features_length)
        else:
            logger.info("Normalization file '%s' does not exist!" % normalization_file)
            self.data_mean = 0
            self.data_std = 1

        self.data_reader = None
        self.session = None
        self.dnn_model = None
        self.data_placeholder = None

    # def simple_lstm_network(self, train_data_shuffler, batch_size=10, lstm_cell_size=64,
    #                         num_time_steps=28, num_classes=10, seed=10, reuse=False):
    #     import tensorflow as tf
    #     from bob.learn.tensorflow.layers import lstm
    #     slim = tf.contrib.slim
    #
    #     if isinstance(train_data_shuffler, tf.Tensor):
    #         inputs = train_data_shuffler
    #     else:
    #         inputs = train_data_shuffler("data", from_queue=False)
    #
    #     initializer = tf.contrib.layers.xavier_initializer(seed=seed)
    #
    #     # Creating an LSTM network
    #     graph = lstm(inputs, lstm_cell_size, num_time_steps=num_time_steps, batch_size=batch_size,
    #                  output_activation_size=num_classes, scope='lstm', name='sync_cell',
    #                  weights_initializer=initializer, activation=tf.nn.sigmoid, reuse=reuse)
    #
    #     # fully connect the LSTM output to the classes
    #     graph = slim.fully_connected(graph, num_classes, activation_fn=None, scope='fc1',
    #                                  weights_initializer=initializer, reuse=reuse)
    #
    #     return graph

    def normalize_data(self, features):
        mean = numpy.mean(features, axis=0)
        std = numpy.std(features, axis=0)
        return numpy.divide(features - mean, std)

    def _check_feature(self, feature):
        """Checks that the features are appropriate."""
        if not isinstance(feature, numpy.ndarray) or feature.ndim != 2 or feature.dtype != numpy.float32:
            raise ValueError("The given feature is not appropriate", feature)
        return True

    def restore_trained_model(self, projector_file):
        import tensorflow as tf

        if self.session is None:
            self.session = tf.Session()
        # add extra dimension to the input, so that 2D convolution would work
        data_pl = tf.placeholder(tf.float32, shape=(None,) + tuple(self.input_shape) + (1,), name="data")

        # create an empty graph of the correct architecture but with needed batch_size==1
        # import ipdb; ipdb.set_trace()
        if self.architecture_name == '3lstm':
            from bob.learn.tensorflow.network import triple_lstm_network
            graph = triple_lstm_network(data_pl, batch_size=1,
                                        lstm_cell_size=self.network_size, num_time_steps=self.num_time_steps,
                                        num_classes=2, reuse=False)
        elif self.architecture_name == '2lstm':
            from bob.learn.tensorflow.network import double_lstm_network
            graph = double_lstm_network(data_pl, batch_size=1,
                                        lstm_cell_size=self.network_size, num_time_steps=self.num_time_steps,
                                        num_classes=2, reuse=False)
        elif self.architecture_name == 'lstm':
            from bob.learn.tensorflow.network import simple_lstm_network
            graph = simple_lstm_network(data_pl, batch_size=1,
                                        lstm_cell_size=self.network_size, num_time_steps=self.num_time_steps,
                                        num_classes=2, reuse=False)
        elif self.architecture_name == 'mlp':
            from bob.learn.tensorflow.network import mlp_network
            graph = mlp_network(data_pl,
                                hidden_layer_size=self.network_size,
                                num_time_steps=self.num_time_steps,
                                num_classes=2, reuse=False)
        elif self.architecture_name == 'simplecnn':
            from bob.learn.tensorflow.network import simple2Dcnn_network
            graph = simple2Dcnn_network(data_pl,
                                        num_classes=2, reuse=False)
        elif self.architecture_name == 'lightcnn':
            from bob.learn.tensorflow.network import LightCNN9
            network = LightCNN9(n_classes=2, device="/cpu:0")
            graph = network(data_pl, reuse=False)
        else:
            return None

        self.session.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        #        saver = tf.train.import_meta_graph(projector_file + ".meta", clear_devices=True)
        saver.restore(self.session, projector_file)
        return tf.nn.softmax(graph, name="softmax"), data_pl
#        return graph, data_pl

    def load_projector(self, projector_file):
        logger.info("Loading pretrained model from {0}".format(projector_file))

        self.dnn_model, self.data_placeholder = self.restore_trained_model(projector_file)

    def project_feature(self, feature):

        logger.info(" .... Projecting %d features vector" % feature.shape[0])
        from bob.learn.tensorflow.datashuffler import DiskAudio
        if not self.data_reader:
            self.data_reader = DiskAudio([0], [0], [1] + self.input_shape)

        # normalize the feature using pre-loaded normalization parameters
        if self.data_std is not None and self.data_std.all() > 0:
            feature = numpy.divide(feature - self.data_mean, self.data_std)

        # split the feature in the sliding window frames
        frames, _ = self.data_reader.split_features_in_windows(features=feature, label=1,
                                                               win_size=self.num_time_steps,
                                                               sliding_step=1)
#        logger.info(" .... And frames of shape {0} are extracted to pass into DNN model".format(frames.shape))
        if frames is None:
            return None

        logger.info(" .... And frames of shape {0} are extracted to pass into DNN model".format(frames.shape))

        projections = numpy.zeros((len(frames), 2), dtype=numpy.float32)
        for i in range(frames.shape[0]):
            frame = frames[i]
            # reshape to 4D shape, so that all networks, including CNN-based
            # would work propery
            frame = numpy.reshape(frame, [1] + self.input_shape + [1])
            #logger.info(" .... projecting frame of shape {0} onto DNN model".format(frame.shape))

            if self.session is not None:
                forward_output = self.session.run(self.dnn_model, feed_dict={self.data_placeholder: frame})
                projections[i] = forward_output[0]
            else:
                raise ValueError("Tensorflow session was not initialized, so cannot project on DNN model!")

        logger.info("Projected scores {0}".format(projections))
        return numpy.asarray(projections, dtype=numpy.float32)

    def project(self, feature):
        """project(feature) -> projected

        This function will project the given feature.
        It is assured that the :py:meth:`load_projector` was called once before the ``project`` function is executed.

        **Parameters:**

        feature : object
          The feature to be projected.

        **Returns:**

        projected : object
          The projected features.
          Must be writable with the :py:meth:`write_feature` function and readable with the :py:meth:`read_feature` function.

        """
        if len(feature) > 0:
            # if we have a set of independent blocks to process
            # collect all projections and flatten them in one output array
            if isinstance(feature, list):
                projections = []
                for feat in feature:
                    feat = numpy.cast['float32'](feat)
                    self._check_feature(feat)
                    projection = self.project_feature(feat)
                    if projection is not None:
                        projections.extend(projection)
                if len(projections) == 0:
                    return None
                return numpy.asarray(projections, dtype=numpy.float32)
            else:
                feature = numpy.cast['float32'](feature)
                self._check_feature(feature)
                return self.project_feature(feature)
        else:
            return numpy.zeros(1, dtype=numpy.float64)

    def score_for_multiple_projections(self, toscore):
        """scorescore_for_multiple_projections(toscore) -> score

        **Returns:**

        score : float
          A score value for the object ``toscore``.
        """
        scores = numpy.asarray(toscore, dtype=numpy.float32)
        real_scores = scores[:, 1]
        logger.debug("Mean score %f", numpy.mean(real_scores))
        return [numpy.mean(real_scores)]

    def score(self, toscore):
        """Returns the evarage value of the probe"""
        logger.debug("score() score %f", toscore)
        # return only real score
        return [toscore[0]]
