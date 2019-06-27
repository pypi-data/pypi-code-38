"""
    See the guides: `Dataset <./Dataset.html>`_
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
from enum import Enum

from tflibs.utils import map_dict
from tflibs import image as tfimage


class FeatureSpec:
    """A class for specifying feature specs of a `tflibs.datasets.BaseDataset <./Dataset.html>`_.
    """

    @staticmethod
    def _int64_feature(values):
        """
        Returns a TF-Feature of int64s.

        :param int or list values: A int values.
        :return: A TF-Feature proto.
        :rtype: tf.train.Feature
        """
        if not isinstance(values, (tuple, list)):
            values = [values]
        return tf.train.Feature(int64_list=tf.train.Int64List(value=values))

    @staticmethod
    def _bytes_feature(values):
        """
        Returns a TF-Feature of bytes.

        :param str values: A string.
        :return: A TF-Feature proto.
        :rtype: tf.train.Feature
        """
        if not isinstance(values, bytes):
            values = bytes(values, 'utf-8')

        return tf.train.Feature(bytes_list=tf.train.BytesList(value=[values]))

    @staticmethod
    def _float_feature(values):
        """
        Returns a TF-Feature of floats.

        :param float or list values: A scalar of list of values.
        :return: A TF-Feature proto.
        :rtype: tf.train.Feature
        """
        if not isinstance(values, (tuple, list)):
            values = [values]
        return tf.train.Feature(float_list=tf.train.FloatList(value=values))

    def __init__(self, shape):
        self._shape = shape

    @property
    def shape(self):
        return self._shape

    @property
    def feature_proto_spec(self):
        """
        A property for specifying inner encoding spec of the feature

        :return: The dict containing shape and dtype info
        :rtype: dict
        """
        raise NotImplementedError

    def feature_proto(self, value_dict):
        """
        Returns a dict of `tf.train.Feature` proto corresponding to `feature_proto_spec`

        :param dict value_dict: A dict containing values of `feature_proto_spec`
        :return: A dict of `tf.train.Feature`
        :rtype: dict
        """

        def map_fn(k, v):
            dtype = v['dtype']
            value = value_dict[k]

            if isinstance(value, np.ndarray):
                value = value.tolist()

            if dtype == tf.string:
                return k, FeatureSpec._bytes_feature(value)
            elif dtype == tf.float16 or dtype == tf.float32 or dtype == tf.float64:
                return k, FeatureSpec._float_feature(value)
            elif dtype == tf.int8 or dtype == tf.int16 or dtype == tf.int32 or dtype == tf.int64:
                return k, FeatureSpec._int64_feature(value)

        return map_dict(map_fn, self.feature_proto_spec)

    def parse(self, parent_key, record):
        """
        Parse TF-record and returns dict of `tf.Tensor`

        :param str parent_key: The key of the feature
        :param tf.Tensor record: String tensor of TF-record
        :return: A dict of tensors as specified at `feature_proto_spec`
        :rtype: dict
        """

        def parse(k, v):
            return '{}/{}'.format(parent_key, k), tf.FixedLenFeature(v['shape'], v['dtype'])

        features = map_dict(parse, self.feature_proto_spec)
        return tf.parse_single_example(record, features)


class ScalarSpec(FeatureSpec):
    def __init__(self, dtype):
        super(ScalarSpec, self).__init__(())
        self._dtype = dtype

    @property
    def tfdtype(self):
        return self._dtype

    @property
    def pydtype(self):
        tfdtype = self._dtype  # type: tf.DType

        if tfdtype.is_integer:
            return int
        elif tfdtype.is_floating:
            return float
        elif tfdtype == tf.string:
            return str
        else:
            raise ValueError('Invalid dtype')

    @property
    def feature_proto_spec(self):
        return {
            'value': {
                'shape': (),
                'dtype': self.tfdtype,
            }
        }

    def create_with_value(self, value):
        if not isinstance(value, self.pydtype):
            value = self.pydtype(value)

        return {
            'value': value
        }


class IDSpec(FeatureSpec):
    """A class for specifying unique ID.
    """

    def __init__(self):
        super(IDSpec, self).__init__(())

    @property
    def feature_proto_spec(self):
        """
        A property for specifying inner encoding spec of the feature

        :return: The dict containing shape and dtype info
        :rtype: dict
        """
        return {
            '_id': {
                'shape': (),
                'dtype': tf.string,
            }
        }

    def parse(self, parent_key, record):
        """
        Parse TF-record and returns `tf.Tensor`

        :param str parent_key: The key of the feature
        :param tf.Tensor record: String tensor of TF-record
        :return: A scalar tensor containing an id
        :rtype: tf.Tensor
        """
        parsed = FeatureSpec.parse(self, parent_key, record)

        return parsed['{}/_id'.format(parent_key)]

    def create_with_string(self, string):
        return {
            '_id': string
        }


class ImageSpec(FeatureSpec):
    """
    A class for specifying image spec

    :param list|tuple image_size: The sizes of images
    """

    def __init__(self, image_size):
        image_size = list(image_size)
        super(ImageSpec, self).__init__(image_size)

    @property
    def feature_proto_spec(self):
        """
        A property for specifying inner encoding spec of the feature

        :return: The dict containing shape and dtype info
        :rtype: dict
        """
        return {
            'encoded': {
                'shape': (),
                'dtype': tf.string,
            }
        }

    def parse(self, parent_key, record):
        """
        Parse TF-record and returns `tf.Tensor`

        :param str parent_key: The key of the feature
        :param tf.Tensor record: String tensor of TF-record
        :return: A 3-D tensor containing an image
        :rtype: tf.Tensor
        """
        parsed = FeatureSpec.parse(self, parent_key, record)
        decoded = tf.image.decode_image(parsed['{}/{}'.format(parent_key, 'encoded')], channels=self.shape[-1])
        decoded = tf.reshape(decoded, self.shape)

        return decoded

    def create_with_path(self, path):
        # TODO: Assert shape
        with open(path, 'rb') as f:
            return {
                'encoded': f.read()
            }

    def create_with_tensor(self, tensor):
        # TODO: Assert shape
        return {
            'encoded': tfimage.encode(tensor)
        }

    def create_with_contents(self, contents):
        # TODO: Assert shape

        return {
            'encoded': contents
        }


class VarImageSpec(FeatureSpec):
    """
    A class for specifying image spec

    :param list|tuple image_size: The sizes of images
    """

    def __init__(self, channels):
        super(VarImageSpec, self).__init__(())
        self._channels = channels

    @property
    def feature_proto_spec(self):
        """
        A property for specifying inner encoding spec of the feature

        :return: The dict containing shape and dtype info
        :rtype: dict
        """
        return {
            'encoded': {
                'shape': (),
                'dtype': tf.string,
            }
        }

    @property
    def channels(self):
        return self._channels

    def parse(self, parent_key, record):
        """
        Parse TF-record and returns `tf.Tensor`

        :param str parent_key: The key of the feature
        :param tf.Tensor record: String tensor of TF-record
        :return: A 3-D tensor containing an image
        :rtype: tf.Tensor
        """
        parsed = FeatureSpec.parse(self, parent_key, record)
        decoded = tf.image.decode_image(parsed['{}/{}'.format(parent_key, 'encoded')], channels=self.channels)
        decoded.set_shape((None, None, self.channels))

        return decoded

    def create_with_path(self, path):
        # TODO: Assert shape
        with open(path, 'rb') as f:
            return {
                'encoded': f.read()
            }

    def create_with_tensor(self, tensor):
        # TODO: Assert shape
        return {
            'encoded': tfimage.encode(tensor)
        }

    def create_with_contents(self, contents):
        # TODO: Assert shape

        return {
            'encoded': contents
        }


class LabelSpec(FeatureSpec):
    """
    A class for specifying one-hot label spec

    :param int depth: The number of labels
    :param list class_names: A list of `str` which describes each labels
    """

    def __init__(self, depth, class_names=None):
        super(LabelSpec, self).__init__([depth])
        self._class_names = class_names

    @property
    def feature_proto_spec(self):
        """
        A property for specifying inner encoding spec of the feature

        :return: The dict containing shape and dtype info
        :rtype: dict
        """
        return {
            'index': {
                'shape': (),
                'dtype': tf.int64
            }
        }

    def parse(self, parent_key, record):
        """
        Parse TF-record and returns `tf.Tensor`

        :param str parent_key: The key of the feature
        :param tf.Tensor record: String tensor of TF-record
        :return: An 1-D tensor containing label
        :rtype: tf.Tensor
        """
        parsed = FeatureSpec.parse(self, parent_key, record)

        return tf.one_hot(parsed['{}/{}'.format(parent_key, 'index')], self.shape[0])

    def create_with_index(self, index):
        assert index < self.shape[0]

        return {
            'index': index
        }

    def create_with_label(self, label):
        # TODO: Assert bad labels don't exist
        return {
            'index': self._class_names.index(label)
        }

    @classmethod
    def from_class_names(cls, class_names):
        """
        Create `LabelSpec` object from a list of names specifying each classes

        :param list class_names: A list of names specifying each classes
        :return: `LabelSpec` object
        :rtype: LabelSpec
        """
        obj = cls(len(class_names), class_names)

        return obj


class MultiLabelSpec(FeatureSpec):
    """
    A class for specifying multi-label spec

    :param int depth: The number of labels
    :param list class_names: A list of `str` which describes each labels
    """

    def __init__(self, depth, class_names=None):
        super(MultiLabelSpec, self).__init__([depth])
        self._class_names = class_names

    @property
    def feature_proto_spec(self):
        """
        A property for specifying inner encoding spec of the feature

        :return: The dict containing shape and dtype info
        :rtype: dict
        """
        return {
            'tensor': {
                'shape': self.shape,
                'dtype': tf.int64
            }
        }

    @classmethod
    def from_class_names(cls, class_names):
        """
        Create `MultiLabelSpec` object from a list of names specifying each classes

        :param list class_names: A list of names specifying each classes
        :return: `MultiLabelSpec` object
        :rtype: MultiLabelSpec
        """
        obj = cls(len(class_names), class_names)

        return obj

    def parse(self, parent_key, record):
        """
        Parse TF-record and returns `tf.Tensor`

        :param str parent_key: The key of the feature
        :param tf.Tensor record: String tensor of TF-record
        :return: A 1-D tensor containing label
        :rtype: tf.Tensor
        """
        parsed = FeatureSpec.parse(self, parent_key, record)

        return parsed['{}/{}'.format(parent_key, 'tensor')]

    def create_with_tensor(self, tensor):
        # TODO: Assert shape
        return {
            'tensor': tensor
        }

    def create_with_labels(self, labels):
        # TODO: Assert bad labels don't exist
        return {
            'tensor': list(map(lambda cls: int(cls in labels), self._class_names))
        }


class EnumSpec(FeatureSpec):
    """A class for specifying enum.
    """

    def __init__(self, enum_cls):
        super(EnumSpec, self).__init__(())

        self.enum = enum_cls

    @property
    def feature_proto_spec(self):
        """
        A property for specifying inner encoding spec of the feature

        :return: The dict containing shape and dtype info
        :rtype: dict
        """
        return {
            'enum': {
                'shape': (),
                'dtype': tf.string,
            }
        }

    def parse(self, parent_key, record):
        """
        Parse TF-record and returns `tf.Tensor`

        :param str parent_key: The key of the feature
        :param tf.Tensor record: String tensor of TF-record
        :return: A scalar tensor containing an id
        :rtype: tf.Tensor
        """
        parsed = FeatureSpec.parse(self, parent_key, record)

        return parsed['{}/enum'.format(parent_key)]

    def create_with_string(self, string: str):
        if string not in [lambda e: e.value, list(self.enum)]:
            raise ValueError('String should be one of members ({})'.format(list(self.enum)))

        return {
            'enum': string,
        }

    def create_with_member(self, member: Enum):
        return {
            'enum': member.value,
        }
