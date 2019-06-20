import unittest
from openProduction.suite import TestSuite, TestClass, TestSuiteValueContainer
from openProduction.suite import ExecutionHelpers
from openProduction.common import Types, Version

class MyValues(TestSuiteValueContainer.TestSuiteValues):
    def __init__(self):
        super(MyValues, self).__init__()
        self.addValue(Types.String("MY_VAL", "Simple description"))

class MyCls(TestClass.TestClass):
    def __init__(self):
        self.params = {}
        self.params["startTrigger"] = False
        
    def _myFunc(self, params, values):
        self.assertEqual(0,0)
    
    @ExecutionHelpers.skipIf(True==True)
    def _mySkipFunc(self, params, values):
        pass
    
    def _myFailFunc(self, params, values):
        self.assertEqual(0,1)
        
    def _myExceptionFunc(self, params, values):
        raise RuntimeError("something went wrong...")
        
    def _myFuncWithParams(self, params, values):
        self.assertEqual(params["TEST_PARAM"], 10)
        
    def _myCustomVals(self, params, values):
        values.MY_VAL = "hello"
        
    def _myAddTestGroup(self, params, attrs):
        tg = TestSuite.TestCaseGroup("testGroup", "testDoc")
        _myFunc = MyCls()._myFunc
        tc = TestSuite.TestCase(_myFunc.__name__, _myFunc.__doc__, _myFunc, TestSuite.StepType.REGULAR)
        tg.addTestCase(tc)
        return tg

