from subprocess import Popen,PIPE
import os
import time
import shlex
import psutil
time.sleep(5)
print 'aaa'
cmd = 'env -i bash -c \'export CUDA_VISIBLE_DEVICES=99 && /opt/mr_binary/test_lane_client_v5.3.2 400205723 400026669_20190116160342369 3 000000020\''
cmd = shlex.split(cmd)
p = Popen(cmd, shell=False)
#p.communicate()
os.system('ps -ef|grep python')
print '123'
print os.getpid()
print p.pid
proc = psutil.Process(p.pid)   #NoSuchProcess: No process found 
for child in proc.children():
    print child.pid
print 'jincheng '
'''
#time.sleep(10)
#print 'before kill'
#time.sleep(5)
#os.system('kill -15 %s' % (p.pid))
#p.kill()
#start = time.time()
#p.wait()
#print time.time() - start
#os.kill(p.pid, 9) 
#print 'after kill'
#os.system('ps -ef|grep python')
#time.sleep(10)
#print 'jincheng'
'''
