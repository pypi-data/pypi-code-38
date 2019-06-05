from unittest import TestCase
import futsu.json as fjson
import tempfile
import os

class TestIo(TestCase):

    def test_json_read(self):
        data = fjson.json_read(os.path.join('futsu','test','test_json_0.json'))
        self.assertEqual(data,{'qwer':'asdf'})

    def test_json_write(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir,'ALSFAWFHMY')

            self.assertFalse(os.path.isfile(tmp_filename))

            data={'qwer':'asdf'}
            fjson.json_write(tmp_filename, data)
            self.assertTrue(os.path.isfile(tmp_filename))
            
            data = fjson.json_read(tmp_filename)
            self.assertEqual(data,{'qwer':'asdf'})
