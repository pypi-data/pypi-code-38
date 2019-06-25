if __name__ == '__main__':
    import unittest
else:
    # this hack hide following test cases from 'python setup.py test'
    class Hack:
        TestCase = object
    unittest = Hack()

class TrainScriptsTest(unittest.TestCase):
    def test_rfcn_ohem(self):
        return
        print('ModelConversionTest: rfcn_ohem')

   def testMultiTasks(self):
        return
        print('MnistBasicTest: testMultiTasks')

    def testMimic(self):
        return
        print('MnistBasicTest: testMimic')

    def testSparse(self):
        return
        print('MnistBasicTest: testSparse')

    def testAutoCompress(self):
        return
        print('MnistBasicTest: testAutoCompress')

    def testSaveMemory(self):
        return
        print('MnistBasicTest: testSaveMemory')

    def testDistributed(self):
        return
        print('MnistBasicTest: testDistributed')

    def testPserver(self):
        return
        print('MnistBasicTest: testPserver')

    def testModelParallel(self):
        return
        print('MnistBasicTest: testModelParallel')


