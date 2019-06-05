from pkg_resources import require
require("numpy>=1.11.1")
require("mock>=1.0.1")
from unittest import TestCase

from CrystalMatch.dls_focusstack.focus.sharpness_detector import SharpnessDetector
from mock import MagicMock

class TestSharpnessDetector(TestCase):

    def setUp(self):
        self._fft_images = MagicMock()
        self._config = MagicMock()
        self._fft_images.__len__= MagicMock(return_value = 20)

    def test_image_stack_method_returns_list_of_images_within_a_range(self):
        fft_image = MagicMock()
        fft_image.getFFT.return_value = 10
        fft_image.get_image_number.return_value = 0
        fft_image.get_image.return_value = 100
        self._config.number_to_stack.value.return_value = 1
        self._fft_images = [fft_image]

        sd = SharpnessDetector(self._fft_images, self._config)
        images = sd.images_to_stack()
        self.assertEqual(images[0],100)

#TODO: parametrization of the tests would reduce repetitions
    def test_returns_correct_when_even_number_passed(self):
        max = 10
        number_to_stuck = 12
        self._config.number_to_stack.value = MagicMock(return_value = number_to_stuck)
        sd = SharpnessDetector(self._fft_images, self._config)
        rng = sd.find_range(max)
        self.assertEqual(len(rng), number_to_stuck)
        half = number_to_stuck/2
        self.assertEqual(rng[0], max-half)
        self.assertEqual(rng[number_to_stuck-1], max+half-1)

    def test_works_correctly_when_max_plus_half_equals_to_number_of_images(self):
        max = 14
        number_to_stuck = 12
        self._config.number_to_stack.value = MagicMock(return_value=number_to_stuck)
        sd = SharpnessDetector(self._fft_images, self._config)
        rng = sd.find_range(max)
        half = number_to_stuck/2
        self.assertEqual(len(rng), number_to_stuck)
        self.assertEqual(rng[0], max - half)
        self.assertEqual(rng[number_to_stuck-1], max+half-1)

    def test_works_correctly_when_max_plus_half_bigger_than_number_of_images(self):
        max = 15
        number_to_stuck = 12
        self._config.number_to_stack.value = MagicMock(return_value=number_to_stuck)
        sd = SharpnessDetector(self._fft_images, self._config)
        rng = sd.find_range(max)
        half = number_to_stuck/2
        self.assertEqual(len(rng), number_to_stuck)
        self.assertEqual(rng[0], max - half)
        self.assertEqual(rng[number_to_stuck-1], max+half-1)

    def test_works_correctly_when_max_minus_half_smaller_than_number_of_images(self):
        max = 3
        number_to_stuck = 12
        self._config.number_to_stack.value = MagicMock(return_value=number_to_stuck)
        sd = SharpnessDetector(self._fft_images, self._config)
        rng = sd.find_range(max)
        self.assertEqual(len(rng), number_to_stuck)
        self.assertEqual(rng[0], 0)
        self.assertEqual(rng[number_to_stuck-1],number_to_stuck-1)

    def test_works_correctly_when_max_minus_half_equals_zero(self):
        max = 6
        number_to_stuck = 12
        self._config.number_to_stack.value = MagicMock(return_value=number_to_stuck)
        sd = SharpnessDetector(self._fft_images, self._config)
        rng = sd.find_range(max)
        half = number_to_stuck/2
        self.assertEqual(len(rng), number_to_stuck)
        self.assertEqual(rng[0], max - half)
        self.assertEqual(rng[number_to_stuck-1], max+half-1)

    def test_works_correctly_when_more_to_stack_than_images(self):
        max = 6
        number_to_stuck = 25
        self._config.number_to_stack.value = MagicMock(return_value=number_to_stuck)
        sd = SharpnessDetector(self._fft_images, self._config)
        rng = sd.find_range(max)
        self.assertEqual(len(rng), self._fft_images.__len__.return_value)
        self.assertEqual(rng[0], 0)
        self.assertEqual(rng[self._fft_images.__len__.return_value-1], self._fft_images.__len__.return_value-1)

    def test_works_correctly_when_to_stack_equals_number_of_images(self):
        max = 6
        number_to_stuck = 20
        self._config.number_to_stack.value = MagicMock(return_value=number_to_stuck)
        sd = SharpnessDetector(self._fft_images, self._config)
        rng = sd.find_range(max)
        self.assertEqual(len(rng), self._fft_images.__len__.return_value)
        self.assertEqual(rng[0], 0)
        self.assertEqual(rng[self._fft_images.__len__.return_value-1], self._fft_images.__len__.return_value-1)

    def test_returns_one_less_for_number_to_stack_when_uneven(self):
        max = 10
        number_to_stuck = 11
        self._config.number_to_stack.value = MagicMock(return_value=number_to_stuck)
        sd = SharpnessDetector(self._fft_images, self._config)
        rng = sd.find_range(max)
        half = 6
        self.assertEqual(len(rng), number_to_stuck+1) # one more
        self.assertEqual(rng[0], max-half)
        self.assertEqual(rng[number_to_stuck], max+half-1)


