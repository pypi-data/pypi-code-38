# -*- coding: utf-8 -*-
# Created by crazyX on 2018/7/12
from ojcrawler.crawlers import supports
import inspect
import json
from queue import Queue
from ojcrawler.utils import sample_save_image, sample_sync_func, Worker


class Controller(object):

    # 😝不同OJ爬虫的同步状态函数和替换图片url函数已经被抽象为统一的函数
    def __init__(self, sync_func=sample_sync_func, image_func=sample_save_image):
        # 这个函数用来同步状态，必须为sync_func(status, *args, **kwargs) 形式xw
        args = inspect.getfullargspec(sync_func)[0]
        if len(args) < 1 or args[0] != 'data':
            raise ValueError('sync_func的第一个参数必须为data而不是{}, '
                             'sample: sync_func(data, *args, **kwargs)'.format(args[0]))

        args = inspect.getfullargspec(image_func)[0]
        if len(args) != 2:
            raise ValueError('image_func必须为两个参数')
        if args[0] != 'image_url' or args[1] != 'oj_name':
            raise ValueError('image_func的两个参数必须为image_url({})和oj_name({}), '
                             'sample: sample_save_image(image_url, oj_name)'.format(args[0], args[1]))

        self.sync_func = sync_func
        self.image_func = image_func

        self.queues = {}
        # 一个oj可能对应多个worker，{'poj': [instance1, instance2], 'hdu': [instance1]}
        self.workers = {}

        self.static_supports = {}

        for key in supports.keys():
            self.queues[key] = Queue()
            self.workers[key] = []
            self.static_supports[key] = supports[key]('static', 'static', image_func)

    def __del__(self):
        print('正在停止workers')
        self.stop()
        print('停止成功')

    @staticmethod
    def supports():
        return supports.keys()

    def _add_account(self, oj_name, handle, password):
        # 同一个oj重复handle只会采用第一个的配置
        worker = Worker(oj_name, handle, password, self.queues[oj_name], self.image_func, self.sync_func)
        # 可能是已经存在的实例
        if worker not in self.workers[oj_name]:
            self.workers[oj_name].append(worker)
            worker.start()

    def load_accounts_json(self, json_path):
        with open(json_path) as fp:
            json_data = json.load(fp)
        accounts = []
        for oj_name in json_data:
            if oj_name not in supports.keys():
                raise NotImplementedError('oj_name only supports: {}'.format(str(supports.keys())))
            for item in json_data[oj_name]:
                accounts.append((oj_name, item['handle'], item['password']))
        self.init_accounts(accounts)

    def init_accounts(self, accounts):
        # 初始化account信息，注意不能用重复的信息初始化
        # 注意会清空之前的账号信息
        for oj_name, handle, password in accounts:
            if oj_name not in supports.keys():
                raise NotImplementedError('oj_name only supports: {}'.format(str(supports.keys())))

        # 先停止所有的worker
        self.stop()
        # 创建对应的队列集和工作者集
        for key in supports.keys():
            self.queues[key] = Queue()
            self.workers[key] = []
        for oj_name, handle, password in accounts:
            self._add_account(oj_name, handle, password)
        return True

    def add_task(self, oj_name, source, lang, pid, *args):
        if oj_name not in supports.keys():
            raise NotImplementedError('oj_name only supports: {}'.format(str(supports.keys())))
        self.queues[oj_name].put((source, lang, pid, *args))

    def start(self):
        if not self.workers:
            raise RuntimeError('you should init accounts first.')
        for key in self.workers:
            for worker in self.workers[key]:
                worker.setDaemon(True)
                worker.start()

    def pause(self):
        for key in self.workers:
            for worker in self.workers[key]:
                worker.pause()

    def stop(self):

        for key in self.workers:
            for worker in self.workers[key]:
                assert type(worker) == Worker
                worker.stop()

        # for key in self.queues.keys():
        #     cnt = len(self.workers[key])
        #     for i in range(cnt):
        #         self.queues[key].put(None)
        #
        # for key in self.workers:
        #     for worker in self.workers[key]:
        #         worker.join()

        # 清空worker和队列内存
        for queue in self.queues.values():
            with queue.mutex:
                queue.queue.clear()
            del queue
        for key in self.workers:
            for worker in self.workers[key]:
                del worker
        self.queues = {}
        self.workers = {}

    def get_languages(self, oj_name):
        if oj_name not in supports.keys():
            raise NotImplementedError('oj_name only supports: {}'.format(str(supports.keys())))
        return self.static_supports[oj_name].get_languages()

    @staticmethod
    def get_basic_language(oj_name):
        if oj_name not in supports.keys():
            raise NotImplementedError('oj_name only supports: {}'.format(str(supports.keys())))
        # 只考虑三种最基础的语言，用来在比赛当中避免选手根据源语言判断OJ来源
        # c, c++, java
        if oj_name == 'poj':
            return {
                'c': 'GCC',
                'c++': 'G++',
                'c++11': None,
                'java': 'JAVA',
            }
        elif oj_name == 'hdu':
            return {
                'c': 'GCC',
                'c++': 'G++',
                'c++11': 'G++',
                'java': 'JAVA',
            }

        elif oj_name == 'codeforces':
            return {
                'c': 'GNU GCC C11 5.1.0',
                'c++': 'GNU G++11 5.1.0',
                'c++11': 'GNU G++11 5.1.0',
                'java': 'Java 1.8.0_162',
            }

    def get_problem(self, oj_name, pid):
        if oj_name not in supports.keys():
            raise NotImplementedError('oj_name only supports: {}'.format(str(supports.keys())))
        return self.static_supports[oj_name].get_problem(pid)
