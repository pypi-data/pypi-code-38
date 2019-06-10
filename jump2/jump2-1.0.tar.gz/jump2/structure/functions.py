# coding: utf-8
# Copyright (c) JUMP2 Development Team.
# Distributed under the terms of the JLU License.


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


class StructureOperation(object):
    
    def get_cell(self):
        return self.lattice.vectors  
   
    # get primary cell % 
    def get_primary_cell(self, thread=0.01):
        pass

    # get volume % 
    def get_volume(self):
        pass

    # get total number of atoms % 
    def get_total_atoms(self):
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
    def get_angle(self, a, b, c):
        pass

    # get dihedral angle % 
    def get_dihedral_angle(self, a, b, c, d):
        pass

    # get mass center % 
    def get_mass_center(self, *args):
        pass

    # get atomic number % 
    def get_atomic_number(self, *args):
        pass

    # get supercell % 
    def get_supercell(self, scale=[1.0, 1.0, 1.0]):
        pass

    # add atoms % 
    def add_atoms(self,position, index=None):
        pass

    # remove atoms % 
    def remove_atoms(self, *args):
        pass

   ## get imaginary configurations % 
    def get_neb_configuration(self, ini=None, fin=None, d=0.0):
       pass
    
