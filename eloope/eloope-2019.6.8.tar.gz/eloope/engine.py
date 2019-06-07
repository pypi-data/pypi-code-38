from gevent.pool import Pool

_current_engine = []


class Engine:
    def __init__(self, name='engine', size=50):
        self._name = name
        self._size = size
        self._task_pool = ()
        self._is_run = False
        self._tasks = []

    @property
    def name(self):
        return self._name

    @property
    def is_run(self):
        """运行状态"""
        return self._is_run

    @property
    def task_count(self):
        """任务数量"""
        return len(self._task_pool if self._is_run else self._tasks)

    @property
    def free_count(self):
        """任务池剩余空间"""
        return self._size - self.task_count

    @property
    def task_pool(self):
        """任务池"""
        return (g for g in self._task_pool)

    def run(self):
        from . import logger
        assert not self._is_run, 'Engine object is already running.'
        self._task_pool = Pool(self._size)
        self._is_run = True
        _current_engine.append(self)
        logger.system('Begin')
        for task in self._tasks:
            self._task_pool.spawn(*task)
        self._task_pool.join()
        logger.system('End')
        _current_engine.pop()
        self._task_pool = ()
        self._is_run = False
        self._tasks = []

    def add_task(self, fn, *params):
        """
        添加单个任务
        :param fn: 函数
        :param params: 函数参数
        """
        self._task_pool.spawn(fn, *params) if self._is_run else self._tasks.append((fn, *params))

    def add_tasks(self, fn, param_groups):
        """
        添加多个任务, 同一个函数不同参数
        :param fn: 函数
        :param param_groups: 参数列表
        """
        for param in param_groups:
            self.add_task(fn, *param)


def get_current_engine():
    """获取当前运行的engine"""
    try:
        return _current_engine[-1]
    except IndexError:
        raise RuntimeError('No engine is running.')
