""" Model """
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import tensorflow as tf

from tfmodelserver.utils import dict_map, dict_filter


class Model:
    def __init__(self, name, export_dir, version, allow_growth=False):
        self._name = name
        # TODO: Load the latest model
        self._model_dir = os.path.join(export_dir, version)
        self._allow_growth = allow_growth

        self._inputs = self._outputs = None
        self._sess = None

    @property
    def name(self):
        return self._name

    @property
    def allow_growth(self):
        return self._allow_growth

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def session(self):
        return self._sess

    @property
    def model_dir(self):
        return self._model_dir

    def load(self):
        tf.logging.debug('Starting Session...')
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = self.allow_growth
        graph = tf.Graph()
        self._sess = tf.Session(config=config, graph=graph)

        # Load a SavedModel
        tf.logging.debug('Loading SavedModel...')
        meta_graph_def = tf.saved_model.loader.load(self._sess, [tf.saved_model.tag_constants.SERVING], self.model_dir)

        # Get default SignatureDef
        default_signature = meta_graph_def.signature_def[
            tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY]
        tf.logging.info('SignatureDef: {}'.format(default_signature))

        # Get input placeholders from SignatureDef
        inputs = default_signature.inputs

        # Get output tensors from SignatureDef
        outputs = default_signature.outputs

        def get_tensor_from_tensor_info(tensor_info_dict):
            return dict_map(lambda k, v: (k, tf.saved_model.utils.get_tensor_from_tensor_info(v, graph=graph)),
                            tensor_info_dict)

        self._inputs = get_tensor_from_tensor_info(inputs)
        self._outputs = get_tensor_from_tensor_info(outputs)

    def eval(self, input_value, output_names=None):
        outputs = dict_filter(lambda k, _: k in output_names,
                              self.outputs) if output_names is not None else self.outputs

        feed_dict = dict_map(lambda k, v: (self.inputs[k], v), input_value)

        return self.session.run(outputs, feed_dict=feed_dict)
