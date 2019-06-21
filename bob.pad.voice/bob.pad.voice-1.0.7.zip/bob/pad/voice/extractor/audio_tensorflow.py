#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

"""Features for face recognition"""

import numpy
# import bob.io.base
from bob.bio.base.extractor import Extractor

# import bob.io.base
# import bob.ip.base

import logging

logger = logging.getLogger("bob.pad.voice")

class AudioTFExtractor(Extractor):
    """

    **Parameters:**

    feature_layer: The layer to be used as features. Possible values are `fc1` or 'fc2'.

    """

    def __init__(
            self,
            feature_layer="fc1",
            **kwargs
    ):

        Extractor.__init__(self, requires_training=False,
                           split_training_data_by_client=False,
                           skip_extractor_training=True, **kwargs)

        # block parameters        
        # import tensorflow as tf
        # self.session = tf.Session()

        # self.session = Session.instance().session
        self.feature_layer = feature_layer

        self.data_reader = None

        self.dnn_model = None

    def __call__(self, input_data):
        """
        """
        # create empty labels array, since this what read/write function of Base accepts
        rate = input_data[0]
        wav_sample = input_data[1]

        from bob.learn.tensorflow.datashuffler import DiskAudio
        if not self.data_reader:
            self.data_reader = DiskAudio([0], [0])

        logger.debug(" .... Extracting frames on the fly from %d length sample" % wav_sample.shape[0])
        frames, labels = self.data_reader.extract_frames_from_wav(wav_sample, 0)
        frames = numpy.asarray(frames)
        logger.debug(" .... And %d frames are extracted to pass into DNN model" % frames.shape[0])
        frames = numpy.reshape(frames, (frames.shape[0], -1, 1))

        projection_on_dnn = self.dnn_model(frames, self.feature_layer)
        return numpy.asarray(projection_on_dnn, dtype=numpy.float64)

    # re-define the train function to get it non-documented
    def train(*args, **kwargs): raise NotImplementedError("This function is not implemented and should not be called.")

    def load(self, extractor_file):
        logger.info("Loading pretrained model from {0}".format(extractor_file))
        from bob.learn.tensorflow.network import SequenceNetwork
        self.dnn_model = SequenceNetwork(default_feature_layer=self.feature_layer)
        # self.dnn_model.load_hdf5(bob.io.base.HDF5File(extractor_file), shape=[1, 6560, 1])
        self.dnn_model.load(extractor_file, clear_devices=True)

        #hdf5 = bob.io.base.HDF5File(extractor_file)
        #self.lenet.load(hdf5, shape=(1,125,125,3), session=self.session)


audiotf = AudioTFExtractor()
