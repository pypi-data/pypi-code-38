#!/usr/bin/env python

import sys
import time
import subprocess as sp

p = sp.Popen (executable = "/bin/sh",
              args       = ['-x', 'wrapper.sh' ],
              stdin      = sp.PIPE, 
              stdout     = sp.PIPE, 
              stderr     = sp.STDOUT)

print 'in'
cmd = "BULK\nRUN /bin/sleep 1\nBULK_RUN\n"
p.stdin.write(cmd)
time.sleep(0.5)
print 'out'
print p.communicate()

