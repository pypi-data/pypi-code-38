#!/usr/bin/env python

import os
import sys
import time

import radica.saga as rs


def fire_and_forget(wait):
    session = rs.Session()
    service = rs.job.Service(rm='local://localhost', session=session)
    description = rs.job.Description()
    description.executable = 'sleep'
    description.arguments = [wait]
    job = service.create_job(description)
    job.run()
    os.system('ps -ef -www | grep -i monitor | grep saga | grep -v grep')
    print '--'
    print job.state
    print '--'
    service.close()
    print '--'
    os.system('ps -ef -www | grep -i monitor | grep saga | grep -v grep')
    print '--'
    return job.id


def pickup(jobid, wait):
    session = rs.Session()
    service = rs.job.Service(rm='local://localhost', session=session)
    job = service.get_job(jobid)

    i = 0
    while job.state == 'Running' and i < wait:
        i += 1
        print i, 'job state:', job.state
        time.sleep(1)

    if job.state == 'Running':
        print 'Job should have finished :('
        return 1
    else:
        print 'success!'
        return 0



if __name__ == "__main__":
    waittime = 10
    jobid = fire_and_forget(waittime)
    sys.exit(pickup(jobid, waittime + 5))


