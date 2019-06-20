import sys
from openProduction.suite.TestSuite import TestSuiteRunner, ExecutionResult, TestSuiteIO
from openProduction.common import misc

class IOHandlerCli:
    def __init__(self):
        pass
    
    def queryYesNo(self, msg, timeout=10):
        rv = misc.queryYesNo(msg)
        if rv:
            return TestSuiteIO.IOAnswer.YES
        else:
            return TestSuiteIO.IOAnswer.NO
        
    def message(self, msg):
        print(msg)

class TestSuiteCliRunner:
    
    def __init__(self, testSuite=None, testSuiteRunner=None):
        if testSuiteRunner == None:
            self._testSuiteRunner = TestSuiteRunner(testSuite)                
        else:
            self._testSuiteRunner = testSuiteRunner
        self._testSuiteRunner.sequenceStart.connect(self._onSequenceStart)
        self._testSuiteRunner.sequenceComplete.connect(self._onSequenceComplete)
        self._testSuiteRunner.stepStart.connect(self._onStepStart)
        self._testSuiteRunner.stepComplete.connect(self._onStepComplete)
        
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
        
        state = str(state)
        print("======================================================================")
        print("= STAGE %s complete"%(state) + " "*(52-len(state)) + "=")
        print("======================================================================")
        
    def _reportErrors(self, suiteResult):
        for res in suiteResult.stepResults:
            if res.result == ExecutionResult.EXCEPTION:
                failStr = "ERROR"
            elif res.result == ExecutionResult.FAIL:
                failStr = "FAIL"
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
        if numFail != 0 or numError != 0:
            overall = preStr + "FAILED (failures=%d, errors=%d, skip=%d, ok=%d)"%(numFail,
                              numError, numSkip, numGood)
        else:
            overall = preStr + "OK (failures=%d, errors=%d, skip=%d, ok=%d)"%(numFail,
                              numError, numSkip, numGood)
        print(overall)
    
    def _onSequenceStart(self, state):
        state = str(state)
        print("======================================================================")
        print("= Starting STAGE %s"%(state) + " "*(52-len(state)) + "=")
        print("======================================================================")
    
    def _onStepStart(self, state, testCase, idx, numCases):
        sys.stdout.write(testCase.getFullName() + "(%s): ... "%testCase.doc)
    
    def _onStepComplete(self, state, stepRes, idx, numCases):
        if stepRes.result == ExecutionResult.EXCEPTION:
            resStr = "Exception"
        elif stepRes.result == ExecutionResult.FAIL:
            resStr = "Failure"
        elif stepRes.result == ExecutionResult.SUCCESS:
            resStr = "Ok"
        elif stepRes.result == ExecutionResult.SKIP:
            resStr = "Skip"
        else:
            resStr = str(stepRes.result)
            
        sys.stdout.write(resStr + "\n")
