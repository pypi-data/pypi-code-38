#-*- coding:utf-8 -*-
import os
import time
import sys
sys.path.append('../')
from klog import *
if __name__ == '__main__':
    for i in range(0, 10):
        time.sleep(i)
        logger().info('第%d次:子进程id: %d' % (i, os.getpid()))
        print '第%d次:子进程id: %d' % (i, os.getpid())
        #print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #sys.stdout.flush()
        
