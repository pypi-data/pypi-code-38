#-*- coding:utf-8 -*-
from multiprocessing import Process
from subprocess import Popen, PIPE, STDOUT
import shlex
import os
import time
from klog import *
import psutil
import fcntl
import traceback
from kd_exception import *

class BasePipe(object):
    def __init__(self, command_line):
        self.__cmd_args = shlex.split(command_line)
        self.__pid = os.getpid()
        self.__proc_pid = None
        self.popen_inst = None
        self.__memory = None
        
    def start(self):
        self.popen_inst = Popen(self.__cmd_args, stdout=PIPE, stderr=PIPE, shell=False)
        self.__proc_pid = self.popen_inst.pid
        logger().info('父进程id: %d' % self.__pid)
        logger().info('子进程id: %d' % self.__proc_pid)
        return self.popen_inst
    
    def noneblock_get_out(self):
        #设置stdout.readline()为非堵塞状态
        output = self.popen_inst.stdout
        fd_out = output.fileno()
        fl_out = fcntl.fcntl(fd_out, fcntl.F_GETFL)
        fcntl.fcntl(fd_out, fcntl.F_SETFL, fl_out | os.O_NONBLOCK)
        buff_out = ''
        try:
            while True:
                line =  output.readline().strip() 
                if not line:
                    break
                else:
                    line += '\n'
                buff_out += line
            return buff_out.strip()
        except:
            return buff_out.strip()
   
    def noneblock_get_err(self):
        #设置stderr.readline()为非堵塞状态
        errput = self.popen_inst.stderr
        fd_err = errput.fileno()
        fl_err = fcntl.fcntl(fd_err, fcntl.F_GETFL)
        fcntl.fcntl(fd_err, fcntl.F_SETFL, fl_err | os.O_NONBLOCK)
        buff_err = ''
        try:
            while True:
                line =  errput.readline().strip() 
                if not line:
                    break
                else:
                    line += '\n'
                buff_err += line
            return buff_err.strip()
        except:
            return buff_err.strip()


 
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
        coreDump_cmd = 'kill -11 ' + str(pid)
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
        self.__child_oom = total_memory
        self.__last_out_ts = 0
        self.__last_err_ts = 0
    
    def run(self, verbose=False):
        if not verbose:
            self.popen_inst.communicate()
        else:
            try:
                time_start_out = time.time()
                time_start_err = time_start_out
                while self.popen_inst.poll() is None:
                    buff_out = None
                    buff_err = None
                    buff_out = self.noneblock_get_out()
                    self.__last_out_ts = time.time() - time_start_out
                    if buff_out:
                        print buff_out[:-1]
                        time_start_out = time.time()
                    #print 'timestep: %f' % (self.__last_out_ts)
                    buff_err = self.noneblock_get_err()
                    self.__last_err_ts = time.time() - time_start_err
                    if buff_err:
                        print>>sys.stderr, buff_err[:-1]
                        time_start_err = time.time()
                    #print 'timestep: %f' % (self.__last_out_ts)
                    if self.__last_out_ts >= self.__timeout and self.__last_err_ts >= self.__timeout:
                        raise ProcessTimeoutException(self.__timeout) # out和err都超时没有输出
                    if self.get_rss_memory() >= self.__child_oom:
                        raise ProcessMemoryoutException(self.__child_oom) #超出限制内存
                    time.sleep(0.001)
                # 进程结束之后，可能管道里还有数据
                buff_out = self.noneblock_get_out()
                if buff_out:
                    print buff_out[:-1]
                buff_err = self.noneblock_get_err()
                if buff_err:
                    print>>sys.stderr, buff_err
            except ProcessTimeoutException, e:
                self.kill()
                print traceback.format_exc()
            except ProcessMemoryoutException, e:
                self.kill()
                print traceback.format_exc()

        
def test1():
    p = AdvPipe('python -u child.py', 5, 1000)
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
