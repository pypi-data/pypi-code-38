from enum import Enum

class Task:

    class Status(Enum):
        CREATED = 1
        COMPLETED = 2

    class Completed_Status(Enum):
        NOT_COMPLETED = 1
        SUCCESS = 2
        FAIL = 3

    def __init__(self, name, f):
        self._name = name
        self._callable = f
        self._result = None
        self._status = self.Status.CREATED
        self._completed_status = self.Completed_Status.NOT_COMPLETED

    def __call__(self):
        try:
            self._result = self._callable()
            self._completed_status = self.Completed_Status.SUCCESS
        except:
            self._completed_status = self.Completed_Status.FAIL
        self._status = self.Status.COMPLETED

    def getName(self):
        return self._name

    def getResult(self):
        return self._result

    def getStatus(self):
        return self._status

    def getCompletedStatus(self):
        return self._completed_status
