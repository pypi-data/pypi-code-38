import sys
import sad
import logManager

class ErrorHandler:
    _errorList = {}
    _errorHandlerName = ""

    def __init__(self, name):
        self._errorList = {}
        self._errorHandlerName = name

    def addError(self, error, errorType = sad._NORMAL_ERROR_):
        if errorType not in self._errorList:
            self._errorList[errorType] = []
        self._errorList[errorType].append(error)

    def handle(self):
        terminate = False


        for typeOfError, errors in self._errorList.iteritems():
            if(typeOfError == sad._CRITICAL_ERROR_):
                terminate = True
            for error in errors:
                logManager.print_all(self._errorHandlerName + ": " + error)
        self._errorList = {}
        if terminate:
            logManager.print_all(self._errorHandlerName + ": CRITICAL ERROR")
            logManager.print_all(self._errorHandlerName + ": Terminate execution")
            sys.exit()
