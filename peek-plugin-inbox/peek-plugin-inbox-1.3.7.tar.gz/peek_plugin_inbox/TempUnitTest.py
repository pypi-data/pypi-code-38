import unittest
from unittest import skip

''' DELETE ME when the first real test is added'''

class TempUnitTest(unittest.TestCase):
    def testPass(self):
        self.assertTrue(True)

    @skip("Tesging skip")
    def testFail(self):
        self.assertTrue(False)


