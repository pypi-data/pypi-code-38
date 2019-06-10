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

__input_scirpts="""\
#!/usr/bin/env python

from jump2.functional import Factory 
from jump2.utils.read import Read
from jump2.pool import Pool
import os 

#functional to prepare the input for calculation % 
def jump_input():
    func = Factory.factory('{0}')
    
    #the basic params you used and tasks you would do%
    func.energy = 1e-5         # the energy thread %
    func.force  = 1e-2         # the force thread if you relax cell %
    func.task   = 'scf' 
    #func.task   = 'cell volume ions scf band optics' 
                               # any tasks you want to do, 
                               # default is 'scf'.
    #func.vdw = 'b86'
    
    #the initial structure you consider % 
    # you can use the for/while loop to do;
    #here is a simple for loop.
    
    # init the pool % 
    pool = Pool()

    pool.functional = func

    for d in os.walk('./test').next()[2]: 
        structure =Read('test/'+d, ftype='vasp').getStructure()
        pool.structure =structure
        job = pool / d
    
    # save data % 
    pool.save()
"""
