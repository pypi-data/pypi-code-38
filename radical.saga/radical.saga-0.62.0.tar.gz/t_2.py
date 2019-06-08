#!/usr/bin/env python

import os
import sys
import time

import radica.saga as rs


start = time.time()
jobs  = list()
for _ in range(10):
    js = rs.job.Service('ssh://localhost')
    jobs.append(js.run_job('/bin/sleep 10'))
    sys.stdout.write('.')
    sys.stdout.flush()
print
stop = time.time()
print 'time: %3.2f seconds'  % (stop - start)

os.system('ps -ef --forest | grep -v grep | grep -e "tail.*notifications"')

