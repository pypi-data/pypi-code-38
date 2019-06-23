from ojcrawler.crawlers.config import *
from ojcrawler.crawlers import supports
from queue import Queue
import threading
from time import sleep
import json


def sample_sync_func(data, *args):
    # 多余的对应参数应该在add_task的时候按顺序传入
    # data = {
    #     'status': '各oj对应的状态字符串',
    #     'established': True,  # False, 表明是否是确定的状态，如果是，应该还有额外的信息
    #     'rid': trs[1].contents[0].text.strip(),
    #     'status': trs[1].contents[2].text.strip(),
    #     'time': trs[1].contents[4].text.strip(),
    #     'memory': trs[1].contents[5].text.strip(),
    # }
    json_data = json.dumps(data)
    logger.info("data: " + json_data)


def sample_save_image(image_url, oj_name):
    # 传入一个图片的地址，返回新的地址
    # oj_name 会传入oj自身的名字，方便用来分类
    # 1. 可以将图片保存到本地然后返回静态服务器的地址
    # 2. 可以上传到某图云然后返回图云的地址
    # 3. 也可以直接返回源oj的地址，这样如果不能访问外网就存在风险
    return image_url


class SingletonOJHandle(type):
    # 这个metaclass保证第一属性和第二属性的元组单例
    _map_instance = {}

    def __call__(cls, a, b, *args, **kwargs):
        if (cls, a, b) not in cls._map_instance:
            cls._map_instance[(cls, a, b)] = super().__call__(a, b, *args, **kwargs)
        else:
            logger.warning('you are create a exist oj-handle({}-{}), '
                           'return mapped instead and this will update other attribute.'.format(a, b))
        return cls._map_instance[(cls, a, b)]


class Worker(threading.Thread, metaclass=SingletonOJHandle):
    # 需要保证同一个oj，同一个handle为单例
    def __init__(self, oj_name, handle, password, queue: Queue, image_func, sync_func):
        super().__init__(name='{}-{}'.format(oj_name, handle))
        self.oj = supports[oj_name](handle, password, image_func)
        self.queue = queue
        self.sync_func = sync_func

        # 线程控制相关
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        # # stop的时候存在一个问题，由于中间还需要从queue中获取数据，如果queue已经为空，run函数
        # # 会阻塞在queue.get()函数处，永远无法退出，所以控制器退出的时候需要往queue中push Worker
        # # 个数的None
        #
        # self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False

    # 队列中的信息：
    # pid, source, lang, *args
    # *args, **kwargs和sync_func中保持一致
    def run(self):
        while self.__running.isSet():
            # self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            item = self.queue.get()
            if item:
                # 注意处理cf的pid
                # cf的pid应该为 123A 之类的形式
                # 内部会将其拆分
                source = item[0]
                lang = item[1]
                pid = item[2]
                args = item[3:]
                success, dat = self.oj.submit_code(source, lang, pid)
                if not success:
                    logger.warning('{} - {}'.format(self.oj.oj_name, dat))
                    # 注意如果处理失败，应该再次放入队列
                    # self.queue.put(item)
                    self.sync_func({'status': 'submit failed', 'established': True}, args)
                    continue

                self.sync_func({'status': 'submitted', 'established': False}, args)
                pre_status = 'submitted'
                cnt = 0
                fetch_success = False
                while cnt < RESULT_COUNT:
                    sleep(RESULT_INTERVAL)
                    success, info = self.oj.get_result_by_rid(dat)
                    if success:
                        status = info['status']
                        if status != pre_status:
                            # 注意codeforces
                            established = True
                            for uncertain_status in self.oj.uncertain_result_status:
                                if str(status).lower() in uncertain_status:
                                    established = False
                            if not established:
                                info['established'] = False
                                self.sync_func(info, args)
                                pre_status = status
                            else:
                                info['established'] = True
                                self.sync_func(info, args)
                                fetch_success = True
                                break
                    cnt = cnt + 1

                if not fetch_success:
                    self.sync_func({'status': 'fetch failed', 'established': False}, args)
            self.queue.task_done()
