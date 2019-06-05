from unittest import TestCase
import futsu.csv as fcsv
import tempfile
import os

class TestCsv(TestCase):

    def test_read_csv(self):
        v_dict_list, col_name_list = fcsv.read_csv(os.path.join('futsu','test','test_csv_0.csv'))
        self.assertEqual(col_name_list,['a','b'])
        self.assertEqual(len(v_dict_list),2)
        self.assertEqual(v_dict_list[0],{'a':'1','b':'2'})
        self.assertEqual(v_dict_list[1],{'a':'3','b':'4'})

        v_dict_list, col_name_list = fcsv.read_csv(os.path.join('futsu','test','test_csv_1.csv'))
        self.assertEqual(col_name_list,['a'])
        self.assertEqual(v_dict_list,[{'a':''}])

        v_dict_list, col_name_list = fcsv.read_csv(os.path.join('futsu','test','test_csv_2.csv'))
        self.assertEqual(col_name_list,['a','b'])
        self.assertEqual(v_dict_list,[{'a':'','b':''}])

    def test_write_csv(self):

        with tempfile.TemporaryDirectory() as tempdir:
            tmp_filename = os.path.join(tempdir,'test.csv')

            v_dict_list = [{'a':'3','b':'4'},{'a':'1','b':'2'}]
            fcsv.write_csv(tmp_filename, v_dict_list)
            
            v_dict_list, col_name_list = fcsv.read_csv(tmp_filename)
            self.assertEqual(col_name_list,['a','b'])
            self.assertEqual(len(v_dict_list),2)
            self.assertEqual(v_dict_list[0],{'a':'3','b':'4'})
            self.assertEqual(v_dict_list[1],{'a':'1','b':'2'})

            v_dict_list = [{'a':'3','b':'4'},{'a':'1','b':'2'}]
            fcsv.write_csv(tmp_filename, v_dict_list, col_name_list=['a'])
            
            v_dict_list, col_name_list = fcsv.read_csv(tmp_filename)
            self.assertEqual(col_name_list,['a'])
            self.assertEqual(len(v_dict_list),2)
            self.assertEqual(v_dict_list[0],{'a':'3'})
            self.assertEqual(v_dict_list[1],{'a':'1'})

            v_dict_list = [
                {'a':'3','b':'4'},
                {'a':'2','b':'0'},
                {'a':'2','b':'0'},
                {'a':'1','b':'2'},
                {'a':'1','b':'1'}
            ]
            fcsv.write_csv(tmp_filename, v_dict_list, sort_key_list=['a','b'])
            
            v_dict_list, col_name_list = fcsv.read_csv(tmp_filename)
            self.assertEqual(col_name_list,['a','b'])
            self.assertEqual(len(v_dict_list),5)
            self.assertEqual(v_dict_list[0],{'a':'1','b':'1'})
            self.assertEqual(v_dict_list[1],{'a':'1','b':'2'})
            self.assertEqual(v_dict_list[2],{'a':'2','b':'0'})
            self.assertEqual(v_dict_list[3],{'a':'2','b':'0'})
            self.assertEqual(v_dict_list[4],{'a':'3','b':'4'})

            v_dict_list = [{'a':None}]
            fcsv.write_csv(tmp_filename, v_dict_list)

            v_dict_list, col_name_list = fcsv.read_csv(tmp_filename)
            self.assertEqual(v_dict_list,[{'a':''}])
