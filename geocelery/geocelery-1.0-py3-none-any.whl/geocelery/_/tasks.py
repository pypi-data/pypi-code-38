import uuid
import time
import inspect
from concurrent.futures import ThreadPoolExecutor
from celery import chord, group
from celery.result import AsyncResult
from celery.states import PENDING, RECEIVED, STARTED, SUCCESS, REVOKED
from geocelery._.application import task_priority, celery_batch, TaskPriority
from geocelery._.application import celery_app, celery_map, celery_reduce, TaskType, celery_function
from geocelery._.tokens import TaskToken, BatchToken
from geocelery._.cookies import MapReduceCookie


class TaskNotFound(Exception):
    '''
    未找到对应的任务
    '''
    pass


class BadFunctionType(Exception):
    '''
    不支持的函数类型
    '''
    pass


class TaskNotSucceed(Exception):
    '''
    任务没有成功
    '''
    pass


def trim_indent(func_text):
    '''
    删除函数定义文本前的缩进
    '''
    func_lines = func_text.split("\n")
    indents = func_lines[0].index("def")
    return "\n".join([func_line[indents:] for func_line in func_lines])


def is_bounded_func(func):
    '''
    判断被调用函数是否是类方法
    '''
    return hasattr(func, '__cls__')



class State:
    '''
    任务状态
    '''
    PENDING = 'PENDING'
    RECEIVED = 'RECEIVED'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    REVOKED = 'REVOKED'
    REJECTED = 'REJECTED'
    RETRY = 'RETRY'
    IGNORED = 'IGNORED'


class Function:
    '''
    普通函数执行类
    '''
    
    @classmethod
    def start(cls, target, args=None, kwargs=None, tasktype=TaskType.B):
        '''
        开始在celery上执行target对应的任务
        :param target: 需要被提交导平台上执行的函数
        :param args: 传到target函数的位置参数
        :param kwargs: 传到target函数的关键字参数
        :param tasktype: 任务类型，默认为普通类型(TaskType.B)
        :return: 当前任务的taskid
        '''
        if not callable(target) or is_bounded_func(target):
            raise BadFunctionType("target:%s must be unbounded function!" % str(target))

        func_name = target.__name__
        func_text = trim_indent(inspect.getsource(target))

        taskid = str(uuid.uuid4())

        hd_id, md_id, lw_id = taskid + ":a", taskid + ":b", taskid + ":c"
        TaskToken.setCeleryids(taskid, [hd_id, md_id, lw_id])

        priorities = task_priority(tasktype)

        celery_function.apply_async(
            task_id=hd_id,
            exchange="celery",
            routing_key=TaskType.A,
            priority=priorities[0],
            args=[taskid, func_name, func_text, args, kwargs]
        )
        celery_function.apply_async(
            task_id=md_id,
            exchange="celery",
            routing_key=TaskType.B,
            priority=priorities[1],
            args=[taskid, func_name, func_text, args, kwargs]
        )
        celery_function.apply_async(
            task_id=lw_id,
            exchange="celery",
            routing_key=TaskType.C,
            priority=priorities[2],
            args=[taskid, func_name, func_text, args, kwargs]
        )

        return taskid

    @classmethod
    def stop(cls, taskid):
        '''
        终止当前任务
        成功返回True，否则返回False
        '''
        taskids = TaskToken.getCeleryids(taskid)
        for taskid in taskids:
            celery_app.control.revoke(taskid, terminate=True)
        TaskToken.removeAll(taskid)
        return True

    @classmethod
    def status(cls, taskid):
        '''
        返回任务状态
        '''
        taskids = TaskToken.getCeleryids(taskid)
        if not taskids:
            return None
        taskid = taskids[0]
        async_rst = AsyncResult(taskid)
        return async_rst.status

    @classmethod
    def result(cls, taskid, timeout=None):
        '''
        返回任务结果
        '''
        timeout = timeout or 3600*24*7

        while timeout > 0:
            taskids = TaskToken.getCeleryids(taskid)
            if not taskids:
                return None

            if len(taskids) > 1:
                time.sleep(1)
                timeout = timeout - 1
                continue

            celery_rst = AsyncResult(taskids[0], app=celery_app)
            asyrst = celery_rst.get(timeout=timeout)
            return asyrst.getResult()

        raise TimeoutError()



