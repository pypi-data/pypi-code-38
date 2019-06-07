from unittest import TestCase
import futsu.fs as fs
import tempfile
import os

class TestFs(TestCase):

    def test_makedirs(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_dirname = os.path.join(tempdir,'JBMLJUBDTQ','TJLQSLRTJL')
            self.assertFalse(os.path.isdir(tmp_dirname))
            fs.makedirs(tmp_dirname)
            self.assertTrue(os.path.isdir(tmp_dirname))
            fs.makedirs(tmp_dirname) # test run 2 times
            self.assertTrue(os.path.isdir(tmp_dirname))

    def test_reset_dir(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_dirname = os.path.join(tempdir,'JUEJKVTEJR','TYEAWJIQSN')
            tmp_filename = os.path.join(tmp_dirname,'JEWKHIDKCU')

            self.assertFalse(os.path.isdir(tmp_dirname))
            self.assertFalse(os.path.isfile(tmp_filename))

            fs.reset_dir(tmp_dirname) # test create tmp_dirname
            self.assertTrue(os.path.isdir(tmp_dirname))
            self.assertFalse(os.path.isfile(tmp_filename))

            with open(tmp_filename,'wt') as fout:
                fout.write('\n')
            self.assertTrue(os.path.isdir(tmp_dirname))
            self.assertTrue(os.path.isfile(tmp_filename))

            fs.reset_dir(tmp_dirname) # test clean tmp_filename
            self.assertTrue(os.path.isdir(tmp_dirname))
            self.assertFalse(os.path.isfile(tmp_filename))

    def test_diff(self):
        self.assertFalse(fs.diff(
            os.path.join('futsu','test','test_diff_0.txt'),
            os.path.join('futsu','test','test_diff_1.txt')
        ))
        self.assertTrue(fs.diff(
            os.path.join('futsu','test','test_diff_0.txt'),
            os.path.join('futsu','test','test_diff_2.txt')
        ))

    def test_cp(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir,'YHGASBIGHI')
            fs.cp(
                tmp_filename,
                os.path.join('futsu','test','test_cp_0.txt')
            )
            self.assertFalse(fs.diff(
                tmp_filename,
                os.path.join('futsu','test','test_cp_0.txt')
            ))

    def test_file_to_string_list(self):
        line_list = fs.file_to_string_list(os.path.join('futsu','test','test_fs_0.txt'))
        self.assertEqual(line_list,['qwer','asdf'])

        line_list = fs.file_to_string_list(os.path.join('futsu','test','test_fs_1.txt'))
        self.assertEqual(line_list,['qwer','asdf'])

        line_list = fs.file_to_string_list(os.path.join('futsu','test','test_fs_2.txt'))
        self.assertEqual(line_list,['qwer','asdf',''])

    def test_string_list_to_file(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir,'PRXNBTESJS')

            line_list = ['qwer','asdf']
            fs.string_list_to_file(tmp_filename, line_list)
            self.assertEqual(line_list,['qwer','asdf'])

            line_list = ['qwer','asdf','']
            fs.string_list_to_file(tmp_filename, line_list)
            self.assertEqual(line_list,['qwer','asdf',''])
            