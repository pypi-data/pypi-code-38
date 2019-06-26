import sys
from openProduction.suite.TestSuite import TestSuiteRunner, ExecutionResult, TestSuiteIO, SuiteState
from openProduction.common import misc
import colorama
colorama.init()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class IOHandlerCli(TestSuiteIO.BaseIOHandler):
    def __init__(self):
        super(IOHandlerCli, self).__init__()
    
    def _queryYesNo(self, title, msg, timeout=10):
        rv = misc.queryYesNo(msg)
        if rv:
            return TestSuiteIO.IOAnswer.YES
        else:
            return TestSuiteIO.IOAnswer.NO
        
    def message(self, msg):
        print(msg)

class TestSuiteCliRunner:
    
    def __init__(self, testSuite=None, testSuiteRunner=None, playSound=True):
        if testSuiteRunner == None:
            self._testSuiteRunner = TestSuiteRunner(testSuite)                
        else:
            self._testSuiteRunner = testSuiteRunner
        self._testSuiteRunner.sequenceStart.connect(self._onSequenceStart)
        self._testSuiteRunner.sequenceComplete.connect(self._onSequenceComplete)
        self._testSuiteRunner.stepStart.connect(self._onStepStart)
        self._testSuiteRunner.stepComplete.connect(self._onStepComplete)
        self._playSound = playSound
        
    def run(self):
        fut = self._testSuiteRunner.start()
        def _onReady(future):
            if future.exception() != None:
                print("Something went wrong")
                print(future.exception())
        fut.add_done_callback(_onReady)
                
    def _onSequenceComplete(self, state, suiteResult):
        self._reportErrors(suiteResult)
        self._reportOverall(suiteResult)
        
        attrs = suiteResult.suite.values
        if len(attrs) > 0:
            print("")
            print("----------------------------------------------------------------------")
            print("The test suite contains the following values:")
            print(attrs)
            print("----------------------------------------------------------------------")
        
        print("======================================================================")
        print("= STAGE %s complete"%(state.name) + " "*(52-len(state.name)) + "=")
        print("======================================================================")
        sys.stdout.flush()
        
        if self._playSound:
            if state == SuiteState.REGULAR:
                ioHandler = TestSuiteIO.BaseIOHandler()
                if suiteResult.isSuccessful() == False:
                    ioHandler.playError()
                else:
                    ioHandler.playSuccess()
        
    def _reportErrors(self, suiteResult):
        for res in suiteResult.stepResults:
            if res.result == ExecutionResult.EXCEPTION:
                failStr = "ERROR"
            elif res.result == ExecutionResult.FAIL:
                failStr = "FAIL"
            elif res.result == ExecutionResult.ABORT:
                failStr = "ABORT"
            else:
                continue
            print("======================================================================")
            print("%s: %s (%s)\n%s"%(failStr, res.case.name, res.case.group.name, res.case.doc))
            print("----------------------------------------------------------------------")
            print(res.msg)
        
    def _reportOverall(self, suiteResult, preStr=""):
        print("----------------------------------------------------------------------")
        dur = suiteResult.executionTime
        numTests = suiteResult.numTotal
        numGood = suiteResult.numGood
        numFail = suiteResult.numFails
        numError = suiteResult.numErrors
        numSkip = suiteResult.numSkips
        print("Ran %d step(s) in %.03f s"%(numTests, dur))
        print("")
        if suiteResult.isSuccessful() == False:
            
            overall = preStr + bcolors.FAIL+"FAILED"+bcolors.ENDC+" (failures=%d, errors=%d, skip=%d, ok=%d)"%(numFail,
                              numError, numSkip, numGood)
        else:
            overall = preStr + bcolors.OKGREEN+"OK"+bcolors.ENDC+" (failures=%d, errors=%d, skip=%d, ok=%d)"%(numFail,
                              numError, numSkip, numGood)
        print(overall)
    
    def _onSequenceStart(self, state):
        state = str(state)
        print("======================================================================")
        print("= Starting STAGE %s"%(state) + " "*(52-len(state)) + "=")
        print("======================================================================")
    
    def _onStepStart(self, state, testCase, idx, numCases):
        sys.stdout.write(testCase.getFullName() + "(%s): ... "%testCase.doc)
        sys.stdout.flush()
    
    def _onStepComplete(self, state, stepRes, idx, numCases):
        if stepRes.result == ExecutionResult.EXCEPTION:
            resStr = "Exception"
        elif stepRes.result == ExecutionResult.FAIL:
            resStr = "Failure"
        elif stepRes.result == ExecutionResult.SUCCESS:
            resStr = "Ok"
        elif stepRes.result == ExecutionResult.SKIP:
            resStr = "Skip"
        elif stepRes.result == ExecutionResult.ABORT:
            resStr = "Abort"
        else:
            resStr = str(stepRes.result)
            
        sys.stdout.write(resStr + "\n")
        sys.stdout.flush()