class BatchFunction:
    '''
    批量任务提交接口
    '''
    @classmethod
    def start(cls, target, dataset, tasktype=TaskType.B):
        '''

        :param target:
        :param dataset:
        :param tasktype:
        :return:
        '''
        if not callable(target) or is_bounded_func(target):
            raise BadFunctionType("target:%s must be unbounded function!" % str(target))

        func_name = target.__name__
        func_text = trim_indent(inspect.getsource(target))

        taskid = str(uuid.uuid4())

        celery_batch.apply_async(
            exchange="celery",
            routing_key=tasktype,
            priority=TaskPriority.HIGH,
            args=[taskid, tasktype, func_name, func_text, dataset]
        )

        BatchToken.set_totals(taskid, len(dataset))

        return taskid


    @classmethod
    def status(cls, taskid):
        '''
        批量任务的状态：如果是STARTED，会同时返回进度
        '''
        if BatchToken.check_revoked_token(taskid):
            return REVOKED

        celeryid = BatchToken.get_recent_celeryid(taskid)
        if not celeryid:
            return PENDING

        celery_status = AsyncResult(celeryid).status
        if celery_status != STARTED and celery_status != SUCCESS:
            return celery_status

        nums = BatchToken.get_finished_count(taskid) or 0
        totals = BatchToken.get_totals(taskid)
        if nums < totals:
            return STARTED + ":" + str(nums) + "/" + str(totals)

        return SUCCESS


    @classmethod
    def stop(cls, taskid):
        '''
        终止taskdi对应的任务
        '''
        BatchToken.reset_token(taskid)


