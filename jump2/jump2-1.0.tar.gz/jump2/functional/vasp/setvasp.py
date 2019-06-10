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

from jump2.functional.compute import Compute
#from workflows import VaspCalculator


__author__ = "Xin-Gang Zhao"
__copyright__ = "Copyright 2017, The JUMP2"
__version__ = "1.0"
__maintainer__ = "JUMP2 team"
__email__ = "xgzhao@0201@gmail.com"
__status__ = "underdeveloped"
__date__ = "Oct 10, 2017"


"""
This module defines the classes relating to structure.
"""

#class SetVasp(Compute, VaspCalculator):
class SetVasp(Compute):
    """
    cls:: Prepare the input files for a single calculation via VASP by
          using the default task and customized parameters.
          
          supporting tasks:

          1) optimize: optimize the cell by relaxing the cell shape/volume,
             one can detailed set the optimization by add more keywords,
             for instance,
              ions :: refers to ISIF = 2;
              shape ions volume :: refers to ISIF = 3;
              shape ions  :: refers to ISIF = 4;
              volume ions :: refers to ISIF = 5;
              shape volume :: refers to ISIF = 6;
              volume :: refers to ISIF = 7;
          2) scf: self-consistent calculation,i.e., get charge density of ground 
             states;
          3) nonscf: nonself-consistent calculation, i.e., properties calculations
             such as optics, carriers masses, epsilon, dos, band structures, etc.
             a).band: calculating the band structure;
             b).dos: caculating the dos;
             c).optics: calculating the dielectic matrix with frequencies;
             d).epsilon: calculating the static dielectric constants;
             e).carriers: carriers masses (under develop);
             f).dynamic: calculating the dynamic by first pricinple,(under developed)
                   dynamic_nvt: 
                   dynamic_nve:
                   dynamic_npt: 
         
    tributes:
        
        functional:: the functional selected for calculation, default DFT
                     (determined by the psudopotentials LDA/PBE etc.)
                     Avaible functionals:
                     a) HSE : hybrid function
                     b) G0W0: green wavefunction
                     c) MBJ: 
                     
                     All above functionals can calculated with spin orbital 
                     coupling (SOC).
                     For example, 
                         self.functional = HSE06, 0.25
                         self.functional = HSE06, 0.20, SOC
                         self.functional = MBJ

    
        task:: the basic tasks to do, you can chose shape/volume/ions/property
               or the combination of them.
               For example,
                   self.task = shape volume ions
                   self.task = shape volume ions optics

        vdw :: Van der Waals(vdw) functional to select, supporting:
               optB86b-vdw, optB88-vdw, D2, DF2, PBE RVV10(only for >vasp5.4) etc. 
               Among them, only D2 depends on the specices.
               For example,
                   self.vdw = optb86
               You can also set the DIY vdw by add the params in a dict.
               For example,
                   self.vdw = optb86, {'PARAM1':0.1000}

        kpoints:: kmesh for crystal calculation for VASP.
                Set the KSPACING or KPOINTS.
                You can use two modes, 
                For instance,
                    self.kpoints = 0.25 
                    (for setting kspacing = 0.25)
                .OR. 
                    self.kpoints = 'test\n0\nG\n6 6 6\n0 0 0'
                other modes,
                    Gamma
                    Cartesian
                    Monkhorst
                    Line
                can also be used.

        plusU:: for considering the hubbardU. set format:
                element = [U, J, orbital], for example, [4, 0, 'd']
               
    """
    
    def __init__(self):

        super(SetVasp, self).__init__()
        self.functional = None
        self.outdir = None
        self.structure = None
        self.energy = 1e-4
        self.force = 1e-2
        self.program=None
        self.__tasks__ = None
        self.__kpoints__ = None
        self.__vdw__ = None
        self.__ispin__ = None
        self.__ldau__ = None


    #set tasks %
    @property
    def task(self):
        """
        what calculations you want to do (relax/property)?

        a). options: [shape, ions, volume] to relax cell including shape/volume;
        b). options: ['optics', 'dos', 'epsilon', 'm_eh', 'band', 'gap'] to get
                     the baisc properties via scf/nonscf calculations;
        """

        return self.__tasks__

    #set vdw functional %
    @property
    def vdw(self):
        """
        Add van der Waals functional. Avalible functionals options:
            a). optB86b-vdw
            b). optB88-vdw
            c). D2
            d). DF2
            e). RVV10

        """
        return self.__vdw__

    #tribute of kpoints
    @property
    def kpoints(self):
        """
        Setting kpoints mesh for crytalline calculation:

        You can set by,
            self.kpoints = 0.25,
        .OR.
            self.kpoints = 'test\n0\nG\n6 6 6\n0 0 0'
        """
        return self.__kpoints__

    # plus U %
    @property
    def plusU(self):

        """
        PlusU for heavy elements, default setting are avalible
        (See Stephan Lanny) if you don't know the suitable value
        for the elements.

        You can set:
            self.ldaU = True, 'Fe'
        .OR.
            self.ldaU = True, 'Fe', 'Mo'
        .OR.
            self.ldaU = True, {'Fe':(4,'d'), 'Mo':(3,'d')}
        """

        return self.__ldau__

    #spin %
    @property
    def ispin(self):
        """
        Spin orbital to be considered, default is 1;
        if self.magnetic is True, ispin = 2;
        if spin orbital coupling was considered, ispin = 1;
        """
        return self.__ispin__

    # setting the magnetic moments %
    @property
    def magnetic(self):
        """
        Initial the magnetic moments, default is used set in VASP,
        i.e.,
        when ISPIN = 2,
            magnetic for each atoms: 1.0,
            i.e.,
            MAGMOM = num_atom*1.0
        when non-colinear magnetic systems (SOC),
            magnetic for each atoms and x/y/z direction: 1.0,
            i.e.,
            MAGMOM = 3*num_atom*1.0
        """

        if self.__magnetic__ is not None:
            self.__ispin__  = 2

        return self.__magnetic__

    @magnetic.setter
    def magnetic(self, value):

        self.__magnetic__ = {'MAGMOM':value}


    def get_nband(self, path):
        """
        Get the total nbands of the whole systems.
        return a integer number.

        args:
            path:: the running direction.
        """
        from os.path import join
        import os

        path = join(path, 'OUTCAR')
        bands = os.popen('grep NBANDS {path}'.format(path=path)).readline()
        bands = int(bands.split()[-1])

        return bands

    def setvasp_input(self, structure, stdout, stdin=None, restart=False,
                            overwrite=False, *args, **kwargs):

        """
        Organizing the input files, e.g. INCAR/POSCAR/POTCAR/KPOINTS etc.

        args::
            structure: the initial structure;
            stdout: the running direction;
            stdin: the former calculation results;
            restart: to restart the calculation in running/former direction;
            overwrite: overwrite input files in running direction;

        external args:

            symmetry:: options for write SYMMETRY files for Boltzman mass;
            primary::  options get primary crystal for calculations;


        kwargs::
            external parameter for INCAR.
        """
        import os
        from jump2.utils.io import vaspio, is_exist
        from format_incar import default_incar
        from setpotcar import SetPotcar
        from setvdw import SetVdw
        from jump2.structure.structure import read
        from copy import deepcopy

        # restart files %
        if restart is True:
            copyfile = ['POTCAR', 'CHG', 'CHGCAR', 'vdw_kenerl.bindat',
			'KPOINTS','WAVECAR']
            copyfile += list(args)
        else:
            copyfile = None

        # judge the existed results %
        if is_exist(stdout):
            if restart is True:
                if overwrite is True:
                    if self.run_status(stdout):
                        structure = read(os.path.join(stdout, 'CONTCAR'), type='poscar')
                    else:
                        structure = read(os.path.join(stdout, 'POSCAR'), type='poscar')
                    stdin = None
        elif stdin is not None:
                if restart is True:  # the former results are needed %
                    if self.run_status(stdin):
                        structure = read(os.path.join(stdin, 'CONTCAR'), type='poscar')

        elements = structure.elements        # get species in the structure %
        incar = default_incar                # basic INCAR parameters %
        incar['ediff'] = self.energy         # updated energy threshold %

        if self.__hasattr__('encut'):
            incar['encut'] = self.encut      # updated cutoff energy %
        else:
            incar['encut'] = 1.3

        if stdin is not None and restart:                 # (under developed)
            self.__copy_files__(stdin, stdout, *copyfile) # copy the input files %
            #pass
        else:
            self.potcar = SetPotcar().setpotcar(elements)    # get the potcar %
            if self.__hasattr__('vdw'):
                vdw = SetVdw(self.vdw, elements).vdw         # get the vdw %
                incar.update(vdw['params'])
            if self.__hasattr__('ldaU'):
                incar.update(self.__set_hubbardU(elements))  # get hubbardU values %
            if self.__hasattr__('magnetic'):
                incar.update(self.magnetic)                  # get magnetic moments %

        # update force thread only for optimization %
        if self.task['optimize'] is not []:
            incar['ediffg'] = self.force*-1.0
        else:
            incar.pop('ediffg')

        # update kpoints mesh %
        if self.kpoints[1] is False: # kpoints mesh %
            incar['kspacing'] = self.kpoints[0]

        # update cutoff energy %
        if incar['encut'] < max(self.potcar['enmax']):
            if int(incar['encut']) in range(1,11):
                incar['encut'] *= max(self.potcar['enmax'])
            # default setting is the 1.3 times ENMAX %
            else:
                incar['encut'] = max(self.potcar['enmax'])*1.3

        # DIY parameter %
        external_parameters = self.__dict__
        eparameters = deepcopy(external_parameters)
        for p in external_parameters:
            if '__' in p: eparameters.pop(p)
        eparameters.pop('functional')
        eparameters.pop('structure')
        eparameters.pop('program')
        eparameters.pop('force')
        eparameters.pop('energy')
        eparameters.pop('outdir')
        eparameters.pop('potcar')
        #if self.__hasattr__('potcar'): eparameters.pop('potcar')

        # update the parameters %
        incar.update(eparameters)  # set by yourself %
        incar.update(kwargs)

        #output the vasp input files %
        if not is_exist(stdout): os.makedirs(stdout)
        vaspio.write_poscar(structure, stdout)
        if 'symmetry' in args:
            vaspio.write_symmetry(structure, stdout)
        if not stdin:
            vaspio.write_potcar(self.potcar, stdout)
            if self.__hasattr__('vdw') and vdw['type'] is not 'D2':
                vaspio.write_kernel(stdout)
        if self.kpoints[1]:
            vaspio.write_kpoints(self.kpoints[0], stdout)
            if 'kspacing' in incar:
                incar.pop('kspacing')
        vaspio.write_incar(incar, stdout)

    ###
    def calculator(self, vasp, path):

        from workflows import VaspWorkflows

        #VaspWorkflows(vasp, stdout=path)
        VaspWorkflows(vasp)

    # get the high symmetry path according to the input structure %
    def get_high_symmetry_path(self, stdin):
        """
        To get the high symmetrized pathway for band structure
        calculation.

        args:
           path:: the absolute path of scf calculation;

        return: split line-mode reciporical kpoints;
                for instance, {'G-X': '0. 0. 0. !\Gamma \n0.5 0. 0. ! X'}
        """

        from  ..high_sym_kpath import HighSymmKpath
        from jump2.structure.structure import read
        import os
        #from ase.io import read 

        kpath = {'suggest':{},
                 'all':{}}

        structure = read(os.path.join(stdin, 'CONTCAR'), type='poscar')

        c = HighSymmKpath()
        c.get_HSKP(structure.struct)
        kpoint = c.kpath

        count = 0
        for p in kpoint['Path']:
            for i in xrange(len(p)-1):
                k1 = '{0[0]:>16.8f} {0[1]:>16.8f} {0[2]:>16.8f} ! {1}'.format(\
                     kpoint['Kpoints'][p[i]], p[i])

                k2 = '{0[0]:>16.8f} {0[1]:>16.8f} {0[2]:>16.8f} ! {1}'.format(\
                     kpoint['Kpoints'][p[i+1]], p[i+1])

                A = p[i]
                B = p[i+1]
                if 'Gamma' in p[i]: A = 'Gamma'
                if 'Gamma' in p[i+1]: B = 'Gamma'
                key = '{0}-{1}'.format(A,B)
                kpath['all'][key] = k1+'+\n'+k2
                if count == 0: kpath['suggest'][key] = k1+'+\n'+k2
            count += 1
                #    """{0[0]:>16.8f} {0[1]:>16.8f} {0[2]:>16.8f} ! {2}\n{1[0]:>16.8f} {1[1]:>16.8f} {1[2]:>16.8f} ! {3}""".format(\
                #       kpoint['Kpoint'][p[i]], kpoint['Kpoint'][p[i+1]],p[i],p[i+1])

        path_points = list(kpoint["Path"][0])
        for i in range(0, len(path_points)):
            if 'Gamma' in path_points[i]:
                path_points[i] = 'Gamma'
        path = []
        for i in range(1, len(path_points)):
            path.append(path_points[i-1] + '-' + path_points[i])

        return kpath, path
        #return {'Gamma-X': '0. 0. 0. !\Gamma \n0.5 0. 0. ! X'}, ['Gamma', 'X']


    def run_status(self, path, task_type='scf'):

        """
        To check the job status.

        Args:
            path: running direction;
            task_type: the task type option [optimize, scf, nonscf]

        return True if succeed .OR. False if not finished.
        """
        import os
        from os.path import join

        isscf_convg = False
        isopt_convg = False
        dlabel='General timing and accounting informations for this job:'
        slabel='aborting loop because EDIFF is reached'
        olabel=' reached required accuracy '

        results = join(path, 'OUTCAR')
        if os.path.exists(results):
            is_finished = os.popen("grep '{key}' {path}".format(key=dlabel,\
                                   path=results)).readline()
            if is_finished != '':
                if os.path.exists(path+'/.running'):
                    os.remove(path+'/.running')
                with open(path+'/.succeed', 'wb') as f:
                    f.write('')
            else:
                if os.path.exists(path+'/.running'):
                    return 'running'
                else:
                    with open(path+'/.error', 'wb') as f:
                        f.write(path)
                    return False

            if task_type in ['scf', 'nonscf']:
                convg = os.popen('grep "{key}" {path}'.format(key=slabel, \
                                path=results)).readline()

                if convg != '': isscf_convg = True

            if task_type == 'optimize':
                convg = os.popen('grep "{key}" {path}'.format(key=olabel,\
                                path=results)).readline()

                if convg != '': isopt_convg = True

            if isscf_convg or isopt_convg:
                return True

            elif task_type is None and is_finished != '':
                return True
            else:
                return False
        else:
            return False

    @magnetic.deleter
    def magnetic(self):
        self.__magnetic__ = None

    @ispin.setter
    def ispin(self,value=None):

        if value > 1 or value is None:
            self.__ispin__ = 2
        else:
            self.__ispin__ = 1
    @ispin.deleter
    def ispin(self):
        self.__ispin__ = None

    @task.setter
    def task(self, value=None):
        if value is None:
            value = 'scf'
        self.__tasks__ = self.__process__(value)

    @task.deleter
    def task(self):
        self.__tasks__ = None

    @kpoints.setter
    def kpoints(self, strings=None, *args):

       ## is/not add the vdw functionals %
        kpoint = None
        if strings is None:
            #set fot default kpoints %
            kpoint = '\n0\nAuto\n15\n', True

        else:
            # for KSPACING setting %
            if isinstance(strings, float):
                if strings > 0. and strings < 1.0:
                    kpoint = strings, False
                else:
                    kpoint = 0.25, False

            # for KPOINTS setting %
            if isinstance(strings, str):

                #for Gamma or Monk %
                if list(strings.split('\n')[2])[0].upper() == 'G' or \
                   list(strings.split('\n')[2])[0].upper() == 'M':
                    if len(strings.rstrip().split('\n')) == 5:
                        kpoint = strings.rstrip(),True

                #for Auto %
                elif list(strings.split('\n')[2])[0].upper() == 'A':
                    if len(strings.rstrip().split('\n')) == 4:
                        kpoint = strings.rstrip(), True

                # for Caterian or K %
                elif list(strings.split('\n')[2])[0].upper() == 'C' or \
                     list(strings.split('\n')[2])[0].upper() == 'K':
                    if  len(strings.rstrip().split('\n')) == 7:
                        kpoint = strings.rstrip(),True

                # for Line %
                elif list(strings.split('\n')[2])[0].upper() == 'L' and \
                     list(strings.split('\n')[3])[0].upper() == 'R':
                    kpoint = strings.rstrip(), True

                #invalid setting %
                else:
                    raise IOError\
                    ("type_kpoints {0} are unknown".format(strings))
        self.__kpoints__ = kpoint

    @kpoints.deleter
    def kpoints(self):
        self.__kpoints__ = None

    @vdw.setter
    def vdw(self, vdwfunc):
        #def vdw(self, vdwfunc=None, *args):
        #under developed, DIY vdw functional should be considered %
        if isinstance(vdwfunc, str):
            vdwfunc = vdwfunc.lower()
            if 'd2' in vdwfunc:
                self.__vdw__ = 'd2'
            elif 'b86' in vdwfunc:
                self.__vdw__ = 'b86'
            elif 'b88' in vdwfunc:
                self.__vdw__ = 'b88'
            elif 'df2' in vdwfunc:
                self.__vdw__ = 'df2'
            else:
                raise NoFoundError\
            ('{0} vdw functional was not found'.format(str))

    @plusU.setter
    def plusU(self, *args):

        ldau = args[0]
        temp = {}
        # plus U by self-defined %
        if len(ldau) >=1:
            if ldau[0] is False:
                self.__ldau__ = None

            elif ldau[0] is True:
                for e in ldau[1:]:
                    if type(e) is str:
                        temp[e] = self.__set_hubbardu(e)
                    elif type(e) is dict:
                        temp.update(e)

                self.__ldau__ = ('PlusU', temp)
            else:
                self.__ldau__ = None

    @plusU.deleter
    def plusU(self):
        self.__ldau__ = None

    # set hubbardU %
    def __set_hubbardU(self, elements=None):

        from hubbardU import default_plusU

        hubbardu = {}              # initialize hubbardU %
        hubbardu['ldau'] = True    # set True for calcualtion %
        orbitalU=['s','p','d','f'] # oribtals for considered %
        if self.plusU is not None:
            plusU = self.plusU     # DIY parameters %
        else:
            return None

        # case for default hubbardU %
        if plusU[1] is {}:
            hubbardu.update(default_plusU(elements))
            return hubbardu
        # case for DIY hubbardU %
        else:
            U = []
            J = []
            types = []
            for e in elements:
                if e in plusU:
                    U.append(plusU[e][0])
                    J.append(0)
                    types.append(orbitalU.index(plusU[e][1]))
                else:
                    U.append(0)
                    J.append(0)
                    types.append(2)

            hubbardu['ldauu'] = ' '.join(U)
            hubbardu['ldauj'] = ' '.join(J)
            hubbardu['ldautype'] = ' '.join(types)

            return hubbardu

    # organize the input tasks %
    def __process__(self, tasks):
        """method:: orginize the tasks according to the input."""

        basic_tasks = {}
        functionals = self.functional

        basic_tasks['optimize'] = []
        basic_tasks['scf'] = ['scf']
        basic_tasks['nonscf'] = []

        # case default is paw_pbe %
        if functionals is None:
            basic_tasks['func'] = 'paw_pbe'
        else:
            if isinstance(functionals, str):
                functionals = functionals.lower()
            else:
                raise NoFoundError\
                    ('unrecognized functional {0}'.format(str(functional)))
            # case HSE %
            if 'hse' in functionals:
                basic_tasks['func'] = 'hse'
            # case MBJ %
            elif 'mbj' in functionals:
                basic_tasks['func'] = 'mbj'
            # case gw0 %
            elif 'gw' in functionals:
                basic_tasks['func'] = 'gw'
            # case pbesol %
            elif 'pbesol' in functionals:
                basic_tasks['func'] = 'pbesol'
            # case pbe0 %
            elif 'pbe0' in functionals:
                basic_tasks['func'] = 'pbe0'
            # case soc %
            if 'soc' in functionals:
                basic_tasks['func'] += ' with soc'
        # set for default tasks %
        if tasks is None:
            return basic_tasks

        else:
            if isinstance(tasks, str):
                tasks = tasks.lower()
        # for optimize calculation %
        if 'volume' or 'shape' or 'ions' in tasks:
            # case IBRION = 3 %
            if 'volume' and 'shape' and 'ions' in tasks:
                basic_tasks['optimize'].append(3)
            # case IBRION = 4 %
            elif 'volume' and 'ions':
                basic_tasks['optimize'].append(4)
            # case IBRION = 5 %
            elif 'shape' and 'ions':
                basic_tasks['optimize'].append(5)
            # case IBRION = 6 %
            elif 'shape' and 'volume':
                basic_tasks['optimize'].append(6)
            # case IBRION = 7 %
            elif 'volume' in tasks:
                basic_tasks['optimize'].append(7)
            # case IBRION = 2 %
            elif 'ions' in tasks:
                basic_tasks['optimize'].append(2)
        # property band %
        if 'band' in tasks:
            basic_tasks['nonscf'].append('band')
        # property dos %
        if 'dos' in tasks:
            basic_tasks['nonscf'].append('dos')
        # property optic %
        if 'optic' in tasks:
            basic_tasks['nonscf'].append('optics')
        # property carrier %
        if 'carrier' in tasks:
            basic_tasks['nonscf'].append('carriers')

        #self.detailed_params()

        return self.__detailed_params(basic_tasks)

    def __detailed_params(self, task):
        t={}
        if task['optimize'] != []:
            if 2 in task['optimize']: 
                t['type'] = 'ions'
                t['param']  = {'isif':2, 'ibrion':1, 'nsw':30} 

            if 3 in task['optimize']: 
                t['type'] = 'full_relax'
                t['param']  =  {'isif':3,'ibrion':2, 'nsw':30}

            if 4 in task['optimize']: 
                t['type'] = 'fix_shape'
                t['param']  = {'isif':4,'ibrion':1,'nsw':30}

            if 5 in task['optimize']: 
                t['type'] = 'fix_volume'
                t['param']  = {'isif':5,'ibrion':1, 'nsw':30}

            if 6 in task['optimize']: 
                t['type'] = 'fix_ions'
                t['param']  = {'isif':6,'ibrion':1,'nsw':30}

            if 7 in task['optimize']: 
                t['type'] = 'fix_shape_ions'
                t['param']  = {'isif':7,'ibrion':1, 'nsw':30}

            task['optimize'] = t

        if 'scf' in task['scf']:
            task['scf']={'type':'scf', 'param':{'ibrion':-1, 'icharg':1,'isif':2}}  
        if task['nonscf'] !=[]:
            tmpnonscf ={}
            if 'band' in task['nonscf']:
                tmpnonscf['band'] = {'type':'band', 'param':{'ibrion':-1, 'icharg':11,'isif':2, 'nband':200}} 
            if 'dos' in task['nonscf']:
                tmpnonscf['dos'] = {'type':'dos', 'param':{'ibrion':-1, 'icharg':11,'isif':2, 'nedos':3001}} 
            if 'optic' in task['nonscf']:
                tmpnonscf['optics'] = {'type':'optics', 'param':{'ibrion':-1, 'icharg':11,'isif':2, 'nedos':3001}} 
            #if 'carrier' in task['nonscf']:
            #    tmpnonscf['carrier'] = {'type':'dos', 'param':{'ibrion':-1, 'icharg':11,'isif':2, 'nedos':3001}} 

            task['nonscf'] = tmpnonscf       

        return task
            
    
    def __hasattr__(self, value):
    
        try:
            self.__getattribute__('value')
        except:
            return False
        return True 
      # if self.__hasattr__('ldau'):
      #    self.pop('ldau') 

      # if 'default' in args: 
      #     self.__setattr__('plusu', 'default')
      # elif kwargs: 
      #     self.__setattr__('plusu', kwargs)
    
#=====================================================================
# need to construct a imaginary class method  % 
#   def setup(self, cluster=None, submit=False):

#       # update incar % 
#       self.set_params()
#       
#       # output files for calulcation % 
#       
#       #self.vasp_output()
#       if submit is True:
#           for motion in ['optimize', 'scf', 'nonscf']:
#               if len(self.task['motion']) > 0: 
#                   self.vasp_output(self.outdir+'/'+motion)
#       else:
#           self.vasp_output(self.outdir+'/'+'optimize')
#           self.create_scripts(self.outdir, cluster)

#   def create_scripts(self, path, cluster):

#       pbs = get_manager(path, cluster)
#       with open(path+'/task.pbs', 'wb') as f:

#           f.write(pbs)

