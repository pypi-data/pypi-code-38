from geocelery._.tasks import Function, MapReduce, State, BatchFunction, TaskNotFound
from geocelery._.application import TaskType

__all__ = [
    "Function", "MapReduce", "State", "TaskType", "BatchFunction", "DuplicateResult", "RetryResult", "FinalResult", "TaskNotFound"
]

class FinalResult:
    def __init__(self, taskid, celery_rst):
        self._id = taskid
        self._rst = celery_rst

    def getResult(self):
        return self._rst

    def getID(self):
        return self._id

    def __repr__(self):
        return str(self._rst)

class DuplicateResult:
    '''
    重复任务的结果
    '''
    def __init__(self, taskid):
        self.taskid = taskid

    def __repr__(self):
        return "DUPLICATE"

    def __str__(self):
        return "DUPLICATE"

    def __unicode__(self):
        return u"DUPLICATE"


class RetryResult:
    '''
    重试之后依然失败的结果
    '''
    def __init__(self, taskid):
        self.taskid = taskid

    def __repr__(self):
        return "RETRY"

    def __str__(self):
        return "RETRY"

    def __unicode__(self):
        return u"RETRY"
