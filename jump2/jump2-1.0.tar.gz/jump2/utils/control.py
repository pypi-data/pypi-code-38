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
This module defines the classes relating to managing the tasks.
"""


__author__ = "Xin-Gang Zhao"
__copyright__ = "Copyright 2017, The JUMP2"
__version__ = "1.0"
__maintainer__ = "JUMP2 team"
__email__ = "xgzhao@0201@gmail.com"
__status__ = "underdeveloped"



from jump2.utils.io import is_exist, noparses 


# underdeveloped class for launch tasks 

class ProjectJob(object):
    
    """
    Aim to launch the tasks in different method, 
        in sequence,
           multijobs,
           interactive,
           etc
    """

    def launch(self, *args, **kwargs):
        pass

    def __launch_single__(self, pool, path):
        pass

    def __launch_script__(self, pool):
        pass
        


class LaunchTasks(object):
    

    @property
    def mgcluster(self, value):
        pass

    def launch(self, *args, **kwargs):
        """
        launch the tasks for according to the setting the 
        parameters.
        
        args:
            prepare:: orgnize the input file; 
            single:: launch the single task;
            input:: prepare the input files;
            qsub:: launch the tasks of maximum of jobs;

        """
        if 'single' in args[0]:
            self.__launch_interactive__(args[0]['single'])
            return   # run single tasks % 
            
        if 'prepare' in args:
            from input import jump_input
            p = jump_input()  # output the pool files % 

        if 'qsub' in args:
            submit = True # qsub the task % 

        if 'input' in args:
            submit = False # sumbit the tasks % 

        if 'max_jobs' in kwargs:
            max_num = kwargs['max_jobs']
        else:
            max_num = 10   # maximum number of project tasks % 

        #print self.parses
        if self.parses.has_key('pool'):
            pool = self.parses['pool']
            if not is_exist(pool):
                raise IOError ('No file named {0}'.format(pool))
            else:
                self.__load_pool__(pool)
                if submit is True:
                    self.__submit__(pool, max_num, True)
               	    print "true"
		else:
                    self.__submit__(pool, max_num, False)
		    print "false"  
    # 
    def __launch_interactive__(self, path):
        
        self.__load_pool__(path['path'])

        func = self.pool[path['task']]['functional']
        stdout = path['task']
        func.calculator(func, stdout)
	
	# underdevelopment % 
        #self.__submit__(pool, 10, submit=True)

    # load jobs pool %     
    def __load_pool__(self, name):

        import cPickle as pickle 
        import fcntl

        if is_exist(name):
            try:
                with open(name, 'rb') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    self.pool = pickle.load(f)
                    fcntl.flock(f,fcntl.LOCK_UN)
                    f.close()
            except:
                raise IOError ('cannot open the pool file.')
    
    # dumpy jobs pool %     
    def __dump_pool__(self, name):

        import cPickle as pickle 
        import fcntl

        if is_exist(name):
            try:
                with open(name, 'wb') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    pickle.dump(self.pool, f)
                    fcntl.flock(f,fcntl.LOCK_UN)
                    f.close()
            except:
                raise IOError ('cannot open the pool file.')
    def write_scripts(self, pool, path, name):

        from jump2.config.cluster import Cluster
        import os 
        from jump2.utils.io import is_exist
        from os.path import dirname  
       
        info = Cluster()
        head = info.scripts['head'].format(name)
        
        script = """jump2 --single {pool}  {path}\n
cd {pool_root} \n
jump2 -r qsub -f {pool} --num 1\n
                 """.format(pool=pool,path=path, pool_root=dirname(pool))
        
        if not is_exist(path): os.makedirs(path)
        path_script = os.path.join(path, 'pbsscript')
        path_wait = os.path.join(path, '.wait')

        with open(path_script, 'wb') as f:
            f.write(head)
            f.write(script)

        with open(path_wait, 'wb') as f:
            f.write('wait for sumbit')


    # prepare the input files % 
    def __submit__(self, pool, max_num, submit=False):
        
        import os
        from os.path import dirname
	from jump2.monitor import Monitor
	
        count = 0
        root_pool = os.path.abspath(pool)
	
	Monitor(self.pool, dirname(root_pool)) # check the status of all the tasks % 
	
        for j in self.pool.keys():
            if self.pool[j]['status'] == 'wait' and \
                    count <= max_num and not self.pool[j].has_key('id'):
                if submit is True:
                    self.write_scripts(root_pool, j, pool)
                    job_id = self.pool[j]['functional'].submit_task(j)   
                    self.pool[j]['id'] = job_id 
                # underdevelopment % 
                #else:
                #    self.pool[j]['functional'].calculator(j, self.pool[j]['structure'])
                count += 1

	self.__dump_pool__(root_pool)


def run_jump2():
    from ..parse import  __jump2label__
    from ..parse.parse import collect_parses
    from ..monitor.status import CheckStatus
    from ..parse.parse_process import ParseProcess 
    from ..analysis import Analysis
    # if not input parses, all the tasks under this user will be 
    # checked by default. % 

    #jump2label()
    if noparses():
        #print out the logo of JUMP2 %
        __jump2label__()
        #check tasks status % 
        CheckStatus('all')
    else:
        # basic parses will be configured %
        # a) -r [options]
        #       output the input files;
        #       submit the tasks;
        #
        # b) -e [options]
        #       extract the basic information from results
        #        
        # c) -c [options]
        #       check the tasks status

        #orgnize the input parses % 
        options = collect_parses()

        #prepare input for calculation %
        ParseProcess(options) 
        #check the status % 
        if not options.has_key('run') \
            and options.has_key('check_status'):
            CheckStatus(options)
        # extract data and tar/store data %
        if options.has_key('extract_data'):
            Analysis(options) 
