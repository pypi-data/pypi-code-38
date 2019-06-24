from openProduction.product import ProductExecutor, ProductExecutorCtor
from openProduction.suite import TestLoader, TestParams

class ProductSetUp(ProductExecutor.ProductExecutor):
    """Product setup hooks"""
    
    def __init__(self, ctor):
        super(ProductSetUp, self).__init__(ctor)
        
    def load__00050(self, params, values):
        """Executing self tests"""
        import unittest
        import openProduction.tests.suite_test as myTests
        suite = unittest.TestLoader().loadTestsFromModule(myTests)
        results = unittest.TestResult()
#        suite.run(results)
#        results = unittest.TextTestRunner(verbosity=2).run(suite)
        
#        self.assertEqual(results.wasSuccessful(), True)
        
    def install(self, testSuite):
        self.testSuite = testSuite

    def load__00100(self, params, values):
        """Construct product executors"""
        ctor = ProductExecutorCtor.ProductExecutorCtor(self.ioHandler, params, values, self.tempParams, self.ui)
        folder = params["productHookDir"]
        l = TestLoader.TestDirectoryLoader(folder)
        tcg = l.discover(ctor, 
                   pattern=params["productHookPattern"],
                   testClass=ProductExecutor.ProductExecutor,
                   patternRegular=params["productHookRegularPattern"],
                   patternSetup=params["productHookSetupPattern"],
                   patternTearDown=params["productHookTearDownPattern"],
                   patternLoad=params["productHookLoadPattern"],
                   patternUnload=params["productHookUnloadPattern"])
        
        return tcg
        
    def load__00200(self, params, values):
        """Probing product executors"""
        ok, desc = self.hardwareManager.probe()
        self.assertEqual(ok, True, "Probing HW failed, with msg %s"%(desc))
        