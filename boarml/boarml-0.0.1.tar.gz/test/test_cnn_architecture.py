import unittest
from boarml.architectures import CnnBaseArchitecture
from boarml.cnn import *


class TestCnnArchitecture(unittest.TestCase):

    def test_empty_architecture(self):
        # Given
        architecture = CnnBaseArchitecture(input_shape=(32, 32), output_nodes=10)

        with open('resources/empty_architecture.txt', 'r') as input_file:
            expected = input_file.read()

        # When
        actual = str(architecture)

        # Then
        self.assertEqual(expected, actual)

        self.assertEqual(Layers.INPUT, architecture.input_arch[0].type)
        self.assertEqual((32, 32), architecture.input_arch[0].shape)
        self.assertEqual(Layers.FLATTEN, architecture.output_arch[0].type)
        self.assertEqual(Layers.DENSE, architecture.output_arch[1].type)
        self.assertEqual(10, architecture.output_arch[1].nodes)
        self.assertEqual('softmax', architecture.output_arch[2].func)

    def test_simple_architecture(self):
        # Given
        architecture = CnnBaseArchitecture(input_shape=(32, 32), output_nodes=10)

        with open('resources/simple_architecture.txt', 'r') as input_file:
            expected = input_file.read()

        # When

        # Unit
        architecture.new_unit()
        architecture.add_to_unit(ConvLayer(filters=64, kernel_size=(3, 3), strides=(2, 2)))
        architecture.add_to_unit(BatchNormalizationLayer(momentum=0.999))
        architecture.add_to_unit(PoolingLayer(operation='max', pool_size=(2, 2), strides=(2, 2)))
        architecture.add_to_unit(DropoutLayer(rate=0.2))
        architecture.add_to_unit(ActivationLayer(func='relu'))

        actual = str(architecture)

        # Then
        self.assertEqual(expected, actual)

    def test_complex_architecture(self):
        # Given
        architecture = CnnBaseArchitecture(input_shape=(32, 32, 3), output_nodes=10)

        with open('resources/complex_architecture.txt', 'r') as input_file:
            expected = input_file.read()

        # When

        # Unit 1
        architecture.new_unit()
        architecture.add_to_unit(ConvLayer(filters=64, kernel_size=(3, 3), strides=(2, 2)))
        architecture.add_to_unit(BatchNormalizationLayer(momentum=0.999))
        architecture.add_to_unit(PoolingLayer(operation='max', pool_size=(2, 2), strides=(2, 2)))
        architecture.add_to_unit(DropoutLayer(rate=0.2))
        architecture.add_to_unit(ActivationLayer(func='relu'))

        # Unit 2
        architecture.new_unit()
        architecture.add_to_unit(ConvLayer(filters=64, kernel_size=(4, 4), strides=(2, 2)))
        architecture.add_to_unit(BatchNormalizationLayer(momentum=0.999))
        architecture.add_to_unit(PoolingLayer(operation='max', pool_size=(2, 2), strides=(2, 2)))
        architecture.add_to_unit(DropoutLayer(rate=0.2))
        architecture.add_to_unit(ActivationLayer(func='relu'))

        # Unit 3
        architecture.new_unit()
        architecture.add_to_unit(ConvLayer(filters=64, kernel_size=(3, 3), strides=(2, 2)))
        architecture.add_to_unit(BatchNormalizationLayer(momentum=0.999))
        architecture.add_to_unit(PoolingLayer(operation='average', pool_size=(2, 2), strides=(2, 2)))
        architecture.add_to_unit(DropoutLayer(rate=0.2))
        architecture.add_to_unit(ActivationLayer(func='relu'))

        actual = str(architecture)

        # Then
        self.assertEqual(expected, actual)

    def test_custom_input_layers_architecture(self):
        # Given
        architecture = CnnBaseArchitecture(input_shape=(32, 32), output_nodes=10)

        with open('resources/custom_input_layers_architecture.txt', 'r') as input_file:
            expected = input_file.read()

        # When
        input_layers = list()
        input_layers.append(InputLayer(shape=(13, 13)))
        input_layers.append(ConvLayer(filters=64, kernel_size=(4, 4), strides=(2, 2)))
        input_layers.append(ActivationLayer(func='relu'))
        architecture.input_arch = input_layers

        actual = str(architecture)

        # Then
        self.assertEqual(expected, actual)

        self.assertEqual(Layers.INPUT, architecture.input_arch[0].type)
        self.assertEqual((13, 13), architecture.input_arch[0].shape)
        self.assertEqual(Layers.CONV, architecture.input_arch[1].type)
        self.assertEqual(64, architecture.input_arch[1].filters)
        self.assertEqual((4, 4), architecture.input_arch[1].kernel_size)
        self.assertEqual((2, 2), architecture.input_arch[1].strides)
        self.assertEqual(Layers.ACTIVATION, architecture.input_arch[2].type)
        self.assertEqual('relu', architecture.input_arch[2].func)

    def test_custom_output_layers_architecture(self):
        # Given
        architecture = CnnBaseArchitecture(input_shape=(32, 32), output_nodes=10)

        with open('resources/custom_output_layers_architecture.txt', 'r') as input_file:
            expected = input_file.read()

        # When
        output_layers = list()
        output_layers.append(PoolingLayer(operation='max', pool_size=(2, 2), strides=(2, 2)))
        output_layers.append(DropoutLayer(rate=0.2))
        output_layers.append(FlattenLayer())
        architecture.output_arch = output_layers

        actual = str(architecture)

        # Then
        self.assertEqual(expected, actual)

        self.assertEqual(Layers.POOLING, architecture.output_arch[0].type)
        self.assertEqual('max', architecture.output_arch[0].operation)
        self.assertEqual((2, 2), architecture.output_arch[0].pool_size)
        self.assertEqual((2, 2), architecture.output_arch[0].strides)
        self.assertEqual(Layers.DROPOUT, architecture.output_arch[1].type)
        self.assertEqual(0.2, architecture.output_arch[1].rate)
        self.assertEqual(Layers.FLATTEN, architecture.output_arch[2].type)

    def test_custom_main_layers_architecture(self):
        # Given
        architecture = CnnBaseArchitecture(input_shape=(32, 32), output_nodes=10)

        with open('resources/custom_main_layers_architecture.txt', 'r') as input_file:
            expected = input_file.read()

        # When
        main_layers = list()

        # Unit 1
        new_unit = Unit()
        new_unit.add_layer(ConvLayer(filters=64, kernel_size=(3, 3), strides=(2, 2)))
        new_unit.add_layer(BatchNormalizationLayer(momentum=0.999))
        main_layers.append(new_unit)

        # Unit 2
        new_unit = Unit()
        new_unit.add_layer(PoolingLayer(operation='max', pool_size=(2, 2), strides=(2, 2)))
        new_unit.add_layer(DropoutLayer(rate=0.2))
        new_unit.add_layer(ActivationLayer(func='relu'))
        main_layers.append(new_unit)

        architecture.main_arch = main_layers

        actual = str(architecture)

        # Then
        self.assertEqual(expected, actual)

        self.assertEqual(Layers.CONV, architecture.main_arch[0].layers[0].type)
        self.assertEqual(64, architecture.main_arch[0].layers[0].filters)
        self.assertEqual((3, 3), architecture.main_arch[0].layers[0].kernel_size)
        self.assertEqual((2, 2), architecture.main_arch[0].layers[0].strides)

        self.assertEqual(Layers.BATCH_NORM, architecture.main_arch[0].layers[1].type)
        self.assertEqual(0.999, architecture.main_arch[0].layers[1].momentum)

        self.assertEqual(Layers.POOLING, architecture.main_arch[1].layers[0].type)
        self.assertEqual('max', architecture.main_arch[1].layers[0].operation)
        self.assertEqual((2, 2), architecture.main_arch[1].layers[0].pool_size)
        self.assertEqual((2, 2), architecture.main_arch[1].layers[0].strides)

        self.assertEqual(Layers.DROPOUT, architecture.main_arch[1].layers[1].type)
        self.assertEqual(0.2, architecture.main_arch[1].layers[1].rate)

        self.assertEqual(Layers.ACTIVATION, architecture.main_arch[1].layers[2].type)
        self.assertEqual('relu', architecture.main_arch[1].layers[2].func)

    def test_build_empty_from_text(self):
        # Given
        expected = CnnBaseArchitecture(input_shape=(32, 32), output_nodes=10)

        # When
        actual = CnnBaseArchitecture()
        actual = actual.build_from_file('resources/empty_architecture.txt')

        # Then
        self.assertEqual(str(expected), str(actual))

    def test_build_simple_from_text(self):
        # Given
        expected = CnnBaseArchitecture(input_shape=(32, 32), output_nodes=10)
        expected.new_unit()
        expected.add_to_unit(ConvLayer(filters=64, kernel_size=(3, 3), strides=(2, 2)))
        expected.add_to_unit(BatchNormalizationLayer(momentum=0.999))
        expected.add_to_unit(PoolingLayer(operation="max", pool_size=(2, 2), strides=(2, 2)))
        expected.add_to_unit(DropoutLayer(rate=0.2))
        expected.add_to_unit(ActivationLayer(func="relu"))
        expected.output_arch = [FlattenLayer(), DenseLayer(nodes=10), ActivationLayer(func="softmax")]

        # When
        actual = CnnBaseArchitecture()
        actual = actual.build_from_file('resources/simple_architecture.txt')

        # Then
        self.assertEqual(str(expected), str(actual))

    def test_build_complex_from_text(self):
        # Given
        expected = CnnBaseArchitecture(input_shape=(32, 32, 3), output_nodes=10)

        # Unit 1
        expected.new_unit()
        expected.add_to_unit(ConvLayer(filters=64, kernel_size=(3, 3), strides=(2, 2)))
        expected.add_to_unit(BatchNormalizationLayer(momentum=0.999))
        expected.add_to_unit(PoolingLayer(operation="max", pool_size=(2, 2), strides=(2, 2)))
        expected.add_to_unit(DropoutLayer(rate=0.2))
        expected.add_to_unit(ActivationLayer(func='relu'))

        # Unit 2
        expected.new_unit()
        expected.add_to_unit(ConvLayer(filters=64, kernel_size=(4, 4), strides=(2, 2)))
        expected.add_to_unit(BatchNormalizationLayer(momentum=0.999))
        expected.add_to_unit(PoolingLayer(operation="max", pool_size=(2, 2), strides=(2, 2)))
        expected.add_to_unit(DropoutLayer(rate=0.2))
        expected.add_to_unit(ActivationLayer(func='relu'))

        # Unit 3
        expected.new_unit()
        expected.add_to_unit(ConvLayer(filters=64, kernel_size=(3, 3), strides=(2, 2)))
        expected.add_to_unit(BatchNormalizationLayer(momentum=0.999))
        expected.add_to_unit(PoolingLayer(operation="average", pool_size=(2, 2), strides=(2, 2)))
        expected.add_to_unit(DropoutLayer(rate=0.2))
        expected.add_to_unit(ActivationLayer(func='relu'))

        expected.output_arch = [FlattenLayer(), DenseLayer(nodes=10), ActivationLayer(func='softmax')]

        # When
        actual = CnnBaseArchitecture()
        actual = actual.build_from_file('resources/complex_architecture.txt')

        # Then
        self.assertEqual(str(expected), str(actual))

    def test_build_invalid_start(self):
        # When
        actual = CnnBaseArchitecture()

        # Then
        self.assertRaises(Exception, actual.build_from_file, 'resources/invalid_start_architecture.txt')

    def test_build_invalid_end(self):
        # When
        actual = CnnBaseArchitecture()

        # Then
        self.assertRaises(Exception, actual.build_from_file, 'resources/invalid_end_architecture.txt')