class TestSuiteTests(unittest.TestCase):

    def test_pass(self):
        """Test a pass"""
        name = "myTS"
        version = Version.Version("VERSION1", 123, "http://nothing")
        ts = TestSuite.TestSuite(name, version, "DOC")
        
        _myFunc = MyCls()._myFunc
        tc = TestSuite.TestCase(_myFunc.__name__, _myFunc.__doc__, _myFunc, TestSuite.StepType.REGULAR)
        tg = TestSuite.TestCaseGroup("Group", "GroupDoc")
        tg.addTestCase(tc)
        ts.addTestCaseGroup(tg)
        tr = TestSuite.TestSuiteRunner(ts)
        fut = tr.loadSuite()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        fut = tr.run()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        
        self.assertEqual(res.numTotal, 1)
        self.assertEqual(res.numGood, 1)
        self.assertEqual(res.numFails, 0)
        self.assertEqual(res.numErrors, 0)
        self.assertEqual(res.numSkips, 0)
        self.assertEqual(res.suite.values.getValue("SUCCESS"), 1)
    
    def test_param(self):
        """Test a pass"""
        name = "myTS"
        version = Version.Version("VERSION1", 123, "http://nothing")
        myParams = {}
        myParams["TEST_PARAM"] = 10
        ts = TestSuite.TestSuite(name, version, "DOC", params=myParams)
        
        _myFunc = MyCls()._myFunc
        tc = TestSuite.TestCase(_myFunc.__name__, _myFunc.__doc__, _myFunc, TestSuite.StepType.REGULAR)
        tg = TestSuite.TestCaseGroup("Group", "GroupDoc")
        tg.addTestCase(tc)
        ts.addTestCaseGroup(tg)
        tr = TestSuite.TestSuiteRunner(ts)
        fut = tr.loadSuite()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        fut = tr.run()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        
        self.assertEqual(res.numTotal, 1)
        self.assertEqual(res.numGood, 1)
        self.assertEqual(res.numFails, 0)
        self.assertEqual(res.numErrors, 0)
        self.assertEqual(res.numSkips, 0)
        self.assertEqual(res.suite.values.getValue("SUCCESS"), 1)
    
    def test_skip(self):
        """Test a skip"""
        name = "myTS"
        version = Version.Version("VERSION1", 123, "http://nothing")
        ts = TestSuite.TestSuite(name, version, "DOC")
        
        _myFunc = MyCls()._mySkipFunc
        tc = TestSuite.TestCase(_myFunc.__name__, _myFunc.__doc__, _myFunc, TestSuite.StepType.REGULAR)
        tg = TestSuite.TestCaseGroup("Group", "GroupDoc")
        tg.addTestCase(tc)
        ts.addTestCaseGroup(tg)
        tr = TestSuite.TestSuiteRunner(ts)
        fut = tr.loadSuite()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        fut = tr.run()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        
        self.assertEqual(res.numTotal, 1)
        self.assertEqual(res.numGood, 0)
        self.assertEqual(res.numFails, 0)
        self.assertEqual(res.numErrors, 0)
        self.assertEqual(res.numGood, 0)
        self.assertEqual(res.numSkips, 1)

    def test_fail(self):
        """Test a fail"""
        name = "myTS"
        version = Version.Version("VERSION1", 123, "http://nothing")
        ts = TestSuite.TestSuite(name, version, "DOC")
        
        _myFunc = MyCls()._myFailFunc
        tc = TestSuite.TestCase(_myFunc.__name__, _myFunc.__doc__, _myFunc, TestSuite.StepType.REGULAR)
        tg = TestSuite.TestCaseGroup("Group", "GroupDoc")
        tg.addTestCase(tc)
        ts.addTestCaseGroup(tg)
        tr = TestSuite.TestSuiteRunner(ts)
        fut = tr.loadSuite()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        fut = tr.run()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        
        self.assertEqual(res.numTotal, 1)
        self.assertEqual(res.numGood, 0)
        self.assertEqual(res.numFails, 1)
        self.assertEqual(res.numErrors, 0)
        self.assertEqual(res.numGood, 0)
        self.assertEqual(res.numSkips, 0)
        self.assertEqual(res.suite.values.getValue("SUCCESS"), 0)
        
    def test_error(self):
        """Test an exception"""
        name = "myTS"
        version = Version.Version("VERSION1", 123, "http://nothing")
        ts = TestSuite.TestSuite(name, version, "DOC")
        
        _myFunc = MyCls()._myExceptionFunc
        tc = TestSuite.TestCase(_myFunc.__name__, _myFunc.__doc__, _myFunc, TestSuite.StepType.REGULAR)
        tg = TestSuite.TestCaseGroup("Group", "GroupDoc")
        tg.addTestCase(tc)
        ts.addTestCaseGroup(tg)
        tr = TestSuite.TestSuiteRunner(ts)
        fut = tr.loadSuite()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        fut = tr.run()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        
        self.assertEqual(res.numTotal, 1)
        self.assertEqual(res.numGood, 0)
        self.assertEqual(res.numFails, 0)
        self.assertEqual(res.numErrors, 1)
        self.assertEqual(res.numGood, 0)
        self.assertEqual(res.numSkips, 0)
        self.assertEqual(res.suite.values.getValue("SUCCESS"), 0)
        
    def test_values(self):
        """test values"""
        name = "myTS"
        version = Version.Version("VERSION1", 123, "http://nothing")
        ts = TestSuite.TestSuite(name, version, "DOC")
        
        _myFunc = MyCls()._myFunc
        tc = TestSuite.TestCase(_myFunc.__name__, _myFunc.__doc__, _myFunc, TestSuite.StepType.REGULAR)
        tg = TestSuite.TestCaseGroup("Group", "GroupDoc")
        tg.addTestCase(tc)
        ts.addTestCaseGroup(tg)
        tr = TestSuite.TestSuiteRunner(ts)
        fut = tr.loadSuite()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        fut = tr.run()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        
        self.assertEqual(res.suite.values.getValue("VERSION"), version.toFullString())
        self.assertEqual(res.suite.values.getValue("SUCCESS"), 1)
        
    def test_custom_values(self):
        """test custom values"""
        name = "myTS"
        version = Version.Version("VERSION1", 123, "http://nothing")
        atts = MyValues()
        
        ts = TestSuite.TestSuite(name, version, "DOC", params=None, values=atts)
        
        _myFunc = MyCls()._myCustomVals
        tc = TestSuite.TestCase(_myFunc.__name__, _myFunc.__doc__, _myFunc, TestSuite.StepType.REGULAR)
        tg = TestSuite.TestCaseGroup("Group", "GroupDoc")
        tg.addTestCase(tc)
        ts.addTestCaseGroup(tg)
        tr = TestSuite.TestSuiteRunner(ts)
        fut = tr.loadSuite()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        fut = tr.run()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        
        self.assertEqual(res.suite.values.getValue("VERSION"), version.toFullString())
        self.assertEqual(res.suite.values.getValue("SUCCESS"), 1)
        self.assertEqual(res.suite.values.getValue("MY_VAL"), "hello")
        
        #run a different test, values have to be reset        
        ts = TestSuite.TestSuite(name, version, "DOC", params=None, values=atts)
        _myFunc = MyCls()._myFunc
        tc = TestSuite.TestCase(_myFunc.__name__, _myFunc.__doc__, _myFunc, TestSuite.StepType.REGULAR)
        tg = TestSuite.TestCaseGroup("Group", "GroupDoc")
        tg.addTestCase(tc)
        ts.addTestCaseGroup(tg)
        tr = TestSuite.TestSuiteRunner(ts)
        fut = tr.loadSuite()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        fut = tr.run()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        
        self.assertEqual(res.suite.values.getValue("VERSION"), version.toFullString())
        self.assertEqual(res.suite.values.getValue("SUCCESS"), 1)
        self.assertEqual(res.suite.values.getValue("MY_VAL"), None)
        
    def test_dynamic_tg_add(self):
        """Test dynamic addition of test cases"""
        name = "myTS"
        version = Version.Version("VERSION1", 123, "http://nothing")
        ts = TestSuite.TestSuite(name, version, "DOC")
        
        _myFunc = MyCls()._myAddTestGroup
        tc = TestSuite.TestCase(_myFunc.__name__, _myFunc.__doc__, _myFunc, TestSuite.StepType.SETUP)
        tg = TestSuite.TestCaseGroup("Group", "GroupDoc")
        tg.addTestCase(tc)
        ts.addTestCaseGroup(tg)
        tr = TestSuite.TestSuiteRunner(ts)
        fut = tr.loadSuite()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        fut = tr.run()
        res = fut.result(timeout=1)
        self.assertEqual(fut.exception(), None)
        
        self.assertEqual(res.numTotal, 2)
        self.assertEqual(res.numGood, 2)
        self.assertEqual(res.numFails, 0)
        self.assertEqual(res.numErrors, 0)
        self.assertEqual(res.numSkips, 0)
        self.assertEqual(res.suite.values.getValue("SUCCESS"), 1)
        self.assertNotEqual(res.stepResults[0].case.func, res.stepResults[1].case.func)
        
if __name__ == '__main__':
    unittest.main()