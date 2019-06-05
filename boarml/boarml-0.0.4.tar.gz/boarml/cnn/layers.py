from enum import IntEnum
from abc import ABC, abstractmethod
from ast import literal_eval as make_tuple


class Layers(IntEnum):
    INPUT = 1
    CONV = 2
    ACTIVATION = 3
    DENSE = 4
    FLATTEN = 5
    BATCH_NORM = 6
    POOLING = 7
    DROPOUT = 8


MAIN_LAYER_TYPES = {Layers.INPUT: 'InputLayer', Layers.CONV: 'ConvLayer', Layers.ACTIVATION: 'ActivationLayer', Layers.DENSE: 'DenseLayer',
                    Layers.FLATTEN: 'FlattenLayer',
                    Layers.BATCH_NORM: 'BatchNormalizationLayer', Layers.POOLING: 'PoolingLayer', Layers.DROPOUT: 'DropoutLayer'}


class Layer(ABC):

    @property
    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def convert_to_tuple(self, parameter):

        if isinstance(parameter, str):
            return make_tuple(parameter)
        else:
            return parameter

    def convert_to_int(self, parameter):

        if isinstance(parameter, str):
            return int(parameter)
        else:
            return parameter

    def convert_to_float(self, parameter):

        if isinstance(parameter, str):
            return float(parameter)
        else:
            return parameter


class InputLayer(Layer):

    def __init__(self, shape):
        self.shape = self.convert_to_tuple(shape)

    @property
    def type(self):
        return Layers.INPUT

    def __str__(self):
        return f'{MAIN_LAYER_TYPES[self.type]}(shape={self.shape})'


class ConvLayer(Layer):

    def __init__(self, filters, kernel_size, strides):
        self.filters = self.convert_to_int(filters)
        self.kernel_size = self.convert_to_tuple(kernel_size)
        self.strides = self.convert_to_tuple(strides)

    @property
    def type(self):
        return Layers.CONV

    def __str__(self):
        return f'{MAIN_LAYER_TYPES[self.type]}(filters={self.filters}; kernel_size={self.kernel_size}; strides={self.strides})'


class ActivationLayer(Layer):

    def __init__(self, func):
        self.func = func

    @property
    def type(self):
        return Layers.ACTIVATION

    def __str__(self):
        return f'{MAIN_LAYER_TYPES[self.type]}(func="{self.func}")'


class DenseLayer(Layer):

    def __init__(self, nodes):
        self.nodes = self.convert_to_int(nodes)

    @property
    def type(self):
        return Layers.DENSE

    def __str__(self):
        return f'{MAIN_LAYER_TYPES[self.type]}(nodes={self.nodes})'


class FlattenLayer(Layer):

    @property
    def type(self):
        return Layers.FLATTEN

    def __str__(self):
        return f'{MAIN_LAYER_TYPES[self.type]}()'


class BatchNormalizationLayer(Layer):

    def __init__(self, momentum):
        self.momentum = self.convert_to_float(momentum)

    @property
    def type(self):
        return Layers.BATCH_NORM

    def __str__(self):
        return f'{MAIN_LAYER_TYPES[self.type]}(momentum={self.momentum})'


class PoolingLayer(Layer):

    def __init__(self, operation, pool_size, strides):
        self.operation = operation
        self.pool_size = self.convert_to_tuple(pool_size)
        self.strides = self.convert_to_tuple(strides)

    @property
    def type(self):
        return Layers.POOLING

    def __str__(self):
        return f'{MAIN_LAYER_TYPES[self.type]}(operation="{self.operation}"; pool_size={self.pool_size}; strides={self.strides})'


class DropoutLayer(Layer):

    def __init__(self, rate):
        self.rate = self.convert_to_float(rate)

    @property
    def type(self):
        return Layers.DROPOUT

    def __str__(self):
        return f'{MAIN_LAYER_TYPES[self.type]}(rate={self.rate})'


class LayerBuilder:

    @staticmethod
    def build_from_text(text):

        parameters = LayerBuilder.extract_parameters(text)

        if text.startswith(MAIN_LAYER_TYPES[Layers.INPUT]):
            return InputLayer(**parameters)
        if text.startswith(MAIN_LAYER_TYPES[Layers.CONV]):
            return ConvLayer(**parameters)
        if text.startswith(MAIN_LAYER_TYPES[Layers.ACTIVATION]):
            return ActivationLayer(**parameters)
        if text.startswith(MAIN_LAYER_TYPES[Layers.DENSE]):
            return DenseLayer(**parameters)
        if text.startswith(MAIN_LAYER_TYPES[Layers.FLATTEN]):
            return FlattenLayer(**parameters)
        if text.startswith(MAIN_LAYER_TYPES[Layers.BATCH_NORM]):
            return BatchNormalizationLayer(**parameters)
        if text.startswith(MAIN_LAYER_TYPES[Layers.POOLING]):
            return PoolingLayer(**parameters)
        if text.startswith(MAIN_LAYER_TYPES[Layers.DROPOUT]):
            return DropoutLayer(**parameters)

    @staticmethod
    def extract_parameters(text):

        params_dict = dict()
        parameters = text.split('(', maxsplit=1)[1][:-1]

        if not parameters:
            return params_dict

        parameters = parameters.split('; ')

        for p in parameters:
            key_value_list = p.split('=')
            params_dict[key_value_list[0].strip('\"')] = key_value_list[1].strip('\"')

        return params_dict