class MapReduce:
    '''
    map/reduce任务类型
    '''

    @classmethod
    def start(cls, dataset, map_func, reduce_func, tasktype=TaskType.B, ignore_error=False):
        '''
        启动map/reduce任务
        :param dataset: 待处理的数据集(数组/Array)
        :param map_func: map函数，参数是dataset中的一个data
        :param reduce_func: reduce函数，参数是所有map_func返回的结果的集合(数组/Array)
        :param tasktype: 任务类型，默认为B类型
        :param ignore_error: 是否忽略map错误
        :return: 返回任务标识taskid
        '''
        if not callable(map_func) or is_bounded_func(map_func):
            raise BadFunctionType("map_func:%s must be unbounded function!" % map_func.__name__)

        if not callable(reduce_func) or is_bounded_func(reduce_func):
            raise BadFunctionType("reduce_func:%s must be unbounded function!" % reduce_func.__name__)

        map_func_name = map_func.__name__
        map_func_text = trim_indent(inspect.getsource(map_func))

        reduce_func_name = reduce_func.__name__
        reduce_func_text = trim_indent(inspect.getsource(reduce_func))

        priorities = task_priority(tasktype)

        taskid = str(uuid.uuid4())

        map_tasks = []
        map_taskids = []
        map_celeryids = {}


        def _map_task(taskid, idx, ignore_error, data, map_func_name, map_func_text):
            map_task_id = taskid + ":m-" + str(idx)
            map_hd_id, map_md_id, map_lw_id = "%s-a" % map_task_id, "%s-b" % map_task_id, "%s-c" % map_task_id

            map_celeryids[map_task_id] = [map_hd_id, map_md_id, map_lw_id]

            map_taskids.extend([map_hd_id, map_md_id, map_lw_id])

            h_map_task = celery_map.signature(
                (taskid, map_task_id, ignore_error, data, map_func_name, map_func_text),
                task_id=map_hd_id,
                exchange="celery",
                routing_key=TaskType.A,
                priority=priorities[0]
            )

            m_map_task = celery_map.signature(
                (taskid, map_task_id, ignore_error, data, map_func_name, map_func_text),
                task_id=map_md_id,
                exchange="celery",
                routing_key=TaskType.B,
                priority=priorities[1]
            )

            l_map_task = celery_map.signature(
                (taskid, map_task_id, ignore_error, data, map_func_name, map_func_text),
                task_id=map_lw_id,
                exchange="celery",
                routing_key=TaskType.C,
                priority=priorities[2]
            )

            return h_map_task, m_map_task, l_map_task

        all_futures = []
        with ThreadPoolExecutor(max_workers=100) as executor:
            for idx, data in enumerate(dataset):
                future = executor.submit(_map_task, taskid, idx, ignore_error, data, map_func_name, map_func_text)
                all_futures.append(future)

        for ft in all_futures:
            sub_tasks = ft.result()
            map_tasks.extend(sub_tasks)

        TaskToken.setMassCeleryids(map_celeryids)

        MapReduceCookie.setMapTaskids(taskid, map_taskids)

        reduce_hd_id, reduce_md_id, reduce_lw_id = "%s:r-a" % taskid, "%s:r-b" % taskid, "%s:r-c" % taskid
        TaskToken.setCeleryids(taskid, [reduce_hd_id, reduce_md_id, reduce_lw_id])

        reduce_a = celery_reduce.signature(
            (taskid, reduce_func_name, reduce_func_text),
            task_id=reduce_hd_id,
            exchange="celery",
            routing_key=TaskType.A,
            priority=priorities[0] + 1
        )

        reduce_b = celery_reduce.signature(
            (taskid, reduce_func_name, reduce_func_text),
            task_id=reduce_md_id,
            exchange="celery",
            routing_key=TaskType.B,
            priority=priorities[1] + 1
        )

        reduce_c = celery_reduce.signature(
            (taskid, reduce_func_name, reduce_func_text),
            task_id=reduce_lw_id,
            exchange="celery",
            routing_key=TaskType.C,
            priority=priorities[2] + 1
        )

        r_task = group(reduce_a, reduce_b, reduce_c)

        mr_task = chord(map_tasks, r_task)

        mr_task.apply_async()

        return taskid


    @classmethod
    def status(cls, taskid):
        '''
        任务状态
        '''
        map_celery_id = MapReduceCookie.getMapCeleryid(taskid)
        if map_celery_id:
            map_task = AsyncResult(map_celery_id)
            map_status = map_task.status
            if map_status in [PENDING, RECEIVED, STARTED]:
                return map_status

        red_celery_id = MapReduceCookie.getReduceCeleryid(taskid)
        if not red_celery_id:
            if MapReduceCookie.exists(taskid):
                return PENDING
            return None

        reduce_task = AsyncResult(red_celery_id)
        reduce_status = reduce_task.status
        if reduce_status in [PENDING, RECEIVED]:
            return STARTED
        return reduce_status


    @classmethod
    def result(cls, taskid, timeout=None):
        '''
        返回任务结果
        '''
        timeout = timeout or 3600*24*7

        while timeout > 0:
            reduce_celery_id = MapReduceCookie.getReduceCeleryid(taskid)
            if not reduce_celery_id:
                time.sleep(1)
                timeout = timeout - 1
                if not MapReduceCookie.exists(taskid):
                    raise TaskNotFound()
                continue

            reduce_rst = AsyncResult(reduce_celery_id)
            asyrst = reduce_rst.get(timeout=timeout)
            return asyrst.getResult()

        raise TimeoutError()


    @classmethod
    def stop(cls, taskid):
        '''
        终止任务
        '''
        reduce_taskids = TaskToken.getCeleryids(taskid)
        for taskid in reduce_taskids:
            celery_app.control.revoke(taskid, terminate=True)

        map_taskids = MapReduceCookie.getMapTaskids(taskid)
        for taskid in map_taskids:
            celery_app.control.revoke(taskid, terminate=True)

        MapReduceCookie.remove(taskid)
