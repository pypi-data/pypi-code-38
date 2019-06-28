import pathlib
import unittest

from tokenizer_tools.conll.iterator_reader import iterator_reader

from . import data_dir


class TestIteratorReader(unittest.TestCase):
    def test_iterator_reader(self):
        input_file = [i for i in pathlib.Path(data_dir).glob('*') if i.is_file()]

        output = list(iterator_reader(input_file))

        self.assertCountEqual(output, [[['3', 'c'], ['4', 'd']], [['31', 'c1'], ['41', 'd1']], [['1', 'a'], ['2', 'b']], [['11', 'a1'], ['21', 'b1']]])
