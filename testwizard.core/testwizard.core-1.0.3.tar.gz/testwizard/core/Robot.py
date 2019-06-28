import os.path
import http.client
import json
import datetime
import time
import sys

from testwizard.core.Session import Session

class Robot:
    def __init__(self, cmdArguments):
        self.url = "localhost:8500"
        self.args = cmdArguments
        self.metadata = self.readSideCarFile(self.args)
        if not 'outputFolder' in self.metadata:
            self.metadata["outputFolder"] = self.constructOutputFolder()

        self.metadata["languageId"] = "Python"
        self.metadata["ScriptFilePath"] = self.args.scriptPath

    def createTestRun(self):
        #requestObj = '{"languageId": "Python","tester":"' + self.metadata['tester'] +'","parameters":' + json.dumps(self.metadata['parameters']) + ',"resources": '+ json.dumps(self.metadata['resources']) +',"outputFolder":"' +self.metadata['outputFolder']  +'"}'
        jsonRequest = json.dumps(self.metadata)
        print(jsonRequest)
        response = self.post("/api/v2/testruns", jsonRequest, "Error creating session")

        testRun = json.loads(response.read())
        return testRun["id"]
    
    def createSession(self, testRunId):
        if testRunId == "":
            testRunId = self.createTestRun()
        session = Session(self, testRunId)
       
        return session

    def throwHttpRequestError(self, httpRequest, message):
        if httpRequest.status == 0:
            message += ": Could not connect to robot"
            raise TestSystemError(message)
        elif httpRequest.status == 500:
            errorObj = json.loads(httpRequest.read())
            if("message" in errorObj):
                message += ": " + errorObj["message"]
            if("exceptionMessage" in errorObj):
                message += ": " + errorObj["exceptionMessage"]
            if(self.isSytemException(errorObj)):
                raise TestSystemError(message)
        elif httpRequest.status == 409:
            message += ": All executors are busy"
            raise TestSystemError(message)
        elif httpRequest.reason:
            errorObj = json.loads(httpRequest.read())
            if("message" in errorObj):
                message += ": " + errorObj["message"]
            if("exceptionMessage" in errorObj):
                message += ": " + errorObj["exceptionMessage"]
        raise Exception(message)

    def isSytemException(self, ex):
        return ex["exceptionType"] == "TestWizard.Automation.Extensibility.Exceptions.TestSystemException"    
    def constructOutputFolder(self):
        strDate = datetime.datetime.now().isoformat()
        timestr = time.strftime("%Y%m%d-%H%M%S")
        strDate.replace("-", "")
        strDate.replace(":", "")
        strDate.replace(".", "")
        return os.getcwd() + "/Runs/" + os.path.splitext(self.args.fileName)[0] + timestr

    def readSideCarFile(self, args):
        if args.sidecar is not None:
            filePath = args.sidecar
        else:
            filePath = os.path.splitext(args.fileName)[0] + ".json"
        if os.path.isfile(filePath):
            with open(filePath) as data_file:
                data = json.load(data_file)
        else:
            raise Exception("Sidecar file: " + filePath + " does not exist")
        return data

    def get(self, relativeUrl, errorMessagePrefix):
        return self.send("GET", relativeUrl, None,  errorMessagePrefix)

    def post(self, relativeUrl, requestObj, errorMessagePrefix):
        return self.send("POST", relativeUrl, requestObj, errorMessagePrefix)

    def put(self, relativeUrl, requestObj, errorMessagePrefix):
        return self.send("PUT", relativeUrl, requestObj, errorMessagePrefix)

    def delete(self, relativeUrl, requestObj, errorMessagePrefix):
        return self.send("DELETE", relativeUrl, requestObj, errorMessagePrefix)    

    def send(self, method, relativeUrl, requestBody, errorMessagePrefix):

        headers = {"Content-Type": "application/json;charset=UTF-8"}
        conn = http.client.HTTPConnection(self.url)
        try:
            conn.request(method, relativeUrl, requestBody, headers)
        except:
            raise Exception("Could not connect to robot")
        response = conn.getresponse()
        if response.status!= 200:
            self.throwHttpRequestError(response, errorMessagePrefix)
        
        return response

    def checkTestRunId(self, testRunId):
        return self.send("GET", "/api/v2/testruns/" + testRunId, None, "Session with testrunid" + testRunId + " does not exist")

    def dispose(self):
        self.disposed = True
    
    def checkIsDisposed(self):
        if(self.disposed):
            raise Exception("Cannot access a disposed object.")

class TestSystemError(Exception):
    pass