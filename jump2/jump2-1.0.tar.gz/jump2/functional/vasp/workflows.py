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


""" to compute optical properties via scf + nonscf cal. """

from ..workflow import WorkFlow 


class VaspWorkflows(WorkFlow):
    """
    Class to organize the calculation workflows, including optimization,
        single point calculation and calculation of properties. Default 
        for single point calculation. 

    args::
        func: the SetVasp object;
        stdin: directory of finished results for restart next calculation;
        stdout: directory for running the calculation;
    
    methods::
        elf: ELF;
        dos: TDOS and PDOS with/without SOC;
        optics: properties relating to the frequencies dielectric matrix;
        epsilon: static dielectric matrix;
        HSE_gap: correct band gap by using the HSE06/HSE03;
        band_structure: band structure;
        carriers_mass: carrieres mass by using Boltzman or Density of States.
    
    kwargs:: contained the external parameters for VASP calculation.
    """

    def __init__(self, func=None, stdin=None, stdout=None, 
                       restart=True, *args, **kwargs):
        
	import os 
        from copy import deepcopy 
        from os.path import join, exists, abspath, basename
        from os import getcwd as get_current_direct
        from jump2.utils.io import status
        # run directory % 
        if stdout is None: 
           stdout = get_current_direct()

        if func is not None:

            vasp = deepcopy(func)  # get a copy of object % 
            # update external parameters %  
            params = {} 
            params.update(kwargs)
    
            # restart or not according to stdin derectory % 
            if stdin is not None:
                params['icharg'] = 1
                params['istart'] = 1
            else:
                params['icharg'] = 2
                params['istart'] = 0
                
            params['restart'] = restart # whether to restart the task % 
            
            os.remove(os.path.join(stdout, '.wait'))   

            # relaxation loop %
            if 'optimize' in vasp.task:
                params.update(vasp.task['optimize']['param'])
                stdin = self.relax_cell_ions(vasp, stdin, stdout, 
                                                *args, **params)
            # single point calculation %
            if abspath(stdin) != abspath(stdout+'/scf'):
                stdin = self.self_consistent_calc(vasp, stdin, stdout+'/scf', 
                                                        *args, **params)
                status.tag_success_status(stdout, 'scf', 'done', stdout+'/scf')
            # properties calculation % 
            if 'nonscf' in vasp.task and basename(stdin) == 'scf':
               for t in vasp.task['nonscf']:
                   self.property_factory(t, vasp, stdin, *args, **kwargs) 
                   status.tag_success_status(stdout, 'property'.format(t), 'done', stdout+'/{0}'.format(t))
            if os.path.exists(os.path.join(stdout, '.running')):
                os.remove(os.path.join(stdout, '.running'))   

    def property_factory(self, task, func, stdin, *args, **kwargs):

        """
        select the case of tasks
        """
        if 'optic' in task:
            self.optics(func, stdin, *args, **kwargs)

        if 'band' in task:
            self.band_structure(func, stdin, *args, **kwargs)

        if 'hse_gap' in task:
            self.HSE_gap(func, stdin, *args, **kwargs)

        if 'epsilon' in task:
            self.epsilon(func, stdin, *args, **kwargs)

        if 'elf' in task:
            self.elf(func, stdin, *args, **kwargs)

        if 'masses' in task:
            self.carriers_mass(func, stdin, *args, **kwargs)
         
        if 'dos' in task:
            self.projected_dos(func, stdin, *args, **kwargs)

    
    def optics(self, func, stdin=None, alpha=True, *args, **kwargs):
        """
        Methods to get the optical properties, including joined 
            density of orbitals states (JDOS), orbsorption (Alpha), 
            transition dipole maxtrix (TDM), as well as other relvant 
            properties of dielectric matrix with frequencies.
        """
        from copy import deepcopy 
        from os.path import join, dirname

        vasp = deepcopy(func)
     
        # basic parameters % 
        params={}
        
        params['loptics'] = True
        params['nedos'] = 3001
        params['cshift'] = 0.01
        params['npar'] = 1
        
        vasp.kpoints = 0.05

        if stdin is None:
            raise IOError ("No such derectory")
        else: 
            path = join(dirname(stdin), 'optics')
            self.calc_properties(vasp.structure, stdin, path, 
                                            *args, **params)


    def epsilon(self, func, stdin, *args, **kwargs):
        """
        Method to get static dielectric matrix. 
        """
        from copy import deepcopy 
        from os.path import join, dirname

        vasp = deepcopy(func)
     
        # basic parameters % 
        params={}
        params.update(kwargs)

        params['lepsilon'] = True
        params['nedos'] = 3001
        
        if stdin is None:
            raise IOError ("No such derectory")
        else: 
            path = join(dirname(stdin), 'epsilon')
            self.calc_properties(vasp, stdin, path, 
                                             *args, **params)

    def band_structure(self, func, stdin, num=20, *args, **kwargs):
        """
        Method to run the band structure calculations. 
        """
        from copy import deepcopy 
        from os.path import join, dirname
        from jump2.analysis.ExtractVasp.extract_band import BandStructure
        from jump2.visualizer.bandstructure import PlotBandStructure
 
        vasp = deepcopy(func)
     
        # basic parameters % 
        params={}
        params.update(kwargs)

        params['nbands'] = 2*vasp.get_nband(stdin)
        params['nedos'] = 2001
        params['algo'] = 'veryfast'
        params['lcharg'] = False
        params['prec'] = 'Normal'

	print stdin         
        kpoints, temp = vasp.get_high_symmetry_path(stdin)
        kpoint  = kpoints['suggest']  # default for suggested 
                                      # high symmetry pathway % 
        if 'all_kpoints' in args: kpoint = kpoints['all']

        path = ''
        for k in kpoint:
            # if 'hse' not in vasp.functional:
            vasp.kpoints = 'band\n{0:d}\nline mode\nreciporcal\n{1}'.format(num, kpoint[k])
            path = dirname(stdin) + '/band'
            path = join(path, k)
            self.calc_properties(vasp, stdin, path, *args, **params)
            # else:
            #    # under developments %
            #    pass

        #band = BandStructure(path=path, symmetry_path=kpoint)


    def band_edge_wave_function(self):
        pass

    def carriers_mass(self, func, stdin, temperature=298, nelect=1e-18, method='boltzman',
                                                            *args, **kwargs):
        """
        Method to get carriers masses, two methods can be used, boltzman and 
            band_directory.

        args:
            temperature:: default 298K, for Boltzman method;
            nelect:: carriers density for Boltzman method, default is 1e-18;
            method:: boltzman OR band, default is 'boltzman';

        """
        from copy import deepcopy 
        from os.path import join, dirname

        vasp = deepcopy(func)
     
        # basic parameters % 
        params={}
        params.update(kwargs)

        params['nedos'] = 3001
        params['ismear'] = -5
        
        vasp.kpoints = 0.05
        
        if stdin is None:
            raise IOError ("No such derectory")
        elif 'boltzman' in method: 
            path = join(stdin, 'carriers')
            self.calc_properties(vasp, stdin, path, 'symmetry', **params)
            vasp.boltzman(path, temperature, nelect)
        elif 'band' in method: # ('underdevelopment') % 
            pass

    def epsilon(self, func, stdin, *args, **kwargs):
        """
        Method to get projected density of states. 
        """
        from copy import deepcopy
        from os.path import join, dirname

        vasp = deepcopy(func)

        # basic parameters % 
        params={}
        params.update(kwargs)

        params['lepsilon'] = True
        params['nedos'] = 3001

        params['nedos'] = 3001
        params['ismear'] = 0

        vasp.kpoints = 0.15  # need to updated % 

        if stdin is None:
            raise IOError ("No such derectory")
        else:
            path = join(dirname(stdin), 'epsilon')
            self.calc_properties(vasp, stdin, path,
                      projected=True, *args, **params)


    def projected_dos(self, func, stdin, *args, **kwargs):
        """
        Method to get projected density of states. 
        """
        from copy import deepcopy 
        from os.path import join, dirname

        vasp = deepcopy(func)
     
        # basic parameters % 
        params={}
        params.update(kwargs)

        params['nedos'] = 3001
        params['ismear'] = 0
        params['sigma'] = 0.08

        vasp.kpoints = 0.05

        if stdin is None:
            raise IOError ("No such derectory")
        else: 
            path = join(dirname(stdin), 'pdos')
            self.calc_properties(vasp, stdin, path, 
                      projected=True, *args, **params)


    def elf(self, func, stdin, *args, **kwargs):
        """
        Method to get ELF. 
        """
        from copy import deepcopy 
        from os.path import join, dirname

        vasp = deepcopy(func)
     
        # basic parameters % 
        params={}
        params.update(kwargs)
        params['lelf'] = True
        params['nedos'] = 3001
        params['ismear'] = 0
        params['sigma'] = 0.08
        params['kspacing'] = 0.23
        
        if stdin is None:
            raise IOError ("No such derectory")
        else: 
            path = join(dirname(stdin), 'elf')
            self.calc_properties(vasp, stdin, path, *args, **params)


    def hse_gap_values(self, vasp, stdin, stdout, 
                             kpoints=None, *args, **kwargs):
        """
        Calculated the corrected band gap values by using the two steps by 
            default,
            a) calculate the band edges by using PBE functionals;
            b) calculate the band edges by using HSE functionals;
            
            if the band edges were set by using the args kpoints
            the first step was skiped. For instance, 
                kpoints = [[0., 0.5, 0.0], [0.5, 0.5, 0.5]]
        args:
            vasp:: object of the focused systems;
            kpoints:: the set points of the considered band edges;
            kwargs:: external parameters for calculation.

        return None
        """

        if kpoints is None:
            self.self_consistent_calc(vasp, stdin, stdout, functional=None)
            kpoints = self.get_band_edges(stdout).kpoints
            self.self_consistent_calc(vasp, stdin, stdout, 
                                      add_kpoints=kpoints, functional='hse')
        else:
            self.self_consistent_calc(vasp, stdin, stdout, 
                                      add_kpoints=kpoints, functional='hse')

    # relax cell shape and atomic positions % 
    def relax_cell_ions(self, vasp, stdin=None, stdout=None, overwrite=False,
                        accelerate=True, steps=3, maxsteps=5, *args, **kwargs):

        """
        To relax the cell shape and ionic positions.

        args:
            vasp:: SetVasp object for the one calculation;
            stdin:: initial direction to restart, default is None.
            stdout:: running direction;
            overwrite:: whether to overwrite the existed files, default is False;
            accelerate:: whether to accelerate the calculation by using 
                         roughly calculations;
            steps:: maximum steps for roughly calculations;
            maxsteps:: maximum steps for normal calculations;

        """
        from copy import deepcopy 
        from os.path import join, abspath
        from jump2.utils.io import status, is_exist

        count = 0
        is_relax = True   

        #if is_exist(stdout):           # stdout is exist %  
        #    s = status(stdout)
        #    if s.opt:
        #       is_relax = False

           #if overwrite is True:
           #   accelerate = True 
           #elif s.ropt:  # roughly calculation is done % 
           #   accelerate = False 
        if overwrite is True:
            accelerate = True
              
        if accelerate is True:
            self.__roughly_optimization__(vasp, count=count, 
                                          stdout=stdout, **kwargs)
            stdin = stdout + '/relax/0'
            status.tag_success_status(stdout, 'rough_opt', 'done', stdin)
        # normal optimization by using initial setting % 
        run_path, done = self.__relax__(vasp, stdin, stdout+'/relax', \
                                        overwrite, maxsteps, **kwargs)
        return abspath(run_path) 
        #if is_relax:
        #    run_path, done = self.__relax__(vasp, stdin, stdout+'/relax', \
