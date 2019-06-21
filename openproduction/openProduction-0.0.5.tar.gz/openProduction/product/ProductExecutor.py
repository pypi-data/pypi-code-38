import threading
import logging
from openProduction.common import misc, Signals, Version
from enum import Enum
from openProduction.suite import TestSuite, TestLoader, TestClass, TestSuiteIO
from openProduction.suite.TestSuite import SuiteState
from openProduction.product import ProductExecutorCtor
from concurrent.futures import ThreadPoolExecutor
import os

class HWClass:
    
    def __new__(cls, cla, errMsg, *args, **kwargs):
        cls._inst = None
        instance = super(HWClass, cls).__new__(cls)
        return instance
        
    def __init__(self, cla, errMsg, *args, **kwargs):
        self._cla = cla
        self._args = args
        self._kwargs = kwargs
        self.errMsg = errMsg
        
    def getErrMsg(self):
        return self.errMsg
        
    def construct(self):
        if "initCallback" in self._kwargs:
            cb = self._kwargs["initCallback"]
            self._kwargs.pop("initCallback", None)
        else:
            cb = None
        self._inst = self._cla(*self._args, **self._kwargs)
        
        if cb != None:
            cb(self._inst)
        
        return self._inst
    
    def __setattr__(self, name, value):
        if self._inst != None:
            setattr(self._inst, name, value)
        else:
            self.__dict__[name] = value
    
    def __getattr__(self, name):
        return getattr(self._inst, name)

class HardwareManager:
    def __init__(self):
        self.hwList = []
        
    def add(self, cla, errMsg, *args, **kwargs):
        hw = HWClass(cla, errMsg, *args, **kwargs)
        self.hwList.append(hw)
        return hw
        
    def probe(self):
        ok = True
        desc = ""
        
        for hw in self.hwList:
            try:
                obj = hw.construct()
            except:
                ok = False
                desc = hw.getErrMsg()
                break
            
            if hasattr(obj, "probe"):
                ok, desc = hw.probe()
                if ok == False:
                    break

        return ok, desc

    def stop(self):
        for hw in self.hwList:
            if hasattr(hw, "close"):
                hw.close()

class ProductTrigger(threading.Thread):

    def __init__(self, runner, executor):
        threading.Thread.__init__(self)
        self.executor = executor
        self.hardwareManager = self.executor.hardwareManager
        self.runner = runner
        self.wasStarted = False
        self.runner.sequenceComplete.connect(self.onSequenceComplete)
    
    def onSequenceComplete(self, stepType, result):
        if stepType == SuiteState.LOADING and result.isSuccessful():
            self.startTrigger()
            self.wasStarted = True
        if stepType == SuiteState.UNLOADING and self.wasStarted == True:
            self.stopTrigger()
            
    def startTrigger(self):
        self._stop_event = threading.Event()
        self.start()
        
    def stopTrigger(self):
        self._stop_event.set()
        self.join()
        
class ProductExecutor(TestClass.TestClass):
    
    def __init__(self, ctor):
        super(ProductExecutor, self).__init__()
        if isinstance(ctor, ProductExecutorCtor.ProductExecutorCtor) == False:
            print(type(ctor))
            raise RuntimeError("ctor must be of type openProduction.product.ProductExecutor.ProductExecutorCtor")
        self.params = ctor.params
        self.values = ctor.values
        self.ioHandler = ctor.io
        self.ui = ctor.ui
        if self.ioHandler == None:
            self.ioHandler = TestSuiteIO.BaseIOHandler()
        self.hardwareManager = HardwareManager()
        
    def probe(self):
        return self.hardwareManager.probe()

class ProductRunner:
    
    class RunnerState(Enum):
        INIT = 0
        SETUP = 1
        RUN = 2
        TEARDOWN = 3
    
    def __init__(self, productDir, productName, params, ioHandler=None, ui=None):
        
        self._pool = ThreadPoolExecutor(3)
        
        self.logger = logging.getLogger(misc.getAppName())
        self.triggered = Signals.Signal()
        
        #at this stage, don't construct anything
        self.params = params
        self._ioHandler = ioHandler
        self._ui = ui
        
        self.suite = TestSuite.TestSuite(productName, "", params=self.params, values=None)
        self.suiteRunner = TestSuite.TestSuiteRunner(self.suite, stopOnFail=True, stopOnExcept=True)
        
        self.suiteRunner.sequenceComplete.connect(self._onSequenceComplete)
        
        
        params.setReadOnly(False)
        if "productHookDir" not in params:
            params["productHookDir"] = productDir
        else:
            params["productHookDir"] = os.path.abspath(os.path.join(productDir, params["productHookDir"]))
            
        if "productHookPattern" not in params:
            params["productHookPattern"] = ["hook_*.py"]
        if "productHookRegularPattern" not in params:
            params["productHookRegularPattern"] = "step_"
        if "productHookSetupPattern" not in params:
            params["productHookSetupPattern"] = "setup_"
        if "productHookTearDownPattern" not in params:
            params["productHookTearDownPattern"] = "teardown_"
        if "productHookLoadPattern" not in params:
            params["productHookLoadPattern"] = "load_"
        if "productHookUnloadPattern" not in params:
            params["productHookUnloadPattern"] = "unload_"
        if "skipOpenProductionHooks" in params:
            myFolder = productDir
        else:
            myFolder = os.path.split(os.path.abspath(__file__))[0]
        params.setReadOnly(True)
            
        loader = TestLoader.TestDirectoryLoader(myFolder)
        ctor = ProductExecutorCtor.ProductExecutorCtor(self._ioHandler, self.params, self.suite.values, self._ui)
        tgs = loader.discover(ctor)
        for tg in tgs:
            self.suite.addTestCaseGroup(tg)
        
        self._state = ProductRunner.RunnerState.INIT
                
    def _onNewTrigger(self):
        if self._state == ProductRunner.RunnerState.RUN:
            self.triggered.emit()
            rv = self.suiteRunner.run()
        else:
            self.logger.warning("can't trigger ProductRunner in state %s"%self._state)
            rv= None
            
        return rv
    
    def trigger(self):
        return self._onNewTrigger()
    
    
    def _unloadSuiteAfterErr(self):
        self._loadFuture.result(timeout=10)
        self.unload()
                    
    def _onSequenceComplete(self, executionType, suiteResults):
        if executionType == TestSuite.SuiteState.LOADING:
            self._state = ProductRunner.RunnerState.RUN
            if suiteResults.isSuccessful() == False:                
                self._pool.submit(self._unloadSuiteAfterErr)
        if executionType == TestSuite.SuiteState.UNLOADING:
            self._state = ProductRunner.RunnerState.INIT
    
    def load(self, startTrigger=True, startMonitor=True):
        if self._state == ProductRunner.RunnerState.INIT:
            self._state = ProductRunner.RunnerState.SETUP
            self._loadFuture = self.suiteRunner.loadSuite()
            return self._loadFuture
        else:
            self.logger.warning("can't start ProductRunner in state %s"%self._state)
            return None
        
    def unload(self):
        if self._state == ProductRunner.RunnerState.RUN:
            return self.suiteRunner.unloadSuite()
        else:
            self.logger.warning("can't stop ProductRunner in state %s"%self._state)
            return None
    