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


__contributor__ = "Tianshu Li, Xingang Zhao"
__revised_date__= "2017.05.01"

"""choice the HubbardU from reported values by Ladan Stevanovic and Stephan Lany"""


def default_plusU(elements):
    """
       method:: first-principle calculation with LDA plus U.
                the choice of u value is based on Vladan 
                Stevanovic and Stephan Lany(2012)
    """
    plusU={\
    'Ni': [3, 0, 2], \
    'La': [3, 0, 2], \
    'Nb': [3, 0, 2], \
    'Sc': [3, 0, 2], \
    'Ti': [3, 0, 2], \
    'Rh': [3, 0, 2], \
    'Ta': [3, 0, 2], \
    'Fe': [3, 0, 2], \
    'Hf': [3, 0, 2], \
    'Mo': [3, 0, 2], \
    'Mn': [3, 0, 2], \
    'W':  [3, 0, 2], \
    'V':  [3, 0, 2], \
    'Y':  [3, 0, 2], \
    'Zn': [6, 0, 2], \
    'Co': [3, 0, 2], \
    'Ag': [5, 0, 2], \
    'Ir': [3, 0, 2], \
    'Cd': [5, 0, 2], \
    'Zr': [3, 0, 2], \
    'Cr': [3, 0, 2], \
    'Cu': [5, 0, 2]}

    U = []
    J = []
    types = []
    bubbardu = {}
   
    for e in elements:
        if e in plusU:
            U.append(plusU[e][0])
            J.append(plusU[e][1])
            types.append(orbitalU.index(plusU[e][2]))
        else:
            U.append(0)
            J.append(0)
            types.append(2)
            
    hubbardu['ldauu'] = ' '.join(U)
    hubbardu['ldauj'] = ' '.join(J)
    hubbardu['ldautype'] = ' '.join(types)

    return hubbardu