#                                            overwrite, maxsteps, **kwargs)
        #    status.tag_success_status(stdout, 'optimization')
        #    return abspath(run_path) 

    # scf calculation % 
    def self_consistent_calc(self, func, stdin=None, stdout=None, 
                             add_kpoints=None, functional=None, 
                             *args, **kwargs):        
        """
        To running a single point of the structure. 
        """
        
        from copy import deepcopy 
        from os.path import abspath
        from jump2.analysis.ExtractVasp.basic import TotalEnergy

        vasp = deepcopy(func)  # get the copy for initial calculation % 
        
        if functional is not None:
            vasp.functional = functional
            vasp.kpoints = add_kpoints
        
        # basic parameters % 
        params={}
        params.update(kwargs)

        params['icharg'] =  1
        params['lcharg'] =  True
        params['ibrion'] = -1
        params['ismear'] = -5
        params['isif'] = 2
        params['nsw']  = 0
        
        # task options for write out WAVECAR % 
        if any(['optics', 'band']) in vasp.task \
                    or vasp.functional:

            params['lwave'] = True
        else:
            params['lwave'] = False 

        stdout = abspath(stdout)
        # set vasp input files % 
        func.setvasp_input(vasp.structure, stdout, stdin, *args, **params)

        # run vasp program % 
        vasp.run_program(stdout)

        t = TotalEnergy()


        return stdout   
   
    # nonself-consistent calculation % 
    def calc_properties(self, func, stdin, stdout=None, overwrite=True, 
                              projected=False, *args, **kwargs):

        from copy import deepcopy 
        from os import path
        
        vasp = deepcopy(func)
        
        params={}
        params.update(kwargs)

        params['icharg'] = 11
        params['istart'] = 1
        params['ibrion'] = -1
        params['isif'] = 2
        params['nsw']  = 0
        params['nelm']  = 100
        params['ismear']  = 0

        if projected is True: params['lorbit'] = 11
         
        # compute the properties % 
        vasp.setvasp_input(func.structure, stdout, stdin, overwrite, **params)
        vasp.run_program(stdout)
        

    # relax cells shape and atomic positions % 
    def __relax__(self, func, stdin=None, stdout=None, overwrite=False,
                                         maxsteps=3, *args, **kwargs):
        import os 
        from copy import deepcopy 
        from os import path 
        from jump2.structure.structure import read 
        from jump2.utils.io import status 
        
        vasp = func
        
        count = 0
        restart =False
        converaged = False
       
        # restart calculation from input % 
        if stdin is not None:
            stdin = path.abspath(stdin)
            count = int(path.basename(stdin))
            converaged = vasp.run_status(stdin, task_type='optimize')
            if converaged:
                vasp.structure = read(stdin+'/CONTCAR', type='poscar')
                return stdin, False # test restart to the former calculation % 
            restart = True 
        
        if count < maxsteps and not converaged:
            loop = True
            count += 1
        else:
            loop = False
        # running path % 
        run_path = path.join(stdout, str(count))

        # loop relaxation % 
        while (loop and not converaged):
            func.setvasp_input(vasp.structure, stdout=run_path, stdin=stdin, 
                               **kwargs) # vasp input % 
            func.run_program(run_path) # running vasp program % 
            run_path, loop = self.__relax__(vasp, run_path, stdout, overwrite, 
                                            maxsteps, **kwargs) # loop relax %   


        status.tag_success_status(stdout, 'optimization', 'done', run_path)

        return run_path, False 

    # multi-steps roughly calculation %  
    def __roughly_optimization__(self, func, count, stdout, overwrite=False, 
                                          steps=3, *args, **kwargs):
        """
        Aming the roughly optimize the structure by using low density 
        of kpoints mesh.

        Args:
            count:: the real running loop steps;
            stdout:: the running path;
            overwrite:: whether to overwrite the exsited data;
            steps:: the maximum steps to roughly optimize structure;

        return True or False
        """
        from jump2.structure.structure import read 
        from copy import deepcopy  
        import os
        
        is_converaged=None
        vasp = deepcopy(func)
       
        # external parameters % 
        params = {}
        params.update(kwargs)
        params['ediff'] = 1e-5
        params['ibrion'] = 2
        if vasp.__hasattr__('force'):
            params['ediffg'] = -0.5 + vasp.force/steps*count

        path = os.path.join(stdout, 'relax/0')

        if not os.path.exists(path):
            os.makedirs(path)

        else:
            is_converaged=vasp.run_status(path, task_type=None)
            #if is_converaged: # underdeveloping  (need add the 3 steps 
                              # converaged in the run_status calculation)%  
            func.structure = read(path+'/CONTCAR', type='poscar')
        
        # loop the rough calculation (Just for VASP5.0 or latter) %
        if count <= steps:
            loop = True
        else:
            loop = False
        
        while loop:
            
            if count > 0: overwrite = True  
            if vasp.kpoints[1] is False:
                params['kspacing'] = 0.8-(0.8-vasp.kpoints[0])/steps*count
                if 0.8 - vasp.kpoints[0] < 0.1:
                    steps = 1
            if vasp.kpoints[1] is True:
                params['kspacing'] = 0.8 - 0.8/steps*count
            
            if count == 0: 
                stdin=None
            else:
                stdin = path
                stdin=os.path.abspath(stdin)
                stdout=os.path.abspath(stdout)
            func.setvasp_input(func.structure, path, None, *args, **params)
            vasp.run_program(path)

            #if vasp.run_status(path, task_type=None): # converaged to update the structure % 
            #    vasp.structure = read(os.path.join(path, 'CONTCAR'), type='poscar')
            
            count += 1
            stdout, loop = self.__roughly_optimization__(func, count, 
                                  stdout, overwrite, steps, **params)
        
        return stdout, False
