from unittest import TestCase
import futsu.json as fjson
import tempfile
import os

class TestJson(TestCase):

    def test_file_input(self):
        data = fjson.file_input(os.path.join('futsu','test','test_json_0.json'))
        self.assertEqual(data,{'qwer':'asdf'})

    def test_file_output(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir,'ALSFAWFHMY')

            self.assertFalse(os.path.isfile(tmp_filename))

            data={'qwer':'asdf'}
            fjson.file_output(tmp_filename, data)
            self.assertTrue(os.path.isfile(tmp_filename))
            
            data = fjson.file_input(tmp_filename)
            self.assertEqual(data,{'qwer':'asdf'})
