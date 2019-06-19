import unittest

from Matrix import Matrix

class TestMatrixClass(unittest.TestCase):
    def setUp(self):
        self.matrix = Matrix(4,5)
        
    def test_initialization(self):
        self.assertEqual(self.matrix.m, 4, 'incorrect m dimension')
        self.assertEqual(self.matrix.n, 5, 'incorrect n dimension')

    #TODO:
    #   test insert, add, subtract, multiply
        
        
        
if __name__ == '__main__':
    unittest.main()