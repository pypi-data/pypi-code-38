import unittest
from boarml.cnn import *


class TestUnit(unittest.TestCase):

    def test_empty_unit(self):
        # Given
        test_unit = Unit()
        expected = '-Unit-(0)'

        # When
        actual = str(test_unit)

        # Then
        self.assertEqual(expected, actual)
        self.assertEqual(test_unit.size, 0)

    def test_single_layer_unit(self):
        # Given
        test_unit = Unit()

        with open('resources/single_layer_unit.txt', 'r') as input_file:
            expected = input_file.read()

        # When
        test_unit.add_layer(DenseLayer(5))
        actual = str(test_unit)

        # Then
        self.assertEqual(expected, actual)
        self.assertEqual(test_unit.size, 1)

    def test_multi_layer_unit(self):
        # Given
        test_unit = Unit()

        with open('resources/multi_layer_unit.txt', 'r') as input_file:
            expected = input_file.read()

        # When
        test_unit.add_layer(DenseLayer(nodes=5))
        test_unit.add_layer(FlattenLayer())
        test_unit.add_layer(BatchNormalizationLayer(momentum=3))
        test_unit.add_layer(ConvLayer(filters=96, kernel_size=(3, 3), strides=(1, 1)))

        actual = str(test_unit)

        # Then
        self.assertEqual(expected, actual)
        self.assertEqual(test_unit.size, 4)
