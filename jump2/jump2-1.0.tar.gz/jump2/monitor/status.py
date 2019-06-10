# coding: utf-8
# Copyright (c) JUMP2 Development Team.
# Distributed under the terms of the JLU License.


#=================================================================
# This file is part of JUMP2.
#
# Copyright (C) 2017 Jilin University
#
#  Jump2 is a platform for high throughput calculation. It aims to 
#  make simple to organize and run large numbers of tasks on the 
#  superclusters and post-process the calculated results.
#  
#  Jump2 is a useful packages integrated the interfaces for ab initio 
#  programs, such as, VASP, Guassian, QE, Abinit and 
#  comprehensive workflows for automatically calculating by using 
#  simple parameters. Lots of methods to organize the structures 
#  for high throughput calculation are provided, such as alloy,
#  heterostructures, etc.The large number of data are appended in
#  the MySQL databases for further analysis by using machine 
#  learning.
#
#  Jump2 is free software. You can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published 
#  by the Free sofware Foundation, either version 3 of the License,
#  or (at your option) and later version.
# 
#  You should have recieved a copy of the GNU General Pulbic Lincense
#  along with Jump2. If not, see <https://www.gnu.org/licenses/>.
#=================================================================

"""
This module defines the classes relating to show the status of tasks.
"""


__author__ = "Xin-Gang Zhao"

class CheckStatus(object):

    import re, os, sys 
    from re import split 
    import cPickle as pickle
    from ..utils.io import is_exist, load_pool, local_pool_path

    def __init__(self, option):

        import sys 
        if isinstance(option, dict) and isinstance(option['check'], bool):
            return 
        #check the number and name of tasks under user direction %
        self.all_pools = None
        self.all_pools = self.get_all_pools()
        if self.all_pools is None:
            print """No running or waiting tasks under this user,
                    please use 'jump2 -i input.py'  to contruct
                    the input files for new tasks.
                    """
            sys.exit()
        #default to check all the tasks under this user % 
        if isinstance(option, str):
            self.check_pool(pool=None, status='all')
        
        #check single tasks % 
        elif isinstance(option, dict):
            pool = option['pool']
            status = option['check']
            #check the tasks under current direction %
            if not is_exist(pool+'.pool'):
                raise IOError ('No such {0} file in current direction'.format(pool))

            elif pool in self.all_pools:
                #if pool in self.all_pools: 
                self.check_pool(pool, status)
            else:
                raise IOError ("{0} finished/delete ID info".format(pool))
        
    # check the all/current tasks according to the pools %
    def check_pool(self, pool, status=None):

        if pool is None: pool = 'all'

        if isinstance(status, str):
            # default check % 
            if pool == 'all':
                self.check_all_tasks_status()
            else:
                self.check_single_task_status(pool, status)

    # check single tasks %
    def check_single_task_status(self, pool, fstat):

        all_status = ['done', 'running', 'wait', 'error']
        
        #all the status focus on %  
        if fstat == 'all': 
            fstat = all_status
        else:
            fstat = [fstat]

        #get the ID info of pool %
        spl = self.all_pools[pool]
        status = self.collect_status(spl, all_status)
        
        # show the status on screen %
        print "----------------------------------------"
        print "%tasks pool%:", pool
        self.show_status(status, fstat)

        # delete ID information of the finished tasks % 
        path = local_pool_path()
        if status['wait'] == 0 and status['running'] == 0:
            os.remove(os.path.join(path, pool))
            
    #check all tasks status in this user %
    def check_all_tasks_status(self):
        for p in self.all_pools:
            self.check_single_task_status(p, 'all')
        
    
    #collect the status in the jobs pool %
    def collect_status(self, pool, status):
      
        from ..utils.io import load_pool

        nstatus = {}
        for k in status: nstatus[k] = 0

        nstatus['name'] = pool['name']
        nstatus['path'] = pool['path']
   
        job_status = load_pool(nstatus['path'], nstatus['name'])
    
        elog=[]
        dlog=[]
        rlog=[]

        for j in job_status['tasks']:
            path = os.path.join(job_status['folder'], j)     
            # modify the status % 
            if isdone(path):
                job_status['tasks'][j]['status'] = 'done'
                dlog.append(path)
            if isrunning(path): 
                job_status['tasks'][j]['status'] = 'running'
                rlog.append(path)
            if iserror(path): 
                job_status['tasks'][j]['status'] = 'error'
                elog.append(path)

            #count the status %
            if job_status['tasks'][j]['status'] in status:
                nstatus[job_status['tasks'][j]['status']] += 1

        #output status log % 
        all_log = [elog, dlog, rlog]
        status_label=['error', 'done', 'running'] 
        for log in all_log:
            if log is not []:
                with open(job_status['folder']+'/{0}.log'\
                    .format(status_label[all_log.index(log)]), 'wb') as f:
                    f.write('\n'.join(log))
        
        return nstatus

    #show the check status %
    def show_status(self, status, fstat):

        all_status = ['done', 'running', 'wait', 'error']

        for k in all_status:
            if k in fstat:
                print 
                print "%12s %8s :: %8s" % ("%% "+k.upper(), " %% tasks", status[k])
        
    # check the pools at current paths %
    def iscurrent_pool(self):

        current_pool = []

        plfiles = os.walk('.').next()[2]
       
        for p in plfiles:
            # judge current pool is under running %
            if p.endswith('.pool') and p.split('.')[0] in self.all_pools: 
                
                current_pool.append(p)

        if current_pool is not None:
            
            print 
            is2select = raw_input("whether you want to check ONE task? (n/y)")
            print 
            if 'y' in is2select.lower():
                
                current_pool = self.select_pool2check(current_pool)

        # return the result %
        if current_pool is None:

            return None

        else:
            return current_pool

    #select the given pool to  check%  
    def select_pool2check(self, current):

        n = 0
        select_pool = None

        print 
        print "Please select the current pool you want to check, default is all." 
        for p in current:
            print "[{0}] : {1}".format(str(n), p.split('.')[0])
            n += 1
        
        pool = input()
        
        while (not isinstance(pool, int) or pool >= len(current)):
            
            if pool >= len(current):
                print "invalid the index, please input again...."
                pool = input()
        
        select_pool = current[pool]
      # if isinstance(pool, int) and pool < len(current):
      #     select_pool = current[pool]

        # elif isinstance(pool, str) and pool+'.pool' in current:
      #     select_pool = pool

        # else:
      #     print "Invalid input, all the tasks under current direction will be check."
      #     select_pool = current
       #if isinstance(pool, str) and pool in current:
       #    
       #    select_pool = pool
       #
       #else:
       #    print "Invalid input, all the tasks under current direction will be check."
       #    select_pool = current 

        return select_pool 


    # check all the pool %
    def get_all_pools(self):

        """
        method:: get all the pool under this user.
        """
        import os
        from ..utils.io import local_pool_path, is_exist 
        pools = {}  #  dict to store the pools  % 

        path = local_pool_path()
        if not is_exist(path): return None 
        # iteritems all the files %
        for d in os.walk(path).next()[2]:
            pool = {}
            file_dir = os.path.join(path, d)
            #obtained the contains of file %
            with open(file_dir) as f:

                for line in f.readlines():
                    if len(line.split()) == 0: continue
                    pool[line.split(':')[0].strip()] = line.split(':')[1].strip()
                f.close()

            pools[d] = pool
     
        if len(pools) == 0:
            return None

        else:
            return pools
