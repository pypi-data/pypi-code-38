# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
from .CommonLogger import debug, info, warn, error
import time


class StringWithExitstatus(str):
    '''
    封装shell调用的返回值与返回码
    res = StringWithExitstatus(stdout, stderr, exitstatus)
    print res.exitstatus   # ==> got exitcode
    print res              # ==> got stdout
    print res.err          # ==> got stderr
    '''

    def __new__(self, stdout, stderr=None, exitstatus=0):
        '''
        str的__new__是在__init__前调用的，然后str在__new__的时候发现参数不对就抛了个异常。
        这么诡异的行为主要是因为str的__new__就返回了个新的实例，而__init__没毛用
        参考: http://www.cnblogs.com/codingmylife/p/3620543.html
        '''
        return super(StringWithExitstatus, self).__new__(self, stdout)

    def __init__(self, stdout, stderr=None, exitstatus=0):
        super(StringWithExitstatus, self).__init__(stdout)
        # out 不推荐使用，直接读对象
        # self.out = stdout
        self.err = stderr
        self.exitstatus = exitstatus

    def dump(self):
        return {
            'stdout': self,
            'stderr': self.err,
            'exitstatus': self.exitstatus
        }


def execute(cmd, blocked=True):
    '''
    执行shell命令
    Args:
        cmd: shell命令
        blocked: 是否阻塞
    Returns:
        StringWithExitstatus(out,err,code)
    '''
    import time
    code, out, err = 0, None, None
    real_cmd = '. /etc/profile;{cmd}'.format(cmd=cmd)
    time_before = time.time()
    sh = Popen(real_cmd, shell=isinstance(real_cmd, basestring),
               bufsize=2048, stdin=PIPE, stdout=PIPE,
               stderr=PIPE, close_fds=True)
    if blocked:
        # 妈的这个必须用 communicate,不能wait,会有deadlock问题 https://stackoverflow.com/questions/13832734/difference-between-popen-poll-and-popen-wait
        cmd_out, cmd_err = sh.communicate()
        code = sh.poll()
        out = str(cmd_out).strip()
        err = str(cmd_err).strip()
        debug("run return {ext}".format(ext=code))
    time_after = time.time()
    time_spend = round(time_after - time_before, 2)
    debug('exec: {}: ret={}, time_spend={}'.format(cmd, code, time_spend))
    debug('stderr: {}\n stdout: {}'.format(err, out))
    return StringWithExitstatus(out, err, code)


def robust_execute(cmd, retry=5, expect_ret=0, interval=1, blocked=True):
    """高鲁棒性execute接口
    :param cmd: shell命令
    :param retry: 重试次数
    :param expect_ret: 期望返回码
    :param interval: 重试间隔，单位s
    :return:
    """
    res = None
    while retry:
        res = execute(cmd, blocked)
        if res.exitstatus == expect_ret:
            break
        retry -= 1
        warn("执行 {} 返回码为 {}，重试..".format(cmd, res.exitstatus))
        time.sleep(interval)
    return res
