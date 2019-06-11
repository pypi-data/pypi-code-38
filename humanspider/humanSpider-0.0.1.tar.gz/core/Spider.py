import traceback
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from core.downloader.HttpDownloader import HttpDownloader
from core.Request import Request
from core.scheduler.QueueScheduler import QueueScheduler
from core.common import logger


class Spider(object):
    def __init__(self):
        self.pageProcessor = None  # 页面处理器
        self._THREAD_POOL_SIZE = 1  # 默认线程池大小
        self.site = None  # 初始化爬虫配置
        self._downloader = HttpDownloader()  # 默认下载器
        self._scheduler = QueueScheduler()  # 默认队列
        self.exit = False  # 爬虫退出
        self.lock = threading.Lock()  # 线程锁
        self._unfinished_tasks = 0  # 未完成的线程数
        self._success_num = 0  # 执行成功的任务数
        self._fail_num = 0  # 执行失败的任务数
        self._STAT = 0  # 全局爬虫状态
        self._STAT_INIT = 1  # 初始化
        self._STAT_RUNNING = 2  # 运行中
        self._STAT_WAITE = 3  # 暂停
        self._STAT_STOPPED = 0  # 停止
        self.EXIT_WHEN_COMPLETE = True

    @staticmethod
    def create(page_processor):
        """ 创建爬虫 """
        return Spider().spider(page_processor)

    def spider(self, page_processor):
        """ 初始化爬虫 """
        # 初始化页面处理器
        self.pageProcessor = page_processor
        # 初始化全局配置
        self.site = page_processor.get_site()
        return self

    def run(self):
        """ 运行爬虫 """
        logger.info('humanSpider 开始启动')
        executor = ThreadPoolExecutor(self._THREAD_POOL_SIZE)
        self._STAT = self._STAT_RUNNING
        while self._STAT or self.scheduler.get_queue_size():
            request = self.scheduler.get()
            if request is None:
                if self._unfinished_tasks == 0:
                    self._STAT = self._STAT_STOPPED
                else:
                    time.sleep(self.site.sleepTime)
            else:
                executor.submit(self.task, request)
                self.task_num(True)
        if self.scheduler.get_queue_size():
            self.scheduler.close()
        executor.shutdown()
        logger.info('humanSpider 运行结束')

    def task_num(self, p_or_m):
        """线程任务计数"""
        self.lock.acquire()
        if p_or_m:
            self._unfinished_tasks += 1
        else:
            self._unfinished_tasks -= 1
        self.lock.release()

    def success_and_fail_num(self, s_or_f):
        """成功失败计数"""
        self.lock.acquire()
        if s_or_f:
            self._success_num += 1
        else:
            self._fail_num -= 1
        self.lock.release()

    def task(self, request):
        self.process_request(request)
        time.sleep(self.site.sleepTime)

    def process_request(self, request):
        """ 执行下载任务 """
        page = self.downloader.download(request, self.site)
        if page.download_success:
            self.on_download_success(request, page)
        else:
            self.on_download_fail(request, page)

    def on_download_success(self, request, page):
        """ 页面下载成功 """
        try:
            self.pageProcessor.process(page)
            self.extract_and_add_requests(page)
        except Exception:
            logger.error(traceback.format_exc())
        self.on_success()

    def on_download_fail(self, request, page):
        """ 下载页面失败 """
        try:
            self.pageProcessor.process(page)
            if self.site.retryNum > request.retry:
                request.retry = request.retry + 1
                self.add_request(request, again=True)
        except Exception:
            logger.error(traceback.format_exc())
        self.on_fail()

    def on_success(self):
        """ 用于统计成功总数 """
        self.success_and_fail_num(True)
        self.task_num(False)

    def on_fail(self):
        """ 用于统计失败总数 """
        self.success_and_fail_num(False)
        self.task_num(False)

    def extract_and_add_requests(self, page):
        """ 处理新请求 """
        for request in page.targetRequests:
            self.add_request(request)

    def add_url(self, url):
        """ 初始化种子请求 """
        request = Request()
        request.method = self.site.method
        request.url = url
        request.timeout = self.site.timeOut
        request.headers = self.site.headers
        request.cookies = self.site.cookies
        request.json = self.site.json
        request.data = self.site.data
        request.proxies = self.site.proxy
        self.add_request(request)
        return self

    def add_request(self, request, again=False):
        """ 增加请求到队列 """
        self.scheduler.put(request, again)

    @property
    def downloader(self):
        return self._downloader

    @downloader.setter
    def downloader(self, d):
        self._downloader = d

    @property
    def scheduler(self):
        return self._scheduler

    @scheduler.setter
    def scheduler(self, scheduler):
        self._scheduler = scheduler

    def stop(self):
        try:
            self._STAT = self._STAT_STOPPED
        except Exception as e:
            print(e)

    def thread(self, thread_num):
        self._THREAD_POOL_SIZE = thread_num
        return self
