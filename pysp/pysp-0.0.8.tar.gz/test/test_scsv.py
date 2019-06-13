# -*- coding: utf-8 -*-

import codecs
import hexdump
import unittest
import os

from pysp.scsv import SCSV


NORMAL_CONTENT = '''Normal,,\r
2018-10-30 22:37:02,,\r
,string,integer,float\r
1,text,1,1.1\r
2,"t
e
x
t
",2,2.2\r
'''

STRING_CONTENT = '''To String,,\r
2018-10-30 23:06:45,,\r
,string,integer,float\r
1,"=""text""","=""1""","=""1.1"""\r
2,"t
e
x
t
","=""2""","=""2.2"""\r
'''


class CSVTest(unittest.TestCase):
    TMP_FOLDER = '/tmp/csv/'
    TMP_CSV_NORMAL_FILE = TMP_FOLDER+'csv_normal.csv'
    TMP_CSV_STRING_FILE = TMP_FOLDER+'csv_string.csv'
    TMP_CSV_SPLIT_FILE = TMP_FOLDER+'csv_split.csv'

    data_columns = ['string', 'integer', 'float']
    data_fields = [
            ['text', 1, 1.1],
            ['t\ne\nx\nt\n', 2, 2.2],
        ]

    # def tearDown(self):
    #     self.delete_file(self.TMP_CSV_NORMAL_FILE)
    #     self.delete_file(self.TMP_CSV_STRING_FILE)
    #
    # def delete_file(self, del_file):
    #     if os.path.exists(del_file):
    #         os.remove(del_file)

    def test_normal_csv_file(self):
        csv = SCSV(self.TMP_CSV_NORMAL_FILE, 'Normal', self.data_columns)
        for field in self.data_fields:
            csv.write_field(field)
        del csv
        with codecs.open(self.TMP_CSV_NORMAL_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            hexdump.hexdump(NORMAL_CONTENT.encode('utf-8'))
            hexdump.hexdump(content.encode('utf-8'))
            self.assertTrue(content[0x20:] == NORMAL_CONTENT[0x20:])

    def test_string_csv_file(self):
        csv = SCSV(self.TMP_CSV_STRING_FILE, 'To String', self.data_columns)
        for field in self.data_fields:
            csv.write_field(field, to_str=True)
        del csv
        with codecs.open(self.TMP_CSV_STRING_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            hexdump.hexdump(STRING_CONTENT.encode('utf-8'))
            hexdump.hexdump(content.encode('utf-8'))
            self.assertTrue(content[0x20:] == STRING_CONTENT[0x20:])

    def test_split_csv_file(self):
        field = ['split', 3, 3.333]
        SCSV.MAX_FIELD_COUNT = 10
        csv = SCSV(self.TMP_CSV_SPLIT_FILE, 'SPLIT CSV', self.data_columns)
        for i in range(25):
            csv.write_field(field)
        del csv

        apath = self.TMP_CSV_SPLIT_FILE.split('.')
        fname = '.'.join(apath[:-1])
        ext = apath[-1]
        for i in range(3):
            filename = SCSV.SPLIT_FILE_FORMAT.format(
                        fname=fname, idx=i, ext=ext)
            print(filename)
            self.assertTrue(os.path.exists(filename))
