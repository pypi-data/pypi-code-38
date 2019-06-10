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


class Read(object):
    """
    reading structure
    
    arguments:
        file: path of structure. i.e. /home/xx/xx/POSCAR, POSCAR
        type: type of structure file. i.e. cif, vasp....
    
    """
    
    #import json

    def __init__(self, file, ftype=None):
        self.file=file
        self.ftype = ftype
        
        if ftype == None:
            if self.file.endswith('cif'):
                self.ftype='cif'
            elif (self.file.split('/')[-1] == 'POSCAR') \
              or (self.file.split('/')[-1] == 'CONTCAR'):
                self.ftype='vasp'
        elif ftype == 'cif':
            self.ftype='cif'
        elif ftype == 'vasp':
            self.ftype='vasp'
            
                    
    def getStructure(self):
        """
        read structure
        
        returns:
            json's object of a structure
            
        """
        if self.ftype == 'cif':
            return self.__readCIF()
        elif self.ftype == 'vasp':
            return self.__readPOSCAR()
    
    def __readCIF(self):
        """
        read CIF file
        
        returns:
            json's object of a structure
            
        """
        pass        
    
    def __readPOSCAR(self): # only for VASP5.x (It means the file need to contain the element information)
        """
        read POSCAR file
        
        poscar:
            comment: comment of the first line
            lattice=[[x1,x2,x3],
                     [y1,y2,y3],
                     [z1,z2,z3]]
            elements=['Ca', 'Fe', 'Sb']
            numbers=[2, 8, 24]
            type= Direct or Cartesian
            position=[[a1_x,a1_y,a1_z],
                      [a2_x,a2_y,a2_z],
                      [a3_x,a3_y,a3_z],
                      ...]
            constraint=[[T,T,T], # Selective dynamics (optional)
                        [F,F,F],
                        [T,F,T],
                        ...]
        
        returns:
            json's object of a structure
            
        """
        import numpy as np
        poscar=()
        input=open(self.file)
        
        # comment
        comment=''
        string=input.readline()
        if string != "":
            comment=string.split('\n')[0]
            
        scale=float(input.readline())
        
        # lattice
        # ensure all structure's scale equal 1 inside the program     
        lattice=[]
        for i in xrange(0,3):
            try:
                tmp=np.array([float(s0) for s0 in input.readline().split()])
                if tmp.shape[0] == 3:
                    lattice.append(tmp*scale)
                else:
                    print 'lattice parameter is less than 3!'
                    exit()
            except ValueError:
                print "can't transfer literal to float type!"
                exit()
        lattice=np.array(lattice)
        
        # element VASP5.x
        # Note that:
        #   need check symbol of element is valid by comparing the element table in jump2db
        elements=[]
        tmp=np.array(input.readline().split())
        for i in xrange(0,tmp.shape[0]):
            if not(tmp[i].isalpha()):
                print 'elements contain non-alphabet!'
                exit()
        elements=tmp
        
        # numbers
        numbers=[]
        try:
            tmp=np.array([int(s0) for s0 in input.readline().split()])
            if elements.shape[0] != tmp.shape[0]:
                print "length of numbers don't match with that of elements"
                exit()
            numbers=tmp
        except ValueError:
            print "can't transfer literal to int type!"
            exit()
            
        # type
        type=''
        tmp=input.readline()
        if tmp.lower().startswith('c'):
            type='Cartesian'
        elif tmp.lower().startswith('d'):
            type='Direct'
        else:
            print 'type of POSCAR is invalid'
            exit()
        
        # position
        natoms=sum(numbers)
        position=[]
        for i in xrange(0, natoms):
            try:
                tmp=np.array([float(s0) for s0 in input.readline().split()])
                if tmp.shape[0] == 3:
                    position.append(tmp)
                else:
                    print 'position of atom is less than 3!'
                    exit()
            except ValueError:
                print "can't transfer literal to float type!"
                exit()
        position=np.array(position)
        
        input.close()
        poscar=(comment,lattice,elements,numbers,type,position)
        
        return poscar
             
# -------------------- test --------------------
#r=Read('POSCAR')
#poscar=r.getStructure()
#for i in xrange(len(poscar)):
#    print poscar[i]

