from subprocess import Popen,PIPE
import os
import time

p = Popen(['python','child.py'], shell=False)
#p.communicate()
print os.getpid()
print p.pid
print 'jincheng '
time.sleep(10)
os.system('ps -ef|grep python')
print 'before kill'
time.sleep(5)
#os.system('kill -15 %s' % (p.pid))
p.kill()
start = time.time()
p.wait()
print time.time() - start
#os.kill(p.pid, 9) 
print 'after kill'
os.system('ps -ef|grep python')
time.sleep(10)
print 'jincheng'

