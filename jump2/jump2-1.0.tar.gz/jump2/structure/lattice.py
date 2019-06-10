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
This module defines the class relating to crytalline lattice.
"""

class Lattice(object):
    """
    Class aim to get relative properties related to structure.

    tributes:
        a: vector A of lattice;
        b: vector B of lattice;
        c: vector C of lattice;
    
    methods::
        get_lattice:
        get_volume:
        get_elements:
        get_formula:
        get_primary_cell:
        get_supercell:
        get_total_atoms:
        get_chemical_symbols:
        get_bravais_lattice:
        get_point_group:
        get_operations:
        get_space_group:
        get_cartesian_coordination:
        get_brillouin_zone(self):
        get_high_symmetry_points:
        get_atomic_number:
        get_atomic_mass:
        get_atomic_radius:
        get_high_symmetry_path_interploration
    """
   
    @property
    def a(self):
        """
        Return a tribute of lattice A vector. 
        """
        pass

    @property
    def b(self):
        """
        Return a tribute of lattice B vector. 
        """
        pass

    @property
    def c(self):
        """
        Return a tribute of lattice C vector. 
        """
        pass

    def get_lattice(self, space='reciprocal'):
        """
        Method to get lattice of given structure in Angstroms.
      
        args:
            space:: options ['real', 'reciprocal'], default reciprocal.
		   'real' for real space lattice;
                   'reciprocal' for reciprocal space lattice;
                    
                    reciprocal = (2*pi/real)/volume.
        
        Returns a 3x3 array, for instance,
                     array([[1.00, 0.00, 0.00],
                            [0.00, 1.00, 0.00],
                            [0.00, 0.00, 1.00]])
        """
        pass

    def get_volume(self):
        """
        Method to get lattice volume in real space in Angstroms^3.

        Returns a float number.
        """
        pass

    def get_elements(self):
        """
        Method to get elements in the Structure.

        Returns a list of spcieces, e.g., list(['Fe', 'O']).
        """
        pass

    def get_formula(self, simpled=True):
        """
        Method to get the chemical formula of given Structure.

        args::
            simpled: bool, True for the simplest chemical formula,
                     False for the formula within a unit cell,
                     default is True.

        Returns a string, e.g., u'Fe2O3'.
        """
        pass

    def get_primary_cell(self, threshold=0.01):
        """
        Method to get the primary cell of given Structure.
    
        args::
            threshold: float, the threshold to get redefine the 
                       the lattice and get the symmetrized cell,
                       default is 0.01.

        Returns a classic object of jump2.structure.Structure.
        """
        pass

    def get_supercell(self, dimension=[0., 0., 0.]):
        """
        Method to get the supercell of given Structure.

        args::
            dimension: list 1x3, e.g., [1.0, 1.0, 1.0],
                       supercell 1x1x1 along three vectors, 
                       default is [0., 0., 0.].

        Returns a classic object of jump2.structure.Structure.
        """
        pass

    def get_total_atoms(self):
        """
        Method to get the number of atoms of each species.

        Returns a tuple, for instance,
                tuple(('total',10),
                      (list(['Cs','Ag','Bi','Cl']),
                       list([2,1,1,6]))
                     )
        """
        pass
    def get_chemical_symbols(self):
        """
        Method to get the ordered chemical symbols in given Structure.

        Returns a list, e.g., 
             list(['Cs','Cs','Ag','Bi','Cl','Cl','Cl','Cl','Cl','Cl']).
        """
        pass
    def get_bravais_lattice(self):
        """
        Method to get the Bravais Lattice of given Structure, in 
            reciprocal lattice (Angstrom^-1).

        Returns a 3x3 array, for instance,
                     array([[1.00, 0.00, 0.00],
                            [0.00, 1.00, 0.00],
                            [0.00, 0.00, 1.00]])
        """
        pass

    def get_point_group(self):
        """
        Method to get the point group of given Structure.

        Returns a list of point group ordered from high to low, e.g., 
             list(['D6h','C6V', 'D3h', 'D3V']).
        """
        pass

    def get_operations(self, threshold=0.01):
        """
        Method to get possible operation of given Structure.

        args::
            threshold: float, the threshold to get redefine the 
                       the lattice and get the symmetrized cell,
                       default is 0.01.

        Returns a list of operation matrix, for instance,
            list([[1.0, 0.0, 0.0],
                  [0.0, 1.0, 0.0],
                  [0.0, 0.0, 1.0]],
                  .
                  .
                  .
                  [0.0, 1.0, 0.0],
                  [1.0, 0.0, 1.0],
                  [0.0, 1.0, 0.0]]).
        """
        pass

    def get_space_group(self):
        """
        Method to get the space group of given Structure.

        Returns a dict of space group, for instance, 
             dict{'number':225,
                  'symbol':'Fm-3m'}.
        """
        pass

    def get_cartesian_coordination(self, direct=True):
        """
        Method to get the real position of atoms in given Structure,
            in Angstrom.

        args::
            direct: bool, True for crytalline coordination,
                    False for Cartesian coordination.

        Returns a list of atomic position for instance,
            list([0.0, 0.0, 0.0]
                 [0.0, 0.0, 0.5])
        """
        pass

    def get_brillouin_zone(self):
        """
        Method to get the  Brillouin Zone of given Structure.

        Returns a dict of space group, for instance, 
             dict{'volume':5,
                  'symbol':'FCC'}.
        """
        pass

    def get_high_symmetry_points(self, threshold=0.01, optimal=True):
        """
        Method to get the high symmetry points in the of given Structure.

        args::
            threshold: float, the threshold to get redefine the 
                       the lattice and get the symmetrized cell,
                       default is 0.01.
            optimal: bool, the promising high symmetry path in Brillouin 
                     Zone; False all the possible will be presented.

        Returns a dict of high symmetry points, for instance, 
             dict{'point':{'\Gamma':[0.0, 0.0, 0.0], 'X':[0.5, 0.0, 0.0]},
                  'paths':['\Gamma', 'X']}.
        """
        pass

    def get_atomic_number(self, species=None):
        """
        Method to get the atomic number in given Structure.

        args::
            species: given elements, default all the elements in given 
                     structure.

        Returns a dict, contained species and atomic number, e.g., 
             dict{'H':1, 'C':6}.
        """
        pass

    def get_atomic_mass(self, species=None):
        """
        Method to get the atomic mass in given Structure.

        args::
            species: given elements, default all the elements in given 
                     structure.

        Returns a dict, contained species and atomic mass, e.g., 
             dict{'H':1, 'C':12}.
        """
        pass

    def get_atomic_radius(self, species=None):
        """
        Method to get the atomic radius, including atomic/ionic/covalent radii.
        
        args::
            species: string/list, given elements, default all the elements 
                     would be shown in given structure.

        Returns a dict, for example,
            dict{'Pb':{'ionic':{'+2':1.68, '+4':1.56}, 
                       'atomic':2.00, 
                       'convalent':1.90}}
        """
        pass

    def get_high_symmetry_path_interploration(self, 
         		 line_A=None, line_B=None, num=10):
        """
        Method to get interplorated kpoints along the high symmetry path.
        
        args::
            line_A: the initial high symmetry point;
            line_B: the final high symmetry point;
            num: the number of points in the symmetry path;

        Returns a dict contained the kpoints and symbols for example,
            dict{'paths':'\Gamma --> X', 
                 'point': [[0.0,0.0,0.0],
                           .
                           .
                           .
                           [0.0,0.0,0.5]]}
        """
        pass

