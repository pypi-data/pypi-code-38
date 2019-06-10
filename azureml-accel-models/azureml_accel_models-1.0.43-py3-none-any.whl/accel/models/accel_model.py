# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module with abstract base class of HW accelerated models."""
import os
import copy
import tempfile
import zipfile
from abc import abstractmethod
from azureml.accel.models.doesnotexisterror import DoesNotExistError
import warnings
import requests

try:
    from abc import ABCMeta

    ABC = ABCMeta('ABC', (), {})
except ImportError:
    from abc import ABC

try:
    import tensorflow as tf
except ImportError:
    warnings.warn("azureml-accel-models requires tensorflow version >= 1.6, please install it")


class AccelModel(ABC):
    """Abstract base class for accel models.

    Accelerated models are neural networks that can be
    accelerated using dedicated hardware.
    """

    _prefix = ""

    # note: these are defaults *only* - can be overriden by model
    _metagraph_input_list = ['InputImage:0']
    _input_tensor_list = copy.copy(_metagraph_input_list)
    _output_tensor_list = ["brainwave_target_node_1_Version_0.1:0"]

    def __init__(self, model_base_path, model_folder_name, version, check_point_uri, save_name,
                 is_frozen=False, weight_path=None):
        """Abstract base class for anaccel model.

        To add a new model, implement a subclass - model folder_name, version, checkpoint_uri and save_name
        should all be given by the user. Weight path and is frozen should be exposed at least for quantized versions.
        :param model_base_path: The base path to store all models in. Generally given by the user.
        :param model_folder_name: The path on disk to store all versions of this model.
        :param version: The version of this model.
        :param check_point_uri: The URI where the model is downloaded from if they don't have it on disk.
        :param save_name: The name the checkpoint is saved under, used to load metagraph.
        :param is_frozen: If the model should be frozen when it is loaded. This freezes the graph by removing the
        variables from tf.GraphKeys.TRAINABLE_VARIABLES.
        :param weight_path: A custom path to load weights from, instead of the default path on disk. Used in retraining
        scenarios.
        """
        self._model_folder_name = model_folder_name
        self.version = version
        self.__check_point_uri = check_point_uri
        self._save_name = save_name
        self.__model_dir = os.path.join(model_base_path, self._model_folder_name, self.version)
        self.__metagraph_location = os.path.join(self.__model_dir, '{0}_bw.meta'.format(self._save_name))
        self.__download_if_not_present()
        if weight_path is None:
            self.__checkpoint_directory = self.__model_dir
        else:
            self.__checkpoint_directory = weight_path
        self.is_frozen = is_frozen
        self.__saver = None

    def __download_if_not_present(self):
        if not os.path.exists(self.__metagraph_location):
            if not os.path.exists(self.__model_dir):
                os.makedirs(self.__model_dir)
            r = requests.get(self.__check_point_uri)
            model_zip_path = os.path.join(self.__model_dir, 'model.zip')
            with open(model_zip_path, 'wb') as output:
                output.write(r.content)
            zip_ref = zipfile.ZipFile(model_zip_path, 'r')
            zip_ref.extractall(self.__model_dir)
            zip_ref.close()
            os.remove(model_zip_path)

    def import_graph_def(self, input_tensor=None, is_training=True):
        """Import the graph definition corresponding to this model.

        Imports accelerated model into currently active graph.

        :param input_tensor: Replace input tensor to accelerated model (must match expected shape and dtype)
        :param is_training: Boolean indicating if the imported graph is intending for training.
        :return: Either single output tensor or list of output tensors (if more than one).
        """
        graph = tf.get_default_graph()

        input_map = {}
        input_map["is_training"] = tf.placeholder_with_default(is_training, (), "is_training")

        # warning: This assumes accelerated model has single input tensor
        if input_tensor is not None:
            input_map[self._metagraph_input_list[0]] = input_tensor

        # update input tensor names to match relabeling
        # note: require revised input tensor's name for extracting the graph.
        for old_name in input_map:
            for i, existing_name in enumerate(self._input_tensor_list):
                if old_name == existing_name:
                    self._input_tensor_list[i] = input_map[old_name].name.split(':')[0]

        self.__saver = tf.train.import_meta_graph(self.__metagraph_location, input_map=input_map)

        if self.is_frozen:
            vars_to_remove = set(graph.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, self._prefix))
            vars = graph.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
            graph.clear_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
            for variable in vars:
                if variable not in vars_to_remove:
                    graph.add_to_collection(tf.GraphKeys.TRAINABLE_VARIABLES, vars)

        # return tensors in order specified in model-specific class
        return_tensors = []
        for fetch in self._output_tensor_list:
            return_tensors.append(tf.get_default_graph().get_tensor_by_name(fetch))

        # don't break backwards compatibility
        if len(return_tensors) == 1:
            return return_tensors[0]

        return return_tensors

    def restore_weights(self, session):
        """Restore the weights of the model into the specific session.

        :param session: The session to load the weights into.
        :type session: tf.Session
        """
        self.__saver.restore(session, tf.train.latest_checkpoint(self.__checkpoint_directory))

    def save_weights(self, path, session=None):
        """Save the weights of the model from a specific session into a specific path.

        :param path: Path of the checkpoint to save the weights into.
        :param session: Session to save weights from.
        :type session: tf.Session
        """
        if session is None:
            session = tf.get_default_session()
        self.__saver.save(session, path, write_meta_graph=False)

    # Apparently compiler needs a checkpoint with only this part.
    def _write_only_this_checkpoint(self, path, session):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.save_weights(tmpdir, session)
            with tf.Session(graph=tf.Graph()) as sess:
                self.import_graph_def(is_training=False)
                self.restore_weights(sess)
                saver = tf.train.Saver()
                saver.save(sess, path)

    @property
    def model_ref(self):
        """
        Name that refers to the model - used for writing the model_def.

        :return:
        """
        return self._save_name

    @property
    def model_version(self):
        """Model Version.

        :return:
        """
        return self.version

    @property
    def model_path(self):
        """
        Path to directory that contains the model.

        :return:
        """
        return self.__model_dir

    @abstractmethod
    def get_input_dims(self, index=0):
        """Get nth model input tensor dimensions."""
        raise NotImplementedError("Base class doesn't implement this")

    @abstractmethod
    def get_output_dims(self, index=0):
        """Get nth model output tensor dimensions."""
        raise NotImplementedError("Base class doesn't implement this")

    @property
    def input_tensor_list(self):
        """List of names of the input tensors of this model.

        :return:
        """
        return self._input_tensor_list

    @property
    def output_tensor_list(self):
        """List of names of the output tensors of this model.

        :return:
        """
        return self._output_tensor_list

    def _input_op_list(self):
        input_ops = set()
        for name in self.input_tensor_list():
            input_ops.add(name.split(':')[0])
        return list(input_ops)

    def _output_op_list(self):
        output_ops = set()
        for name in self.output_tensor_list():
            output_ops.add(name.split(':')[0])
        return list(output_ops)

    def _write_to_tempdir(self, sess, path):
        model_path = path + "/{0}".format(self._save_name)
        if self.is_frozen:
            tf.train.latest_checkpoint(self.__checkpoint_directory)
            with tf.Session(graph=tf.Graph()) as sess:
                sav = tf.train.import_meta_graph(self.__metagraph_location)
                sav.restore(sess, tf.train.latest_checkpoint(self.__checkpoint_directory))
                sav.save(sess, model_path)
        else:
            self._write_only_this_checkpoint(model_path, sess)

    @classmethod
    def _download_classifier(cls, model_dir):
        if not hasattr(cls, 'classifier_uri'):
            raise DoesNotExistError('This model does not have classifier')

        rndir = os.path.join(model_dir, cls._modelname, cls._modelver)
        _classifier_location = os.path.join(rndir, "{}_classifier.pb".format(cls._save_name))
        if not os.path.exists(_classifier_location):
            if not os.path.exists(rndir):
                os.makedirs(rndir)
            r = requests.get(cls.classifier_uri)
            with open(_classifier_location, 'wb') as output:
                output.write(r.content)
        return _classifier_location

    def get_default_classifier(self, input_tensor, prefix='classifier'):
        """Import a frozen, default Imagenet classifier for the model into the current graph.

        :param prefix: namespace to load classifier into.
        :param input_tensor: The input feature tensor for the classifier. Expected to be [?, 2048]
        :param model_dir: The directory to download the classifier into. Used as a cache locally.
        :return:
        """
        _classifier_location = self._download_classifier(self.__model_dir)

        input_map = {self.classifier_input: input_tensor}
        input_graph_def = tf.GraphDef()
        with tf.gfile.Open(_classifier_location, "rb") as f:
            data = f.read()

            input_graph_def.ParseFromString(data)

        tensors = tf.import_graph_def(input_graph_def, name=prefix, input_map=input_map,
                                      return_elements=[self.classifier_output])
        return tensors[0]
