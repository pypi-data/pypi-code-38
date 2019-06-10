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
This module defines the classes relating to structure.
"""


__author__ = "Xin-Gang Zhao"
__copyright__ = "Copyright 2017, The JUMP2"
__version__ = "1.0"
__maintainer__ = "JUMP2 team"
__email__ = "xgzhao@0201@gmail.com"
__status__ = "underdeveloped"
__date__ = "Oct 10, 2017"


import numpy as np 

class Structure(object):

    def __init__(self):
        pass

    @property
    def struct(self):
        return (self.lattice, \
                self.positions, \
                np.ones(len(self.positions)))

   
 
    @property
    def lattice(self):
        return self.__lattice
     
    @property
    def comment(self):
        return self.__comment
     
    @property
    def scale(self):
        return self.__scale
     
    @property
    def elements(self):
        return self.__elements
     
    @property
    def numbers(self):
        return self.__numbers
     
    @property
    def positions(self):
        return self.__positions
     
    @property
    def constraints(self):
        return self.__constraints
    
    @lattice.setter
    def lattice(self, value):
	self.__lattice = value 
    @comment.setter
    def comment(self, value):
	self.__comment = value 
    @scale.setter
    def scale(self, value):
	self.__scale = value 
    @elements.setter
    def elements(self, value):
	self.__elements = value 
    @numbers.setter
    def numbers(self, value):
	self.__numbers = value 
    @positions.setter
    def positions(self, value):
	self.__positions = value 
    @constraints.setter
    def constraints(self, value):
	self.__constraints = value 

    def get_atomic_numbers(self):
        return np.array(self.structure['numbers']) 
    #
    def __getitem__(self, i):
        pass  
    def get_scaled_positions(self):
        return np.array(self.structure['positions'])
    # get primary cell % 
    def get_primary_cell(self, thread=0.01):
        pass

    # get volume % 
    def get_volume(self):
        pass

    def get_cell(self):
        return np.array(self.structure['lattice'])
        #return self.get_lattice()
    # get lattice %
### class get_lattice(object):
###     a = 0 
###     b = 0
###     c = 0
###     
###     def __repr__(self):
###         return None

    # get elements % 
    def get_elements(self):
        
        return list(self.structure['elements'])

    # get total number of atoms % 
    def get_total_atoms(self):
        pass

    # get number of elements % 
    def get_num_elements(self):
        pass

    # get atomic position % 
    def get_atomic_position(self, index):
        pass

    # get coordination number % 
    def get_coordnation_number(self, index):
        pass

    # get XRD spectrum % 
    def get_xrd_spectrum(self, light=800, *args):
        pass

    # get distance between two atoms % 
    def get_distance(self, index1, index2):
        pass

    # get equal atomic position % 
    def get_equal_Wyckoff_Position(self):
        pass

    # get symmetry operations % 
    def get_symmetry_operation(self):
        pass

    # get point group % 
    def get_point_group(self, thread=0.01):
        pass

    # get space group % 
    def get_space_group(self, thread=0.01):
        pass

    # get high symmetry points and pathways % 
    def get_high_symmetry_paths(self):
        pass

    # get angle % 
    def get_angle(self, index1, index2, index3):
        pass

    # get dihedral angle % 
    def get_dihedral_angle(self, index1, index2, index3, index4):
        pass

    # get mass center % 
    def get_mass_center(self, *args):
        pass

    # get atomic number % 
    def get_atomic_number(self, *args):
        pass

    # get chemical symbol %
    def get_chemical_symbols(self):
        pass

    # get supercell % 
    def get_supercell(self, scale=[1.0, 1.0, 1.0]):
        pass

    # set element % 
    def set_atoms(self, poistion, index=None):
        pass

    # add atoms % 
    def add_atoms(self,position):
        pass

    # remove atoms % 
    def remove_atoms(self):
        pass

   ## get imaginary configurations % 
   #def get_neb_configuration(self, ini=None, fin=None, d=0.0):
   #    pass
    
    # read structure % 
    def read_structure(self, structure):
        pass

    # write structure % 
    #def write_structure(self, format='vasp', direct=True, isvasp5=True):
    def write(self, stdout, format='vasp', direct=True, **kwargs):
       
       if format is 'vasp':
           from ..utils.io import vasp_write
           vasp_write(self.structure, direct=True, **kwargs)



    
def read(name, type=None):
    from read import Read 
    obj = Structure()
    structure   = Read(name, type=type).getStructure() 
    obj.structure = structure 
    obj.comment = structure['comment']
    obj.lattice = np.array(structure['lattice'])
    if structure['type'].lower() == 'direct':
        obj.direct = True
    if len(structure['constraints']) == 0:
        obj.frozen = False
    else:
        obj.frozen = True
        obj.fz_xyz = structure['constraints']
    obj.elements = structure['elements']
    obj.num_elements = structure['numbers']
    obj.positions = np.array(structure['positions'])

    return obj

