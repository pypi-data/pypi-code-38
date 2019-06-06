#-*- coding:utf-8 -*-
from multiprocessing import Process
from subprocess import Popen, PIPE
from timeout_decorator import timeout as time_limit
import shlex
import os
import time
import sys
from sub import *
sys.path.append('../')
from klog import *
import psutil

class SubProcess(object):
    def __init__(self, command_line):
        self.cmd_args = shlex.split(command_line)
        self.pid = os.getpid()
        self.child_pid = None
        self.popen_inst = None
        self.memory = None
        
    def start(self):
        self.popen_inst = Popen(self.cmd_args, stdout=PIPE, stderr=PIPE, shell=False)
        self.child_pid = self.popen_inst.pid
        logger().info('父进程id: %d' % self.pid)
        logger().info('子进程id: %d' % self.child_pid)
        return self.popen_inst

    def get_outerr(self):
        return self.popen_inst.stdout.readline(), self.popen_inst.stderr.readline()

    def wait(self):
        self.popen_inst.wait()

    #杀死父进程和子进程
    def kill_all(self, signal=9):
        result = os.killpg(self.pid, signal)
    
    #只杀死子进程
    def kill(self, signa, signal):
        result = os.kill(self.child_pid, signal)

    #获取子进程的返回值
    def get_child_value(self):
        self.popen_inst.wait()
        value = self.popen_inst.returncode
        return value

    def get_child_memory(self):
        child = psutil.Process(self.child_pid)
        self.memory = child.memory_info().rss / 1024 / 1024    
        return self.memory
    
    def gen_core(self, pid):
        #设置coredump文件大小
        coreSize_cmd = 'ulimit -c unlimited'
        Popen(coreSize_cmd, stdout=PIPE, stderr=PIPE, shell=True)
        #查询coredump文件产生位置
        corePath_cmd = 'cat /proc/sys/kernel/core_pattern'
        corePath_inst = Popen(corePath_cmd, stdout=PIPE, stderr=PIPE, shell=True)
        corePath = corePath_inst.stdout.readline()
        logger().info('coredump文件:%s' %corePath)
        coreDump_cmd = 'kill -11 '+str(pid)
        try:
            coreDump_inst = Popen(coreDump_cmd, stdout=PIPE, stderr=PIPE, shell=True)
            coreDump_out = coreDump_inst.stdout.readline()
            logger().info('%s'%coreDump_out)
            logger().info('Segmentation fault (core dumped)')
        except:
            logger().info('Error when generating coredump file')


class AdvProcess(SubProcess):
    def __init__(self, command_line, timeout, total_memory):
        super(AdvProcess, self).__init__(command_line)
        self.timeout = timeout
        self.total_memory = total_memory
    
    def show(self):
        # while self.popen_inst.poll() is not  None:
        try:
            while True:
                time_start = time.time()
                buff_out = None
                buff_err = None
                buff_out, buff_err = time_limit(self.timeout)(super(AdvProcess, self).get_outerr)()
                if super(AdvProcess, self).get_child_memory() >= self.total_memory:
                    print 'Memory out!'
                    #print  super(AdvProcess, self).get_child_memory() 
                    super(AdvProcess, self).kill_all()
                    break
                print 'spend %f s' % (time.time() - time_start)
                if not buff_out and not buff_err:
                    break
                else:
                    if buff_out:
                        print buff_out
                        logger().info(buff_out)
                    if buff_err:
                        print buff_err
                        logger().error(buff_err)
        except:
            print "Time out!"
            super(AdvProcess, self).kill_all()
    

def test1():
    p = AdvProcess('python -u child.py', 5, 8)
    #p = WorkerProcess('python test.py')
    p.start()
    p.show()
    #time.sleep(5)
    print '子进程占用内存大小: %d KB' % p.get_child_memory()
    #p.kill()
    time.sleep(1)
    print '子进程返回值: %s' % p.get_child_value()
    

if __name__ == '__main__':
    test1()
