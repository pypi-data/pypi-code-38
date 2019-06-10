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
This module defines the classes relating to organize the parses.
"""

__contributor__ = 'Xingang Zhao'
__edited_date__ = '2017.05.17'

from ..utils.control import LaunchTasks
#class ParseProcess(Compute):

"""aiming to preprocess the input according to the parses."""
class ParseProcess(LaunchTasks):
    
    """
    class ParseProcess:: aiming the process the input files and
          orgnize the input data according to the input parses.

    methods:: 
          class_tasks:: orgnize the tasks w.r.t input parameters.

          update_pool_env:: update the tasks environment when the
              tasks move to direction.

	  update_data:: 

    """

    def __init__(self, options, *args, **kwargs):

        import time, os
        self.pool = None
        # get the input parse %
        if isinstance(options, dict):
            self.parses = options

        if kwargs is not None:
            pass
            #self.__update__(*args, **kwargs)

        self.__class_options__()

    # create prepared input file for program % 
    def __create_input__(self, overwrite=False):
        """
        Create the sample of input files.

        args:
            overwrite:: bool, overwrite the input example.

        """
        from ..utils.cores import __input_scripts as script

        if overwrite is True:
            with open('input.py', 'wb') as f:
                f.write(script.format(self.parses['script']))


    # classic the basic motion % 
    def __class_options__(self):
        
        from ..utils.io import is_exist

        # launch single tasks % 
        if self.parses.has_key('single'):
            self.launch(self.parses)
            return

        # create input example according to  parses% 
        if self.parses.has_key('script'):
            # create script % 
            if not is_exist('input.py'): 
                self.__create_input__(overwrite=False)
                self.parses.pop('script')
            else:
                self.__create_input__(overwrite=True)
                self.parses.pop('script')
            return 
        
        # update the pool environmment info due to change
        # calculation direction % 
        if  self.parses['update']:
            self.__update__()

        # submit the tasks by using scripts % 
        if 'run' in self.parses:
            self.launch(self.parses['run'])
            if 'tarfile' in self.parses:
                self.tarfile_data()
            return

	# remote manager the tasks % 
	if 'ssh' in self.parses:
	    if self.parses['ssh'] is not None:
		self.remote_manager()
   
    # update the pool environment %  
    def __update__(self, *args, **kwargs):
      
        from ..utils.io import is_exist

        # pool files exists %
        pool = self.parses['pool']
        if not is_exist(pool):
                #self.parses.__update__()
                 pass   
	elif is_exist(pool):
            if self.parses['overwrite'] is False:
	        raise IOError ("pool file exists!")
	    
        # update the pool environmment info due to change % 
        #self.update_pool_env(options['pool'])
        
        # default parrellel environment % 
        #penv = parrallel_env
        #penv.update(options['cluster'])
        #self.update_parrallel_env(options, penv)

        #update pool data % 
        #if overwrite: self.update_pool_data()

    def tarfile_data(self):
        pass

    # create pool env at ~/.local/jump2/pool %
    def update_pool_env(self, pool):
        """
        update the runing environment of the tasks of pool.
        """

        from os.path import basename
        # for existed pool %
        if is_exist(pool):
            abspath = os.path.abspath(pool) 
            name = basename(abspath)
            path = abspath.replace(name,'')
        
        # for new pool %
        else:
            name = basename(pool)
            path = os.getcwd()

        # basic info %
        localtime = time.asctime(time.localtime(time.time()))
        new_path = local_pool_path()

        # mkdir ~/.local/jump2/pool direction %
        if not os.path.isdir(new_path):
            os.makedirs(new_path)

        # store the basic info
        with open(new_path+pool, 'wb') as f:
            f.write('name : '+ name+ '\n')
            f.write('path : '+ path+ '\n')
            f.write('time : '+ localtime+ '\n')

    #options % 
    def post_option(self,option):
        
        option['run']  = 'submit'
        if 'all' in option['args']: del option['args']
        del option['check']
        del option['update']
        option['overwrite'] = False

        pickle.dump((option),(open('.cluster','wb')))

