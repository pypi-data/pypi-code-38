import subprocess
import os
import fcntl
p = subprocess.Popen('./a.out', stdout=subprocess.PIPE, shell=False)
output = p.stdout
fd_out = output.fileno()
fl_out = fcntl.fcntl(fd_out, fcntl.F_GETFL)
fcntl.fcntl(fd_out, fcntl.F_SETFL, fl_out | os.O_NONBLOCK)
while p.poll() is None:
    t=1
print p.stdout.read()
print '123'
print p.stdout.readlines()
