# -*- coding: utf-8 -*-
import rpyc
import sys
import time
from rpyc.utils.server import ThreadPoolServer
from .. import debug, info, warn, error
from .task_queue import Task, task_queue, result_dict
import json
import uuid


class TaskScheduler(rpyc.Service):
    rpyc_conn = None

    def on_connect(self, conn):
        info("connect~! {}".format(conn))
        self.task_queue = task_queue

    def on_disconnect(self, conn):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        debug("disconn :{}".format(conn))

    # 对于服务端来说， 只有以"exposed_"打头的方法才能被客户端调用，所以要提供给客户端的方法都得加"exposed_"
    def exposed_put_one_task(self, priority, url, kwargs):
        the_task_id = str(uuid.uuid1())
        the_task = Task(time.time(), the_task_id, priority, url, json.loads(kwargs))
        self.task_queue.put(the_task)
        return json.dumps({'id': the_task_id})

    # 对于服务端来说， 只有以"exposed_"打头的方法才能被客户端调用，所以要提供给客户端的方法都得加"exposed_"
    def exposed_get_one_task_result(self, task_id):
        ret = result_dict.get(task_id)
        if ret is None:
            debug("没有获取到 {}".format(task_id))
            return None
        else:
            result = {'result': None}
            if ret.result is None:
                debug("任务:{},返回了None".format(task_id))
                result['result'] = None
            elif isinstance(ret.result, dict) or isinstance(ret.result, str):
                result['result'] = ret.result
            else:
                warn("未知的返回对象:{}".format(ret.result))
            try:
                result = json.dumps(result)
            except Exception as e:
                warn("处理task {} 的返回内容出错::{}".format(task_id, e.message))
            del (result_dict[task_id])

            return result

    @classmethod
    def send_one_task(cls, priority, url, kwargs, max_try=3):
        """
        触发后台任务进程执行一个任务
        :param priority: int, 任务的优先级,越大优先级越高.
        :param url: string, 需要触发的任务的url.
        :param kwargs: dict, 需要发送的参数字典.
        :param max_try: int, 最大尝试次数(避免偶然性出错).
        :return: json, 任务uuid
        """
        import rpyc
        try_time = max_try
        try:
            if cls.rpyc_conn is None:
                cls.rpyc_conn = rpyc.connect('127.0.0.1', 50188, config={"allow_public_attrs": True})
            ret = json.loads(cls.rpyc_conn.root.put_one_task(priority=priority, url=url, kwargs=json.dumps(kwargs)))
            debug("运行返回:{}".format(ret))
            return ret
        except Exception as e:
            if try_time > 0:
                time.sleep(1)
                debug("出现异常,重试:", e)
                return cls.send_one_task(priority, url, kwargs, try_time - 1)
            else:
                error("try_time {t} is over get exception again".format(t=try_time), e)
                return None

    @classmethod
    def send_task_get_result(cls, priority, url, kwargs, max_try=3, max_timeout=120):
        ret = cls.send_one_task(priority, url, kwargs, max_try)
        if ret:
            result = cls.get_one_result(ret.get('id'), max_timeout)
            debug("请求任务 url:{}, params:{}\n返回结果:{}".format(url, kwargs, result))
            return result
        else:
            warn("无法发送任务 url:{}".format(url))
            return '__mark_unable_to_send_task_url__'

    @classmethod
    def get_one_result(cls, task_id, max_try=3):
        import rpyc
        if cls.rpyc_conn is None:
            cls.rpyc_conn = rpyc.connect('127.0.0.1', 50188, config={"allow_public_attrs": True})
        try_time = max_try
        try:
            ret_result = cls.rpyc_conn.root.get_one_task_result(task_id=task_id)
            debug("get_one_result ret:{}".format(ret_result))
            # 返回为None 以及网络异常,都会抛异常,都认为是没有取到结果,可以重试
            ret = json.loads(ret_result)
            debug("运行返回:{}".format(ret))
            return ret.get('result')
        except Exception as e:
            if try_time > 0:
                time.sleep(1)
                debug("出现异常,重试: {}".format(try_time), e)
                return cls.get_one_result(task_id, try_time - 1)
            else:
                warn("try_time {t} is over get exception again".format(t=try_time), e)
                return None

    @staticmethod
    def run_service():
        debug("start TaskScheduler service")
        from .task_worker import TaskWorker
        for w_id in range(10):
            wk = TaskWorker(w_id, task_queue)
            wk.setDaemon(True)
            wk.start()
        the_server = ThreadPoolServer(TaskScheduler, hostname='localhost', nbThreads=5, port=50188,
                                      auto_register=False)
        the_server.start()
