from celery import Celery, platforms
from geocelery._.settings import BROKER_URL, RESULT_URL


class TaskType:
    '''
    任务类型： A：高优先级任务； B：普通任务； C：低优先级任务
    '''
    A, B, C = "HIGH_PRIORITY", "MID_PRIORITY", "LOW_PRIORITY"

class TaskPriority:
    '''
    任务优先级：最低0，最高255
    '''
    HIGH, MID, LOW = 30, 20, 10


def task_priority(task_type):
    if task_type == TaskType.A:
        return [TaskPriority.HIGH, TaskPriority.MID, TaskPriority.HIGH]

    if task_type == TaskType.B:
        return [TaskPriority.MID, TaskPriority.HIGH, TaskPriority.LOW]

    if task_type == TaskType.C:
        return [TaskPriority.LOW, TaskPriority.LOW, TaskPriority.MID]


celery_app = Celery('tasks')

platforms.C_FORCE_ROOT = True   #for root user

celery_app.conf.update(
    BROKER_URL=BROKER_URL,
    BROKER_POOL_LIMIT=None,
    CELERYD_SEND_EVENTS=True,
    CELERY_TRACK_STARTED=True,
    CELERYD_PREFETCH_MULTIPLIER=1,
    CELERY_TASK_SERIALIZER='pickle',
    CELERY_RESULT_BACKEND=RESULT_URL,
    CELERY_RESULT_SERIALIZER='pickle',
    CELERY_ACCEPT_CONTENT=['pickle']
)

@celery_app.task(name='tasks.add')
def add(x, y):
    return x + y

@celery_app.task(name='tasks.celery_batch')
def celery_batch(taskid, tasktype, func_name, func_text, dataset):
    pass

@celery_app.task(bind=True, name='tasks.exec_function')
def celery_function(self, taskid, func_name, func_text, *args, **kwargs):
    pass


@celery_app.task(bind=True, name='tasks.celery_map')
def celery_map(self, taskid, m_taskid, ignore_error, data, func_name, func_text):
    pass

@celery_app.task(bind=True, name='tasks.celery_reduce')
def celery_reduce(self, results, taskid, func_name, func_text):
    pass
        
