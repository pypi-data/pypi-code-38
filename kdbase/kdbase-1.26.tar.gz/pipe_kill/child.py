#-*- coding:utf-8 -*-
import os
import time
import sys

if __name__ == '__main__':
    for i in range(0, 10):
        time.sleep(i)
        #logger().info('第%d次:子进程id: %d' % (i, os.getpid()))
        print '第%d次:子进程id: %d' % (i, os.getpid())
        print '第%d次:子进程id: %d' % (i, os.getpid())
        #sys.stdout.flush()
        if i%2 == 0:
            sys.stderr.write('第%d次error\n' % (i))
    #time.sleep(30)
    sys.stderr.write('第%d次error\n' % (i))
        #print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #sys.stderr.flush()
        
