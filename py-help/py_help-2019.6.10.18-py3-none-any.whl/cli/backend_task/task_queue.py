# -*- coding: utf-8 -*-

import Queue
import time
from .. import debug, info, warn, error
import threading

# 创建全局ThreadLocal对象:
running_task_local = threading.local()

# 结果存储的字典,key是任务的uuid
result_dict = {}

# 任务的队列
task_queue = Queue.PriorityQueue()


class Task(object):

    def __init__(self, start_time, uuid, priority, url, kwargs):
        self.priority = priority
        self.url = url
        self.kwargs = kwargs
        self.start_time = start_time
        self.task_id = uuid
        self.result = None
        return

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)

    def __repr__(self):
        return "job:[{}]=>{}".format(self.priority, self.kwargs)

    @staticmethod
    def clear_result_dict():
        if len(result_dict) > 100:
            debug("剩余结果超过100,尝试清理超时的结果")
            need_delete = []
            for task_id, task in result_dict.items():
                # 这里认为超过20分钟就超时了,可以安全清理掉了
                if task.start_time + 1200 < time.time():
                    need_delete.append(task_id)
            info("需要清理:{}".format(need_delete))
            for task_id in need_delete:
                try:
                    del (result_dict[task_id])
                except Exception as ex:
                    warn("这里可能是其他地方又刚刚好来拿结果了 [{}],没有加锁,直接一条日志拉倒".format(task_id), ex)

    def do_task(self):
        debug("开始执行任务:{}".format(self.task_id))
        from ..router import router
        running_task_local.task = self
        if not self.url.startswith('/'):
            self.url = "/{}".format(self.url)
        route = router.match_rule(self.url)
        handler = route.get('handler')
        self.result = handler(**self.kwargs)
        debug("跑完返回 {} :{}".format(self.url, self.result))
        # 搞完把自己挂到结果字典里
        result_dict[self.task_id] = self
        self.clear_result_dict()
        running_task_local.task = None
