# -*- coding: utf-8 -*-
from .. import debug, info, warn, error
import threading


class TaskWorker(threading.Thread):

    def __init__(self, wk_id, queue):
        super(TaskWorker, self).__init__()
        self.worker_id = wk_id
        self.wk_queue = queue
        self.is_start = True

    def run(self):
        debug("start Worker[{}]".format(self.worker_id))
        while self.is_start:
            try:
                one_task = self.wk_queue.get()
                debug("worker:{} 运行任务:{}".format(self.worker_id, one_task))
                one_task.do_task()
            except Exception as e:
                error("处理任务出错::", e)

    def stop(self):
        self.is_start = False
