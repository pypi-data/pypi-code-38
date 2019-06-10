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
Module for extract data from vasp output:XDATCAR. 
"""
import os
import numpy as np
from basics import BasicParam

__contributor__ = 'Xin He, Xingang Zhao'
__edited_date__ = '2017-04-29'

class get_ProStructure(BasicParam):
    """
    Class to get the structures of the trajectory from the XDATCAR 
            during the optimization/scf/nonscf by VASP calculation, 
            and append those structures into a lab.

    return:: Struct{'S1':{'structure':Structure, 'Energy':float}}
    """

    def __init__(self, path=None, *args, **kwargs):
	"""
	initialize the pathway
	"""
        
	super(get_ProStructure, self).__init__()

	# structure % 
        if path is None: path = os.getcwd()
        self.__path = path
   
    @property
    def structures(self):
	self.__read_structures()
        
	return self.__structure

    def __read_structures(self):

        """
        Read in the data in XDATCAR.
        """
	
	from jump2.structure.structure import Structure

	structure = None
	from os.path import join 

	path = join(self.__path, 'XDATCAR')

	isif = self.isif  # 3 for relax cell, 2 for relax ions %  
	version = self.vasp_version

	with open(path, 'r') as f: # open XDATCAR %
	    while True:

                if version <= 5.3 and not structure: 
                    for i in xrange(0,7): temp = f.readline()
	        line = f.readline()
                if not line: break
                if isif >= 3:
                    name = line # system name % 
		    scale, lattice, species, numbers =\
		    self.__read_lattice(f)

		if isif <3 and not structure:
                    name = line # system name % 
                    scale, lattice, species, numbers =\
                    self.__read_lattice(f)
		
		#print name, scale, lattice, species, numbers
		# structure of each step % 
	        line = f.readline()
                if line.startswith('Direct configuration='):
    
                    count = 'S'+(line.split('=')[-1]).strip()
                    positions = self.__read_position(f, sum(numbers))
    	     	    
                    if not structure: structure = {}

                    structure[count] = Structure()
                    structure[count].comment   = name
                    structure[count].scale     = scale
                    structure[count].elements  = np.array(species)
                    structure[count].numbers   = np.array(species)
                    structure[count].lattice   = np.array(lattice)
                    structure[count].positions = np.array(positions)
                    structure[count].contraints= None
        self.__structure = structure 
        del structure 
    #
    def __read_lattice(self, file=None):
	
        line = file.readline()
        scale = float(line) # lattice scale % 
        
	lattice = [] 
        # lattice % 
        for i in xrange(0,3):
            line = file.readline()
            lattice.append([float(v) for v in line.split()])
        
        # species in structure % 	
        line = file.readline()
        species = [str(s) for s in line.split()]
        
        # numbers of each element % 
        line = file.readline()
        numbers = [int(n) for n in line.split()]
    
	return scale, lattice, species, numbers

    #	 	
    def __read_position(self, file=None, num=None):
	"""
	return one structure position.
        """

        count = 0 
        position = []
        while count < num:
            line = file.readline()
            position.append([float(p) for p in line.split()])
            count += 1
	
	return position 

    def save_structure(self, total_energy=True, **kwargs):

        """
	output the structure with total energy and other information 
        extracted from VASP output
        """

	from jump2.utils.io import write_poscar
        
        ordered_index = sorted(self.structures.keys())
        
        comments = self.__organize_comments(**kwargs)

	for k in ordered_index:
             structure = self.structures[k]
	     structure.comments = comments[ordered_index.index(k)]
	     write_poscar(structure)
	
    def __organize_comments(self, **kwargs):
	
	"""
	return string 
	"""
	
	from basics import BaiscParam   
	
        basic = BasicParam(self.__path)
	
	if not kwargs.has_key('total_energy'):
            kwargs['total_energy'] = True

	comment = []
        tag = ''
	for k in kwargs:
            if BaiscParam.__hasattr__(k):
		comment.append([basic.get_attr(k)])
		tag += k+'/'
	comment = np.array(comment).T
