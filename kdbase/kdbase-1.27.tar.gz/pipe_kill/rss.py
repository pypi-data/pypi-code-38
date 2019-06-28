from subprocess import PIPE, Popen, STDOUT
import os
import shlex
if __name__ == '__main__':
    pid = 21916
    cmd_top = 'top -p %s' % (str(pid))
    #cmd_top = shlex.split(cmd_top)
    print '1'
    #p = Popen(cmd_top, shell=False)
    p = Popen(cmd_top, stdout=PIPE, stderr=STDOUT, shell=True)
    print '2'
    print p.stdout.read()
    print 'aaa'
    
