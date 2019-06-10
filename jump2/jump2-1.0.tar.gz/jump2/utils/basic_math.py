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
This module defines the methods relate to basic math functions.
"""


__author__ = "Xin-Gang Zhao"


import numpy as np

from material.atom import cartesian2direct, direct2cartesian

def normalizingCoordinateComponent(x, **kwargs):
    """
    remove periodicity of atomic position, ensure x value is 
    between 0 and 1.0. i.e. 2.3 -> 0.3; -0.9 -> 0.1.
    
    Arguments:
        x (Direct): component of atomic position
        
        kwargs:
            range (default='right'): right -> [0,1] or center -> [-0.5, 0.5]
    """
    
    newx=x-int(x) # fraction of floating number x
    
    range='right'
    if 'range' in kwargs:
        range=kwargs['range']
    
    if range == 'right':
        if newx < 0:
            newx += 1
    elif range == 'center':
        if newx >= 0.5:
            newx -= 1
        elif newx < -0.5:
            newx += 1
    else:
        raise Exception('unknown parameter value: range!')
    
    return newx

def normalizingCoordinate(position, **kwargs):
    """
    remove periodicity of atomic position, ensure all component's values 
    are between 0 and 1.0. i.e. 2.3 -> 0.3; -0.9 -> 0.1.
    
    Arguments:
        position (Direct): component of atomic position. i.e. [x, y, z]
        
        kwargs:
            range (default='right'): right -> [0,1] or center -> [-0.5, 0.5]
    """
    range='right'
    if 'range' in kwargs:
        range=kwargs['range']
    
    newposition=[]        
    for i in xrange(0, len(position)):
        newposition.append(normalizingCoordinateComponent(position[i], range=range))
        
    return newposition

def extractingCoordinate(structure, atom):
    """
    
    Arguments:
        structure: object of structure
        atom: a array contained atomic information 
              [element_symbol, x, y, z, coord_type (optional)]. 
              i.e. ['Na', 0.5, 0.5, 0.5](Direc) or 
              ['Na', 1.3, 3.5, 2.0, 'Cartesian'](Cartesian)
    
    Return:
        position (Direct): atomic position.
    """
    position=[]
    type='Direct' # default
    if len(atom) == 5:
        position=atom[1:-1]
        if atom[-1].lower().startswith('c'):
            type='Cartesian'
            position=cartesian2direct(structure, position)
        elif atom[-1].lower().startswith('d'):
            type='Direct'
        else:
            raise Exception('unknown value in coord_type(Direct/Cartesian)!')
    elif len(atom) == 4:
        position=atom[1:]
    else:
        raise Exception('check the input parameter: atom')
    position=np.array(position)
    
    return position

def convertingCoordinate(structure, position):
    """
    
    Arguments:
        structure: object of structure
        atom: a array contained atomic information 
              [x, y, z, coord_type (optional)]. 
              i.e. [0.5, 0.5, 0.5](Direc) 
              or [1.3, 3.5, 2.0, 'Cartesian'](Cartesian)
    
    Return:
        position (Direct): atomic position.
    """
    newposition=[]
    type='Direct' # default
    if len(position) == 4:
        newposition=position[:-1]
        if position[-1].lower().startswith('c'):
            type='Cartesian'
            newposition=cartesian2direct(structure, newposition)
        elif position[-1].lower().startswith('d'):
            type='Direct'
        else:
            raise Exception('unknown value in coord_type(Direct/Cartesian)!')
    elif len(position) == 3:
        newposition=position
    else:
        raise Exception('check the input parameter: position')
    newposition=np.array(newposition)
    
    return newposition


def massCenter(atom_set):
    """
    get the mass center of given atom set
    """
    # check data
    type=None # class of object
    for atom in atom_set:
        print 'class', atom.structure.__class__.__name__
        if type == None:
            type=atom.structure.__class__.__name__
            print 'class', type
        elif type != atom.structure.__class__.__name__:
            raise Excption("type doesn't match")
        
    if type == 'MolStructure':
        print type
    elif type == 'Structure':
        print type            

def distancePoint2Surface(point, surface):
    """
    calculates the distance from point to surface
    
    Arguments:
        point: 
        surface:
        
    Return:
        distance: 
    """
    
def isPointInsidePolyhedron(point, polydhedron):
    pass    
    
