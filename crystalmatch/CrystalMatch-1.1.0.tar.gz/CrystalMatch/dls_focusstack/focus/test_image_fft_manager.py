from pkg_resources import require
require("pygelf>=0.3.1")
require("numpy>=1.11.1")
require("scipy>=0.19.1")
require("mock>=1.0.1")

from CrystalMatch.dls_focusstack.focus import image_fft_manager

from unittest import TestCase

from mock import MagicMock

from CrystalMatch.dls_focusstack.focus.image_fft_manager import ImageFFTManager
import os

class TestImageFFTManager(TestCase):

    def setUp(self):
        self._file1= MagicMock()
        self._file2 = MagicMock()
        dict = os.path.join(".", "system-tests", "resources")
        self._file1.name = os.path.join(dict, "A02.jpg")
        self._file2.name = os.path.join(dict, "A03.jpg")
        file_list = [self._file1, self._file2]
        self._imgFFTmanEmpty = ImageFFTManager(file_list)
        self._imgFFTman = ImageFFTManager(file_list)
        self._imgFFTman.read_ftt_images()

    def test_read_ftt_images_creates_list_of_two_fft_images_for_two_input_file_objects(self):
        self.assertEquals(len(self._imgFFTmanEmpty.fft_images), 0)
        self._imgFFTmanEmpty.read_ftt_images()
        self.assertEquals(len(self._imgFFTmanEmpty.fft_images), 2)

    def test_an_exception_is_raised_when_trying_to_read_a_file_which_does_not_exist(self):
        file3 = MagicMock()
        file3.name = "FL0"
        self.failUnlessRaises(ImageFFTManager([file3]))

    def test_get_fft_images_return_the_correct_field(self):
        self.assertEquals(self._imgFFTman.fft_images, self._imgFFTman.get_fft_images())

    def test_the_created_fft_images_contain_image_array(self):
        for fft_img in self._imgFFTman.get_fft_images():
            self.assertIsNotNone(fft_img.get_image())

    def test_the_created_fft_images_are_numbered_according_to_the_sequence_of_the_input_list(self):
        file_list = [self._file1, self._file2]
        manager = ImageFFTManager(file_list)
        manager.read_ftt_images()
        for idx, name in enumerate(file_list):
            for fft_img in manager.get_fft_images():
                if(fft_img.get_image_name() == name): #assuming the names are unique
                    self.failUnlessEqual(fft_img.get_image_number, idx)

    def test_the_created_fft_images_contain_fft(self):
        for fft_img in self._imgFFTman.get_fft_images():
            self.assertIsNotNone(fft_img.getFFT())

    def test_fft_method_creates_fft_value_and_set_the_image_number_correctly(self):
        param = (self._file1.name, 10)
        image_fft = image_fft_manager.fft(param)
        self.assertIsNotNone(image_fft.getFFT())
        self.assertEquals(image_fft.get_image_number(), 10)
