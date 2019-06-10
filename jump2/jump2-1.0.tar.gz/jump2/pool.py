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
This module defines the classes relating to tasks pool.
"""


__author__ = "Xin-Gang Zhao"
__copyright__ = "Copyright 2017, The JUMP2"
__version__ = "1.0"
__maintainer__ = "JUMP2 team"
__email__ = "xgzhao@0201@gmail.com"
__status__ = "underdeveloped"


class Pool(object):

    """
    Pool is a interface for organizing the input data according to
        the program and structural factory, and output a file as 
        input including all the info (OBJECTS) for calculations.

    tributes::
        functional: the main task to do;
        structure: the structure object; 

    methods:

        save: save the pool contained all the information
                    as you set, default name is 'test.dict';

        update: update pool according to the input file or
		     status;

        load_pool: get the detailed information in pool file;
        iter_pool: do loop the pool for different operation;
        check_pool: check the all pool status;

    """
    import re, os 

    from re import split 
    from functional import Factory 
    def __init__(self, *args, **kwargs):

        self.pool = {}

        self.__prior__ = 0
        self.__status__ = 'wait'
        self.__func__ = None 
        self.__structure__ = None

    """ job id of each job"""
    id=None

    @property
    def status(self):
        """
        Object of task status, initalize the status of tasks.
            default is wait for sumbitting.
        """
        return self.__status__ 
    @status.setter
    def status(self, value='wait'):
        if isinstance(value, str):
            if value in ['wait', 'error', 'done']:
                self.__status__ = value
            else:
                print """warnning::invalid initalized status,
                                   initalizing the tasks for launch"""
                self.__status__ = 'wait'
        else:
            
            print """warnning::invalid initalized status,
                               initalizing the tasks for launch"""
            self.__status__ = 'wait'

    @property 
    def prior(self):
        """
        Object of prior, range of integer number [0~10], the tasks 
            with maximum number would be lauched firstly.
            default is 0, all the tasks are equally to be submitted.
        """
        return self.__prior__ 
    @prior.setter
    def prior(self, value=0):
        try:
            value = int(value)
        except:
            pass
        if isinstance(value, int):
            self.__prior__ = value
        else:
            print """Warnning:: invalid input prior, integer number
                                in range of [0~10] needed."""

            self.__prior__ = 0

    @property
    def functional(self):
        """
        Object of program, type ModuleFactory.
        """
        return self.__func__
    @functional.setter
    def functional(self, value):
        #if isinstance(value, Factory):
        #    self.__func__ = value
        self.__func__ = value
        #else:
        #    raise IOError ("invalid functional object")

    @property 
    def structure(self):
        """
        Object of Structure.
        """
        return self.__structure__
    @structure.setter
    def structure(self, value):
        from structure.structure import Structure 
        if isinstance(value, Structure):
            self.__structure__ = value
        else:
            self.__structure__ = value  # should be modified (developed) %%
    
    # get the path to calculate the tasks % 
    def __div__(self, value):
        
        # % built in method to classify the input tasks.
	from copy import deepcopy 

        if isinstance(value, str):
            path = value.strip()
            self.pool[path] = {}
            self.pool[path]['prior'] = self.prior
            self.pool[path]['status'] = self.status
            self.pool[path]['structure'] = deepcopy(self.functional.structure)
            self.pool[path]['functional'] = deepcopy(self.functional) 
            
    def save(self, name='test.dict', overwrite=False):
        """
        Method aims to store input information in a binary file.

        args:
            name:: string, name of output file, default is `test.dict`;
            overwrite:: bool, overwrite the file or not, default is
			is False;
        
        """

        import cPickle as pickle

        if overwrite is True: # overwrite the old file %  
            pickle.dump((self.pool), open(name, 'wb'))
        else:
	    print """{0} already exists. Please change the parse in function `save(overwrite=True)`"""
           # print """{0} already exists. Overwrite or not (y/n)?""".format(name)
           # isave = raw_input()

           # if isave.lower() in ['y', 'yes']:
           #     pickle.dump((self.pool), open(name, 'wb'))
           # else:
           #     print "Warnning:: redefine the name of output file."
        
        del self.pool
        del self.__func__
        del self.__structure__
   
    # update all the tasks % 
    def update(self, value, merge=False, *args, **kwargs):
        """
        Method to update the pool files by using new pools, merge the files 
        or add the files.

	args:
	    value: object of Pool (dict);
            merge: bool, to merge the new Pool in `value` or not,
		   default is False;
        """
        pass

    # return the default path store the pool info % 
    def __local_pool_info(self):
        home_dir = os.environ['HOME']
        save_dir = '.local/jump2/pool/'
        default_pools_dir = os.path.join(home_dir, save_dir)
        return default_pools_dir

    # get pools under current path %
    def get_pool_info(self):
        """
        method:: to check whether there pools under current direction

        return:: a list contained the filename of pool in current 
                 direction, if not pool under current path, default
                 return None.
        """

        current_pool = []

        for p in os.walk('.').next()[2]:
            # judge current pool is under running %
            if p.endswith('.pool') and p.split('.')[0] in self.all_pools: 
                
                current_pool.append(p.split('.')[0])

        if current_pool is not []:
            
            print 
            is2select = raw_input("Do you want to check ONE taskflow? (n/y)")
            print

            if 'y' in is2select.lower():
                
                print "%% Please select on taskflow, default for all %%" 
                for p in current_pool:
                    print "%5s : %15s" % (str(current.index(p)), p)
                
                pool = input()
                
                while (not isinstance(pool, int) or pool >= len(current_pool)):
                    
                    if pool >= len(current):
                        print "invalid the index, please input again...."
                    
                    if not isinstance(pool, int):
                        print "please input the index number in [*]"

                    pool = input()
                
                current_pool = current_pool[pool]

        # return the result %
        if current_pool == []:

            return None

        else:
            return current_pool

    #walk through all the tasks contained in tasksflow %
    def __collect_status__(self, pool, status):

       	"""
	Build-in method to collect the status of all the tasks; 
	"""

        nstatus = {}
        for k in status: nstatus[k] = 0

        nstatus['name'] = pool['name']
        nstatus['path'] = pool['path']
   
        job_status = load_pool(nstatus['path'], nstatus['name'])

        for j in job_status['tasks']:
            if job_status['tasks'][j]['status'] in status:
                
                nstatus[job_status['tasks'][j]['status']] += 1
        
        return nstatus


    def __load_pool__(self):

        pass

    def __iter_pool__(self):

        pass

    def __check_pool__(self):

        pass

