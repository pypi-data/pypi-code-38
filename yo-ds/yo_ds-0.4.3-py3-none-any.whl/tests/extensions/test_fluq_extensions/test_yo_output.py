import unittest
from tests.extensions.common import *

import pandas as pd


FOLDER = 'test_fluq_extensions/files'

class DTO:
    def __init__(self,num):
        self.num = num
        self.s = 'test'*num
        self.array = Query.en(range(num)).to_list()


class ExtendedMethodsTests(unittest.TestCase):

    def test_text_file(self):
        data = Query.file.text(path(FOLDER,'../sample.txt')).to_list()
        self.assertListEqual(["1","2","","3","4"],data)

    def test_text_io(self):
        os.makedirs(path(FOLDER), exist_ok=True)
        array = ['23','342','1241','','452']
        Query.en(array).feed(fluq.to_text_file(path(FOLDER, 'sample1.txt'), autoflush=True))
        self.assertListEqual(array,Query.file.text(path(FOLDER,'sample1.txt')).to_list())

    def test_zip_io(self):
        os.makedirs(path(FOLDER), exist_ok=True)
        array = ['23', '342', '1241', '', '452']
        Query.en(array).feed(fluq.to_zip_text_file(path(FOLDER, 'sample1.txt.gzip')))
        self.assertListEqual(array,Query.file.zipped_text(path(FOLDER,'sample1.txt.gzip')).to_list())





    def test_pickle_unpickle(self):
        os.makedirs(path(FOLDER),exist_ok=True)
        Query.en(range(10)).select(DTO).feed(fluq.to_pickle_file(path(FOLDER, 'sample.pickle')))
        result = Query.file.pickle(path(FOLDER,'sample.pickle')).with_indices().all(lambda z:
          z.item.num == z.index and
          z.item.s == 'test'*z.index and
          len(z.item.array) == z.index)
        self.assertTrue(result)
