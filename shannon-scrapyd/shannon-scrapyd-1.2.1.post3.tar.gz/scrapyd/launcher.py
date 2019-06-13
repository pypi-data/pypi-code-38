import os
import sys
import json
from datetime import datetime
from multiprocessing import cpu_count

import requests
from twisted.internet import reactor, defer, protocol, error
from twisted.application.service import Service
from twisted.python import log

from scrapyd.config import Config
from scrapyd.utils import get_crawl_args, native_stringify_dict
from scrapyd import __version__
from .interfaces import IPoller, IEnvironment

class Launcher(Service):

    name = 'launcher'

    def __init__(self, config, app):
        self.processes = {}
        self.finished = []
        self.finished_to_keep = config.getint('finished_to_keep', 100)
        self.max_proc = self._get_max_proc(config)
        self.runner = config.get('runner', 'scrapyd.runner')
        self.app = app

    def startService(self):
        for slot in range(self.max_proc):
            self._wait_for_project(slot)
        log.msg(format='Scrapyd %(version)s started: max_proc=%(max_proc)r, runner=%(runner)r',
                version=__version__, max_proc=self.max_proc,
                runner=self.runner, system='Launcher')

    def _wait_for_project(self, slot):
        poller = self.app.getComponent(IPoller)
        poller.next().addCallback(self._spawn_process, slot)

    def _spawn_process(self, message, slot):
        msg = native_stringify_dict(message, keys_only=False)
        project = msg['_project']
        args = [sys.executable, '-m', self.runner, 'crawl']
        args += get_crawl_args(msg)
        e = self.app.getComponent(IEnvironment)
        env = e.get_environment(msg, slot)
        env = native_stringify_dict(env, keys_only=False)
        pp = ScrapyProcessProtocol(slot, project, msg['_spider'], \
            msg['_job'], env)
        pp.deferred.addBoth(self._process_finished, slot)
        reactor.spawnProcess(pp, sys.executable, args=args, env=env)
        self.processes[slot] = pp

    def _process_finished(self, _, slot):
        process = self.processes.pop(slot)
        process.end_time = datetime.now()
        self.finished.append(process)
        del self.finished[:-self.finished_to_keep] # keep last 100 finished jobs
        self._wait_for_project(slot)

    def _get_max_proc(self, config):
        max_proc = config.getint('max_proc', 0)
        if not max_proc:
            try:
                cpus = cpu_count()
            except NotImplementedError:
                cpus = 1
            max_proc = cpus * config.getint('max_proc_per_cpu', 4)
        return max_proc

class ScrapyProcessProtocol(protocol.ProcessProtocol):

    def __init__(self, slot, project, spider, job, env):
        self.slot = slot
        self.pid = None
        self.project = project
        self.spider = spider
        self.job = job
        self.start_time = datetime.now()
        self.end_time = None
        self.env = env
        self.logfile = env.get('SCRAPY_LOG_FILE')
        self.itemsfile = env.get('SCRAPY_FEED_URI')
        self.deferred = defer.Deferred()
        self.error_list = list()

    def outReceived(self, data):
        log.msg(data.rstrip(), system="Launcher,%d/stdout" % self.pid)

    def errReceived(self, data):
        self.error_list.append(str(data.rstrip()))
        log.msg(data.rstrip(), system="Launcher,%d/stderr" % self.pid)

    def connectionMade(self):
        self.pid = self.transport.pid
        self.log("Process started: ")

    def processEnded(self, status):
        if isinstance(status.value, error.ProcessDone):
            self.log("Process finished: ")
        else:
            self.log("Process died: exitstatus=%r " % status.value.exitCode)
            try:
                error_data = str(self.error_list[-1]).encode('utf-8').decode('utf-8')
            except:
                error_data = ''
            try:
                self.send_dingtalk_info("Process died: exitstatus=%r " % status.value.exitCode, str(error_data))
                self.error_list = list()
            except:
                pass
        self.deferred.callback(self)

    def log(self, action):
        fmt = '%(action)s project=%(project)r spider=%(spider)r job=%(job)r pid=%(pid)r log=%(log)r items=%(items)r'
        log.msg(format=fmt, action=action, project=self.project, spider=self.spider,
                job=self.job, pid=self.pid, log=self.logfile, items=self.itemsfile)

    def send_dingtalk_info(self, action, error_data):
        '''
        title: 报警标题
        '''
        failure_template_info = ('### {title}\n\n'
                                 '> hostname: {hostname}\n\n'
                                 '> error_count: {error_count},'
                                 'project: {project},'
                                 'spider: {spider},'
                                 'job: {job},'
                                 'pid: {pid},'
                                 'log: {log},'
                                 'items: {items}\n\n'
                                 'error_data: {error_data}')
        
        try:
            hostname_obj = os.popen('hostname')
            hostname = str(hostname_obj.read())
            conf = Config()
            dingtalk_robot_error = conf.get('dingtalk_robot_error')

            content = failure_template_info.format(
                title='scrapyd==》爬虫任务异常死亡报警',
                hostname=hostname,
                error_count=action,
                project=self.project,
                spider=self.spider,
                job=self.job,
                pid=self.pid,
                log=self.logfile,
                items=self.itemsfile,
                error_data=error_data,
            )

            msg = {
                "msgtype": "markdown",
                "markdown": {
                    "title": '爬虫任务异常死亡报警',
                    "text": content
                }
            }

            i = 0
            while i < 3:
                i += 1 
                resp = requests.post(dingtalk_robot_error, json=msg, timeout=30)
                json_data = json.loads(resp.text)
                if resp.status_code == 200 and json_data['errcode'] == 0:
                    break
                else: 
                    fmt = '钉钉报警发送失败%(errmsg)s'
                    log.msg(format=fmt, errmsg=json_data['errmsg'])
        except Exception as e:
            fmt = '钉钉报警发送失败%(e)s'
            log.msg(format=fmt, e=str(e))
