import unittest
from boarml.generators import *
from boarml.architectures import *


class TestModelGenerator(unittest.TestCase):

    def test_create_base_model(self):
        # Given
        architecture = CnnBaseArchitecture()
        architecture.build_from_file('resources/complex_architecture.txt')

        # When
        generator = ModelGenerator(architecture, 'keras')
        actual = generator.create_base_model()

        # Then
        self.assertEqual(19, len(actual.model._layers))

    def test_create_mutated_model_duplication(self):
        # Given
        expected = CnnBaseArchitecture()
        expected = expected.build_from_file('resources/mutated_architecture_duplication.txt')

        architecture = CnnBaseArchitecture()
        architecture.build_from_file('resources/complex_architecture.txt')

        # When
        generator = ModelGenerator(architecture, 'keras', removal_rate=0, duplication_rate=1, amendment_rate=0, seed=14)
        actual = generator.create_mutated_model()
        mutated_arch = generator.get_last_mutation()

        # Then
        self.assertEqual(34, len(actual.model._layers))
        self.assertEqual(str(expected), str(mutated_arch))

    def test_create_mutated_model_amendments(self):
        # Given
        expected = CnnBaseArchitecture()
        expected = expected.build_from_file('resources/mutated_architecture_amendments.txt')

        architecture = CnnBaseArchitecture()
        architecture.build_from_file('resources/complex_architecture.txt')

        # When
        generator = ModelGenerator(architecture, 'keras', removal_rate=0, duplication_rate=0, amendment_rate=1, seed=13)
        actual = generator.create_mutated_model()
        mutated_arch = generator.get_last_mutation()

        # Then
        self.assertEqual(16, len(actual.model._layers))
        self.assertEqual(str(expected), str(mutated_arch))

    def test_create_mutated_model_removal(self):
        # Given
        expected = CnnBaseArchitecture()
        expected = expected.build_from_file('resources/mutated_architecture_removal.txt')

        architecture = CnnBaseArchitecture()
        architecture.build_from_file('resources/complex_architecture.txt')

        # When
        generator = ModelGenerator(architecture, 'keras', removal_rate=0.5, duplication_rate=0, amendment_rate=0, seed=13)
        actual = generator.create_mutated_model()
        mutated_arch = generator.get_last_mutation()

        # Then
        self.assertEqual(9, len(actual.model._layers))
        self.assertEqual(str(expected), str(mutated_arch))

    def test_unknown_builder(self):
        # Given
        architecture = CnnBaseArchitecture()

        # When
        generator = ModelGenerator(architecture, 'foo')

        # Then
        self.assertRaises(Exception, generator.create_base_model)

    def test_populate_builder_history(self):
        # Given
        expected = CnnBaseArchitecture()
        expected = expected.build_from_file('resources/mutated_architecture_history_duplicate.txt')

        architecture = CnnBaseArchitecture()
        architecture.build_from_file('resources/complex_architecture.txt')

        # When
        generator = ModelGenerator(architecture, 'keras', removal_rate=0, duplication_rate=0.8, amendment_rate=0, seed=14)
        generator.populate_history('resources/history', 'test-arch-', 3)
        actual = generator.create_mutated_model()
        mutated_arch = generator.get_last_mutation()

        # Then
        self.assertEqual(24, len(actual.model._layers))
        self.assertEqual(str(expected), str(mutated_arch))

    def test_get_last_empty_mutation(self):
        # Given
        expected = CnnBaseArchitecture()
        expected = expected.build_from_file('resources/complex_architecture.txt')

        architecture = CnnBaseArchitecture()
        architecture.build_from_file('resources/complex_architecture.txt')

        # When
        generator = ModelGenerator(architecture, 'keras')
        mutated_arch = generator.get_last_mutation()

        # Then
        self.assertEqual(str(expected), str(mutated_arch))