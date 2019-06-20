from openProduction.suite import TestSuite, TestClass
from openProduction.common import misc
import glob
import os
from importlib.machinery import SourceFileLoader
import logging


class TestGroupLoaderClass:
    
    def __init__(self, inst):
        if isinstance(inst, TestClass.TestClass):
            self._tcInst = inst
        else:
            raise RuntimeError("Test class has to be of type "+
                               "openProduction.suite.TestClass.TestClass")
    
    def discover(self, patternRegular="step_", 
                 patternSetup = "setup_", patternTearDown = "teardown_",
                 patternLoad = "load_", patternUnload = "unload_"):
        className = self._tcInst.__class__.__name__
        classDoc = self._tcInst.__class__.__doc__
        
        tcg = TestSuite.TestCaseGroup(className, classDoc, self._tcInst)
        for val in dir(self._tcInst):
            if val.find(patternRegular) == 0:
                typ = TestSuite.StepType.REGULAR
            elif val.find(patternSetup) == 0:
                typ = TestSuite.StepType.SETUP
            elif val.find(patternTearDown) == 0:
                typ = TestSuite.StepType.TEARDOWN
            elif val.find(patternLoad) == 0:
                typ = TestSuite.StepType.LOAD
            elif val.find(patternUnload) == 0:
                typ = TestSuite.StepType.UNLOAD
            else:
                typ = None
                
            if typ != None:
                
                methodName = val
                func = getattr(self._tcInst, val)
                doc = func.__doc__
                hint = TestSuite.InstallHints()
                tc = TestSuite.TestCase(methodName, doc, func, typ, hint)
                tcg.addTestCase(tc)
        return tcg
    
class TestDirectoryLoader:
    
    def __init__(self, directory):
        self.logger = logging.getLogger(misc.getAppName())
        self.dir = directory
        
    def discover(self, ctor, pattern=["hook_*.py"], testClass=TestClass.TestClass,
                 patternRegular="step_", patternSetup = "setup_",
                 patternTearDown = "teardown_", patternLoad = "load_",
                 patternUnload = "unload_", dontConstruct=False):
        filesGrabbed = []
        for files in pattern:
            join = os.path.join(self.dir, files)
            filesGrabbed.extend(glob.glob(join))
        
        tgs = []
        for file in filesGrabbed:
            self.logger.info("discoverying file %s for TestClasses"%file)
            loader = TestClassLoader(file)
            tgs.extend(loader.discover(ctor, testClass, patternRegular, patternSetup,
                 patternTearDown, patternLoad, patternUnload, dontConstruct))
            
        return tgs
    
class TestClassLoader:
    
    def __init__(self, fname):
        self.fname = fname
        
    def discover(self, ctor, testClass=TestClass.TestClass,
                 patternRegular="step_", patternSetup = "setup_",
                 patternTearDown = "teardown_", patternLoad = "load_",
                 patternUnload = "unload_", dontConstruct=False):
        testClasses = []
        f = os.path.splitext(os.path.split(self.fname)[-1])[0]
        mod = SourceFileLoader("TestClassLoader_%s"%f, self.fname).load_module()
        classes = dir(mod)
        for cla in classes:
            claObj = getattr(mod, cla)
            try:
                if issubclass(claObj, testClass):
                    testClasses.append(claObj)
            except:
                pass
            
        if dontConstruct:
            return testClasses
        
        tgs = []
        objs = []
        for cla in testClasses:
            objs.append(cla(ctor))
            
        for obj in objs:
            loader = TestGroupLoaderClass(obj)
            tgs.append(loader.discover(patternRegular, patternSetup, patternTearDown, patternLoad, patternUnload))
            
        return tgs
            
class TestModuleLoader:
    
    def __init__(self, module):
        self.module = module
        
    def discover(self, ctor, testClass=TestClass.TestClass,
                 patternRegular="step_", patternSetup = "setup_",
                 patternTearDown = "teardown_", patternLoad = "load_",
                 patternUnload = "unload_", dontConstruct=False):
        testClasses = []

        mod = self.module
        classes = dir(mod)
        for cla in classes:
            claObj = getattr(mod, cla)
            try:
                if issubclass(claObj, testClass):
                    testClasses.append(claObj)
            except:
                pass
            
        if dontConstruct:
            return testClasses
        
        tgs = []
        objs = []
        for cla in testClasses:
            objs.append(cla(ctor))
            
        for obj in objs:
            loader = TestGroupLoaderClass(obj)
            tgs.append(loader.discover(patternRegular, patternSetup, patternTearDown, patternLoad, patternUnload))
            
        return tgs    
