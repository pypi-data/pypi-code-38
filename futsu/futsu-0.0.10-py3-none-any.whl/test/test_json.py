from unittest import TestCase
import futsu.json as fjson
import tempfile
import os

class TestJson(TestCase):

    def test_file_to_data(self):
        data = fjson.file_to_data(os.path.join('futsu','test','test_json_0.json'))
        self.assertEqual(data,{'qwer':'asdf'})

    def test_data_to_file(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir,'ALSFAWFHMY')

            self.assertFalse(os.path.isfile(tmp_filename))

            data={'qwer':'asdf'}
            fjson.data_to_file(tmp_filename, data)
            self.assertTrue(os.path.isfile(tmp_filename))
            
            data = fjson.file_to_data(tmp_filename)
            self.assertEqual(data,{'qwer':'asdf'})
