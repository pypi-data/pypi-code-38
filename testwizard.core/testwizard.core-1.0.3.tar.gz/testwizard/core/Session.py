
import json
from enum import Enum

from testwizard.core.ResultCodes import ResultCodes

class Session():
    def __init__(self, robot, testRunId):
        self.robot = robot
        self.args = {}
        if(testRunId is None):
            self.testRunId = self.robot.createTestRun()
            self.isSelfManaged = True
        else:
            self.robot.checkTestRunId(testRunId)
            self.testRunId = testRunId
            self.isSelfManaged = False
        self.setResultUrl = "/api/v2/testruns/" + self.testRunId + "/result"
        self.tearDownUrl = "/api/v2/testruns/" + self.testRunId
        self.results = []
        if(self.robot.metadata.get("parameters")):
            for parameter in self.robot.metadata["parameters"]:
                self.args[parameter['name']] = parameter['value']
        self.failCount = 0
        self.errorCount = 0
        self.disposed = False
        self.scriptPath = self.robot.args.scriptPath

    def dispose(self):
        self.disposed = True

        if(len(self.results)>0):
            self.postTestResult(self.results)

        if(self.isSelfManaged):
            self.tearDown()
        
        self.robot = None
        self.results = []

    def checkIsDisposed(self):
        if(self.disposed):
            print("Cannot access a disposed object")
            raise Exception("Cannot access a disposed object.")

    def addPass(self, message):
        self.checkIsDisposed()

        data = {}
        data['result'] = ResultCodes.PASS.value
        data['comment'] = message
        self.results.append(data)

    def addFail(self, message):
        self.checkIsDisposed()

        self.failCount += 1

        data = {}
        data['result'] = ResultCodes.FAIL.value
        data['comment'] = message
        self.results.append(data)

    def addError(self, message):
        self.checkIsDisposed()

        self.errorCount += 1

        data = {}
        data['result'] = ResultCodes.SCRIPTERROR.value
        data['comment'] = message
        self.results.append(data)

    def hasFails(self):
        self.checkIsDisposed()

        return self.failCount > 0

    def hasErrors(self):
        self.checkIsDisposed()

        return self.errorCount > 0

    def setResult(self, result, message):
        self.checkIsDisposed()

        if (result == ResultCodes.FAIL):
            self.failCount += 1
        elif (result == ResultCodes.SCRIPTERROR):
            self.errorCount += 1
        elif (result == ResultCodes.SYSTEMERROR):
            self.errorCount += 1

        data = {}
        data['result'] = result.value
        data['comment'] = message
        tempResult = []
        tempResult.append(data)

        self.postTestResult(tempResult)

    def postTestResult(self, requestObj):
        jsonRequest =  json.dumps(requestObj)
        self.robot.post(self.setResultUrl, jsonRequest, "Error setting test result")

    def tearDown(self):
        self.robot.delete(self.tearDownUrl, None, "Error tearing down session")