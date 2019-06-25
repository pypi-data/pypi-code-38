import unittest
from yo_core._common.ordered_enum import *
import pandas as pd

class TestEnum(OrderedEnum):
    LESS = 0
    GREATER = 1

class TestOrderedEnum(unittest.TestCase):
    def test_ordered_enum(self):
        self.assertGreater(TestEnum.GREATER,TestEnum.LESS)
        self.assertGreaterEqual(TestEnum.GREATER, TestEnum.LESS)
        self.assertLess(TestEnum.LESS,TestEnum.GREATER)
        self.assertLessEqual(TestEnum.LESS,TestEnum.GREATER)

        self.assertRaises(NotImplementedError, lambda:TestEnum.GREATER > 0)
        self.assertRaises(NotImplementedError, lambda:TestEnum.GREATER >= 0)
        self.assertRaises(NotImplementedError, lambda:TestEnum.GREATER < 0)
        self.assertRaises(NotImplementedError, lambda:TestEnum.GREATER <= 0)

    def test_ord_enum_in_pd(self):
        df = pd.DataFrame({'a':[TestEnum.GREATER,TestEnum.GREATER,TestEnum.LESS],'b':[1,1,2]})
        df.groupby('a').size()
