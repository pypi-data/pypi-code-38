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

__author__ = "Xin-Gang Zhao"
__copyright__ = "Copyright 2017, The JUMP2"
__version__ = "1.0"
__maintainer__ = "JUMP2 team"
__email__ = "xgzhao@0201@gmail.com"
__status__ = "underdeveloped"
__date__ = "Oct 10, 2017"


""" global class for basic calculations with different functionals."""

class Compute(object):

    def __init__(self):

        self.functional = None

    # copy files from input path  to output path %  
    def __copy_files__(self, stdin, stdout, *args):

        """
        varbiles:
            
            stdin:: input path;
            stdout:: output path;
            args:: files name needed to be copied;
        
        return True if done
        """
        import shutil, os
        from os.path import exists, join
        
	# files to need to be copied % 
	
	if stdin == stdout:
	    return 	
        if not exists(stdin):
            raise IOError ('No such directory')

        if not exists(stdout):
	    os.makedirs(stdout)
	
	copy_files = args
	
	# copy file % 
        for f in copy_files:
	    if f is any([None, '', ' ']): continue
 
	    orgin_file = join(stdin, f)
            if exists(orgin_file):
		object_file = join(stdout, f)
                shutil.copyfile(orgin_file, object_file)
            else:
		print "Warning:: not orginal file {0}".format(f)
		pass 

        return True 

    # call the mpirun program % 
    def run_program(self, path):
        
        from ..config.cluster import Cluster
        from os.path import join
	import os 

        a=Cluster()
        
        current_path = os.getcwd()
        os.chdir(path)
        mpi=join(a.mpi_env, 'bin/mpirun')
        os.system('{mpi} -np {cores} {program} > pbs.log'.format(mpi=mpi,
                  cores=a.cores, program=self.program))     
        os.chdir(current_path)

    #need to construct a imaginary class method  % 
    #def setup(self, cluster=None, submit=False):
    def setup(self, output=False):
	pass
    def run_status(self):
        pass
    def create_script(self, path):
        """
        To create the pbs scripts
        """
        pass         

    @staticmethod
    def submit_task(path):
        """
        Project the jobs to cluster for calculating.
        """
        from ..config.cluster import Cluster
        from os.path import join
        import os, re 

        current_path = os.getcwd()

        a=Cluster()
        cmd = a.scripts['cmd'] 
        submit = cmd['submit']
        os.chdir(path)
        recall = os.popen(submit).readline()
        os.chdir(current_path)
        job_id = re.findall('[0-9]\d*',recall)[0]
        
        return job_id 
