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
This module defines the classes relating to monitor the tasks.
"""


__author__ = "Xin-Gang Zhao"

import os, cPickle as pickle 
#from io.pool import Pool
from status import CheckStatus

#from module_factory import ModuleFactory

class Monitor(object):
   
    """
    Monitor check the status of the running jobs and update the pool 
    of sequene and recorrect the normal error.
    """
   
    def __init__(self, pool=None, path=None, *args, **kwargs):
        
        self.__check_pool__(pool, path)  # check the old pool
        if kwargs.has_key('pool'):
            self.__update__(kwargs['pool'])      
            # update the job sequene
        self.__status__ = None 

    def __check_pool__(self, pool=None, path=None):
   
        """
        check all the jobs status in the pool.
        """
        
        from os.path import exists, join
        
        if pool is None: return
        
        root = path
        for p in pool:
            if pool[p]['status'] in ['running','error', 'done']: 
                pass
            stdout = join(root, p)
            if exists(stdout):
               std_done = join(stdout, '.sucess')
               if exists(std_done):
                   stat, stdin = self.__sucess__(std_done) 
                   pool[p]['status'] = stat
                   pool[p]['functional'].stdin = stdin

    def __sucess__(self, path=None):
        """
        to check all the tasks 
        """
        if path is None: return 
        with open(path, 'r') as f:
            while True: 
                line = f.readline()
                if not line: break
		if line.split()[1] is 'done':
		    if line.startswith('optimize'):
                        temp = line.split()[2]
		    if line.startswith('scf'):
                        temp = line.split()[2]
                else:
                    return 'error', temp
        return sucess, None
                  
    def __update__(self):

        """
        Update the pool after the checking all the jobs status.
        """

        pass

    def __check_status__(self):


        pass

    def jobtag(self, stat):
        

        if stat == 'wait': self.__status__ = 'wait'   
        
        if stat == 'break': self.__status__ = 'break' 

        if stat == 'error': self.__status__ = 'error' 

        if stat == 'failed': self.__status__ = 'failed' 
        
        if stat == 'success': self.__status__ = 'success' 
 

    def __repr__(self):


        #"""
        #Return a tuple contained the jobs status.
        #"""

       #total = self.total()
       #success = self.success()
       #running = self.running()
       #error = self.error()
       #waiting = self.waiting()
        self.__allstatus__ = True 
        total = 10 
        success = 5
        running = 3
        error = 2
        waiting = 1 
        status_list = ['Total', 'Success', 'Running', 'Error', 'Waiting']      
        status_num  = [total, success, running, error, waiting]

        if self.__allstatus__ is True:
             for s,n in zip(status_list, status_num): 
                 print "%12s: %9d" %(s, n)
                 print 

        return ''
