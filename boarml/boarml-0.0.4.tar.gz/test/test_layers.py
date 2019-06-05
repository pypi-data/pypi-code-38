import unittest
from boarml.cnn.layers import *


class TestLayers(unittest.TestCase):

    def test_input_layer(self):
        # Given
        layer = InputLayer(shape=(3, 4))
        expected = 'InputLayer(shape=(3, 4))'

        # When
        actual = str(layer)

        # Then
        self.assertEqual(Layers.INPUT, layer.type)
        self.assertEqual(expected, actual)

    def test_conv_layer(self):
        # Given
        layer = ConvLayer(filters=64, kernel_size=(3, 3), strides=(2, 2))
        expected = 'ConvLayer(filters=64; kernel_size=(3, 3); strides=(2, 2))'

        # When
        actual = str(layer)

        # Then
        self.assertEqual(Layers.CONV, layer.type)
        self.assertEqual(expected, actual)

    def test_activation_layer(self):
        # Given
        layer = ActivationLayer(func='relu')
        expected = 'ActivationLayer(func="relu")'

        # When
        actual = str(layer)

        # Then
        self.assertEqual(Layers.ACTIVATION, layer.type)
        self.assertEqual(expected, actual)

    def test_dense_layer(self):
        # Given
        layer = DenseLayer(nodes=10)
        expected = 'DenseLayer(nodes=10)'

        # When
        actual = str(layer)

        # Then
        self.assertEqual(Layers.DENSE, layer.type)
        self.assertEqual(expected, actual)

    def test_flatten_layer(self):
        # Given
        layer = FlattenLayer()
        expected = 'FlattenLayer()'

        # When
        actual = str(layer)

        # Then
        self.assertEqual(Layers.FLATTEN, layer.type)
        self.assertEqual(expected, actual)

    def test_batch_normalization_layer(self):
        # Given
        layer = BatchNormalizationLayer(momentum=0.99)
        expected = 'BatchNormalizationLayer(momentum=0.99)'

        # When
        actual = str(layer)

        # Then
        self.assertEqual(Layers.BATCH_NORM, layer.type)
        self.assertEqual(expected, actual)

    def test_pooling_layer(self):
        # Given
        layer = PoolingLayer(operation='max', pool_size=(2, 2), strides=(2, 2))
        expected = 'PoolingLayer(operation="max"; pool_size=(2, 2); strides=(2, 2))'

        # When
        actual = str(layer)

        # Then
        self.assertEqual(Layers.POOLING, layer.type)
        self.assertEqual(expected, actual)

    def test_droput_layer(self):
        # Given
        layer = DropoutLayer(rate=0.2)
        expected = 'DropoutLayer(rate=0.2)'

        # When
        actual = str(layer)

        # Then
        self.assertEqual(Layers.DROPOUT, layer.type)
        self.assertEqual(expected, actual)
