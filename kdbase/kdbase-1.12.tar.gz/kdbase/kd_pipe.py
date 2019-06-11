#-*- coding:utf-8 -*-
from multiprocessing import Process
from subprocess import Popen, PIPE, STDOUT
from timeout_decorator import timeout as time_limit
import shlex
import os
import time
from klog import *
import psutil

class BasePipe(object):
    def __init__(self, command_line):
        self.__cmd_args = shlex.split(command_line)
        self.__pid = os.getpid()
        self.__proc_pid = None
        self.popen_inst = None
        self.__memory = None
        
    def start(self):
        self.popen_inst = Popen(self.__cmd_args, stdout=PIPE, stderr=STDOUT, shell=False)
        self.__proc_pid = self.popen_inst.pid
        logger().info('父进程id: %d' % self.__pid)
        logger().info('子进程id: %d' % self.__proc_pid)
        return self.popen_inst
    
    def get_out(self):
        out =  self.popen_inst.stdout
        if out == None:
            return None
        else:
            return out.readline()
    
    def get_err(self):
        err =  self.popen_inst.stderr
        if err == None:
            return None
        else:
            return err.readline()


    def wait(self):
        self.popen_inst.wait()
 
    #只杀死子进程
    def kill(self, signal=15):
        result = os.kill(self.__proc_pid, signal)  #OSError: NO such process

    #获取子进程的返回值
    def get_return_code(self):
        self.popen_inst.wait()
        value = self.popen_inst.returncode
        return value

    def get_rss_memory(self):
        proc = psutil.Process(self.__proc_pid)   #NoSuchProcess: No process found 
        self.__memory = proc.memory_info().rss / 1024 / 1024    
        return self.__memory
    
    def gen_core(self, pid):
        #设置coredump文件大小
        coreSize_cmd = 'ulimit -c unlimited'
        os.system(coreSize_cmd)
        #查询coredump文件产生位置
        corePath = os.popen('cat /proc/sys/kernel/core_pattern').read()
        logger().info('coredump文件: %s' % corePath)
        coreDump_cmd = 'kill -11 '+str(pid)
        try:
            coreDump_inst = Popen(coreDump_cmd, stdout=PIPE, stderr=PIPE, shell=True)
            coreDump_out = coreDump_inst.stdout.readline()
            logger().info('%s' % coreDump_out)
            logger().info('Segmentation fault (core dumped)')
        except Exception, e:
            print e


class AdvPipe(BasePipe):
    def __init__(self, command_line, timeout, total_memory):
        super(AdvPipe, self).__init__(command_line)
        self.__timeout = timeout
        self.__total_memory = total_memory
    
    def run(self, verbose=False):
        if not verbose:
            self.popen_inst.communicate()
        else:
            try:
                while self.popen_inst.poll() is None:
                    time_start = time.time()
                    buff_out = None
                    buff_err = None
                    buff_out = time_limit(self.__timeout)(super(AdvPipe, self).get_out)()
                    buff_err = time_limit(self.__timeout)(super(AdvPipe, self).get_err)()
                    if super(AdvPipe, self).get_rss_memory() >= self.__total_memory:
                        print 'Memory out!'
                        #print  super(AdvPipe, self).get_rss_memory() 
                        super(AdvPipe, self).kill_all()
                        break
                    print 'spend %f s' % (time.time() - time_start)
                    if buff_out:
                        print buff_out
                    if buff_err:
                        print>>sys.stderr, buff_err
                    
            except:
                print "Time out!"
                super(AdvPipe, self).kill_all()
    


        
def test1():
    p = AdvPipe('python -u child.py', 5, 8)
    #p = WorkerProcess('python test.py')
    p.start()
    p.run(True)
    #time.sleep(5)
    #print '子进程占用内存大小: %d KB' % p.get_rss_memory()
    #p.kill()
    #p.wait()
    #time.sleep(1)
    #print '子进程返回值: %s' % p.get_return_code()
    

if __name__ == '__main__':
    test1()
