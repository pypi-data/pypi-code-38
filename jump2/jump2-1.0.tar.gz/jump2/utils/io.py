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
 baisc method for control the input and output 
"""

__contributor__ = 'Yawen Li, Dianlong Zhao, Xingang Zhao'


import os 

def runtime():
    
    import time as tm
    return tm.strftime("%Y-%m-%d %H:%M:%S",tm.localtime(tm.time()))

def noparses():
    """
    check parses % 
    """
    import sys
    if len(sys.argv) == 1:

        return True
    else:
        return False

# basic reading class for input the structure with any type %
# ase.io.read can be used %  

def vasp_write(structure, name='POSCAR', direct=True, **kwargs):

    structure = structure.structure  
    formats=['comment','constraints','lattice','elements','numbers','type','positions']
    if not kwargs.has_key('isvasp5'): 
        pass
    
    with open(name, 'wb') as f:
        f.write(str(structure['comment'])+'\n')
        if len(structure['constraints']) == 0:
            f.write('  1.00000000\n')
        else:
            f.write('_'.join(str(c) for c in structure['constraints'])+'\n')
        for l in structure['lattice']:
            f.write('{0[0]:>20.12f} {0[1]:>20.12f} {0[2]:>20.12f}'.format(l)+'\n')
        for e in structure['elements']:f.write('{:<6s}'.format(e))
        f.write('\n')
        for n in structure['numbers']: f.write('{:<6d}'.format(n))
        f.write('\n')
        f.write(structure['type']+'\n')
        for i in structure['positions']:
            f.write('{0[0]:>20.16f} {0[1]:>20.16f} {0[2]:>20.16f}'.format(i)+'\n')
        
class CrystalRead(object):
    """
    class CrystalReand for get input structure 

    tributes:
        structure::  a class Atoms from ase.io
        elements::  get the species for organize the potcar etc.

    method:: 
        get_elements:: for get the elements from readin structure.
    """

    from ase.io import read 
    def __init__(self, structure):
        
        self.structure = read(structure)
        self.elements =  self.get_elements()

    def get_elements(self):

        symbols = self.structure.get_chemical_symbols()
        elements =  list(set(symbols))
        elements.sort(key=symbols.index)
        return elements


def pre_cluster_info(path, head, mpi, lib):
    
    import cPickle as pickle 
    if head and mpi and lib:
        
        pbs = '\n'.join([head, mpi, lib])
        pickle.dump((pbs),(open(path+'/.rqcluster_info', 'wb')))

    elif head is None and mpi is None and lib is None:
        (pbs) = pickle.load(open(path+'/.rqcluster_info', 'rb'))

    return pbs 
# create the head the script of the pbs % 
def get_manager(path, cluster=None):
	
            
    pbs=None
    mpiprogram=None
    relatelibs=None

    if not is_exist(path+'.rqcluster_info'):
        if pbs_manager in default_managers:
            pbs= default_managers[pbs_manager]
        else:
            pbs='#!/bin/bash\n'
        #pbs = pbs.format(cluster_info[0],cluster_info[1],cluster_info[2])
        mpiprogram=path_mpi
        relatelibs=path_libs

    pbs = pre_cluster_info(path, pbs, mpiprogram, relatelibs)
    
    return pbs 
    #return (pbs, mpiprogram, relatelibs)


    
# prepare the input files for the program % 
def output_input(outdir, pool, output):
    
    path_root = os.path.abspath(pool['folder'])
    path_run = os.path.join(path_root, outdir)
     
    pool['functional'].outdir = path_run 
    pool['functional'].structure = pool['tasks'][outdir]['structure']

    pool['functional'].setup(output)

def get_all_pools():

    """
    method:: get all the pool under this user.
    """

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

def collect_status(pool, status):
   
    nstatus = {}
    for k in status: nstatus[k] = 0

    nstatus['name'] = pool['name']
    nstatus['path'] = pool['path']

    job_status = load_pool(nstatus['path'], nstatus['name'])

    for j in job_status['tasks']:
        if job_status['tasks'][j]['status'] in status:
            
            nstatus[job_status['tasks'][j]['status']] += 1
    
    return nstatus

# return the default path store the pool info % 
def local_pool_path():
    home_dir = os.environ['HOME']
    save_dir = '.local/jump2/pool/'
    default_pools_dir = os.path.join(home_dir, save_dir)

    return default_pools_dir

class status(object):
    """
    Class to show the status of the jobs.
    """
    def __init__(self, path=None):
       
        self.__rough_optimization__ = False 
        self.__optimization__ = False 
        self.__scf__ = False 
        self.__property__ = False 

	if path is None: 
	   path = os.getcwd()
        
        path = os.path.join(path, '.success')
        if os.path.exists(path):
           with open(path, 'r') as f:
               while True:
                   line = f.readline()
                   if not line: break 
                   if line.startswith('rough'):
                       if line.split()[2] == 'done':
                           self.__rough_optimization__ = True
                   if line.startswith('opt'):
                       if line.split()[2] == 'done':
                           self.__optimization__ = True
                   if line.startswith('scf'):
                       if line.split()[2] == 'done':
                           self.__scf__ = True
                   if line.startswith('property'):
                       if line.split()[2] == 'done':
                           self.__property__ = True

    @property
    def ropt(self):
        
	return self.__rough_optimization__ 
   
    @property
    def opt(self):
	return self.__optimization__ 
    
    @property
    def scf(self):
	return self.__scf__ 
    
    @property
    def prop(self):
	return self.__property__
   
    @staticmethod 
    def check_status(path):
        
        spath = os.path.join(path, '.success')
        wpath = os.path.join(path, '.wait')
        rpath = os.path.join(path, '.running')
        #if os.path.exists(rpath):
        #    os.system('rm '+wpath)
        #else:
        #    return '.wait'
        if os.path.exists(spath):
            os.system('rm '+rpath)
            os.system('rm '+wpath)
            return 'success' 
        else:
            return 'wait' 
          
    @staticmethod
    def tag_success_status(path, value, status, stdout):
        
	path = os.path.join(path, '.success')
	with open(path, 'a') as f:
           f.write("{value}  {status} {path}\n".format(
                   value=value, status=status, path=stdout))
        #os.system('rm {path}/.wait'.format(path=stdout)) 
        #os.system('rm {path}/.running'.format(path=stdout)) 

def is_exist(path):

    """
    whether the direction is exist;

    return True
    """
    if os.path.exists(path):
        return True 
    else:
        return False 

#   def create_pool(name, overwrite=False):

#       "create input according name.input" 
#      
#       name = name +'.pool'
#       pool = {}

#       pool['script'] = None
#       pool['func'] = None
#       pool['folder'] = None
#       pool['tasks'] ={}

#       if is_exist(name) and overwrite:
#           pass

#       elif not is_exist(name):
#           import sys
#           path = os.getcwd()
#           sys.path.append(path)
#           from input import jump_input 
#           a = jump_input()
    
def load_pool(path, name):

    import cPickle as pickle 
    import fcntl 
    p = None
    fpath = os.path.join(path, name)
    if is_exist(fpath):
        try:
            with open(fpath, 'rb') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                p = pickle.load(f)
                fcntl.flock(f,fcntl.LOCK_UN)
                f.close()
        except:
            raise IOError ('cannot open the pool file.')
    return p 
        
class Control(object):

    """
    Control to sumbit/kill the jobs.

    """

    def __init__(self, pool, tasks, max_njobs=10, *args, **kwargs):

        self.check_status()  # check all the jobs in the pool.
        self.submit_tasks()  # submit jobs in the tasks.


    def check_status(self):


        """
        Check the pool, tasks etc.
        """

        pass

    def submit_tasks(self):

        """
        Submit the jobs with wait status.
        """
        
        pass

    def kill(self,jobid):
        """
        Kill the given jobs.
        """
        pass 


def iserror(path):
    if os.path.exists(path+'/.error'):
        return True
    else:
        return False 

def iswait(path):
    if os.path.exists(path+'/.wait'):
        return True
    else:
        return False 

def isrunning(path):
    if os.path.exists(path+'/.running'):
        return True
    else:
        return False 

def isdone(path):
    """
    whether the task is done
    """

    if os.path.exists(path+'/.done'):
        return True 
    else:
        return False     


class vaspio(object):
    """
    Class for output the baisc file for VASP calculation.

    method::
        write_symmetry:: SYMMETRY contained rotation operations;
        write_poscar:: POSCAR contained lattice and atomic positions;
        write_incar:: INCAR contained control parameters;
        write_potcar:: POTCAR contained atomic psudopotentials;
        write_kpoints:: KPOINTS contained kponit mesh;
        write_kernel:: vdw_kernel.bindat contained experimental parameters;
    """
    import shutil

    @classmethod
    def write_symmetry(cls, structure, stdout=None):
        """
        Output the SYMMETY files for calculate the carriers masses 
            by using Boltzmann method.

        args:
            structure:: Structure object contained the methods get_cell()

            stdout:: the output direction of SYMMETY
        """
        from spglib import get_symmetry
        from os.path import join 

        path = join(stdout, 'SYMMETRY')
        rotation = get_symmetry(structure)
        with open(path, 'wb') as f:
            f.write("{:>12d}".format(len(rotation)))
            for rot in rotation:
                for k in rot:
                    f.write("{:>16.8f} {:>16.8f} {:>16.8f}".format(k[0],k[1], k[2]))
                f.write('\n')
        f.close()


    @classmethod
    def write_poscar(cls, poscar, stdout=None):

        vasp_write(poscar, stdout+'/POSCAR', direct=True)

    @classmethod
    def write_potcar(cls, potcar, stdout=None):

        """
        method:: Output the POTCAR in the given direction;

              :param potcar: a dict include the basic info; 
              :param stdout: object direction of POTCAR;

        return True/False
        """

        lines = ''
        with open(stdout+'/POTCAR', 'w') as f:

            for i  in xrange(len(potcar['species'])):
                fi = open(potcar['path'][i],'r')
                lines += ''.join(fi.readlines())
                fi.close()

            f.write(lines)
            f.close()

    @classmethod
    def write_kpoints(cls, kpoints, stdout=None):
        """
        write out the KPOINTS files if kspacing parameter is None.

        :param kpoints: the object of the kmesh;
        :param stdout: the object path;

        :return: kspacing values if exists.
        """
        if isinstance(kpoints, float):
            return kpoints

        if isinstance(kpoints, str):

            with open(stdout+'/KPOINTS','w') as f:
                f.write(kpoints)
                f.close()

    @classmethod
    def write_kernel(cls, stdout=None):
        """Prepare the vdw_kernel"""

        path = path_vdw_kernel + '/vdw_kernel.bindat'


        if os.path.exists(stdout) is False:
            os.mkdir(stdout)

        if os.path.isabs(stdout) is True:
            shutil.copy(path, stdout)

        else:
            print 'ERROR: The input path should be an absolute path.'

    @classmethod
    def write_incar(self, incar, stdout=None, *kwargs):
        """
        function: output the INCAR file with format: key = value.
        :param name: output file name, type: string
        :param parses: INCAR input parameters. type: dict
        :param kwargs: external parameter.
        """

        format_incar=('basic input',['system', 'prec', 'istart', 'icharg', 'ispin'], 
         'write flags',['lwave', 'lcharg','lvtot', 'lvhar', 'lorbit'],
         'electronic',['encut','nelm', 'ediff', 'lreal', 'algo', 'amin', 'iddgrid'],
         'ionic relaxation',['isif', 'ibrion', 'ediffg', 'nsw', 'isym'],
         'dos related', ['ismear', 'sigma'],
         'parallel control', ['lplane','npar'],
         'property related',[])

        if isinstance(incar, dict) is True:
            for key in incar:
                if incar[key] == None:
                    print "Error: The value of the key '%s' \
                                    shouldn't be None" % key
                    incar.pop(key)

                elif incar[key] == '':
                    print "Error: The key '%s' should have \
                                            a value." % key
                    incar.pop(key)

            with open(stdout+'/INCAR', 'w') as output:
                output.writelines([
                "%-{0}s = %s\n".format(str(len(item))) % (item[0].upper(), item[1])
                                   for item in incar.items()])
                output.close()
        else:
            print "Error: The type of input parameter should be 'dict'"


class gaussainio(object):
    
    classmethod
    def write_input(cls, com, direct=False):
        pass

