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

__contributor__ = 'Xin He, Xingang Zhao'
__update_date__ = '2017.05.01'

default_incar={\
   'system': 'jump2',                                   
   'prec': ' Normal',    
   'istart':       0,    
   'icharg':       2,    
   'lwave':    False,    
   'lcharg':   False,    
   'encut':    364.0,  
   'nlem':       100,
   'ediff':  0.1E-06,   
   'lreal':    'Auto',    
   'algo':  'VeryFast',    
   'amin':      0.01,
   'addgrid': True,
   'isif':         2,    
   'ibrion':      -1,    
   'ediffg': -0.1E-04,   
   'nsw':          0,    
   'ismear':       0,
   'sigma':     0.10,  
   'ncore':        8}

# basic functional for VASP calculations %
#set MBJ %
imbj={'metagga':'MBJ', 'lasph': True, 'lmixtau':True}

# set SOC %
isoc={'lsobit':True, 'lnoncollinear':True}

# set HSE06 and HSE03 %
ihse06={'lhfcalc':True, 'hfscreen':0.2, 'precfock':'Fast'}
ihse03={'lhfcalc':True, 'hfscreen':0.3, 'loptics':True}

#set optics % 
ioptic={'loptics':True, 'cshift':1e-4, 'nedos':8000, 'npar':1, 'ismear':-5}

# set GW % 
igw={'loptics':True, 'algo': 'GW0', 'lhfcalc':True}

# set born effective charge and dielectric tensonor % 
iborn={'ibrion':8, 'lepsilon': True, 'lpead':True, 'nsw':2}

#Partial Charge
ipcharge={'lpard':True, 'eint': 0, 'lcharg': True}

# need updated  (under developed)% 
#set dynamic NVE % 
dynamic={\
'nve':{'ISIF':2,
     'TEBEG':300,
     'NBLOCK':1,
     'KBLOCK':50,
     'APACO':10,
     'NPACO':200,
     'TEBND':300,
     'SMASS':[-3,-1]},
'nvt':{'ISIF':2,
     'MDALGO':3,
     'TEBEG':300,
     'TEBND':300,
     'NBLOCK':1,
     'KBLOCK':50,
     'APACO':10,
     'NPACO':200,
     'SMASS':[1,2,3]},
'npt':{'PSTRESS':0,
     'MDALGO':3,
     'TEBEG':300,
     'TEBND':300,
     'NBLOCK':1,
     'KBLOCK':50,
     'APACO':10,
     'NPACO':200,
     'SMASS':[1,2,3]}
     }

#==============================================================================
basic_params={\
   'system': 'jump2',                                   
   'prec': ' Normal',    
   'istart':       0,    
   'icharg':      11,    
   'lwave':    False,    
   'lcharg':    True,    
   'lvtot':    False,    
   'lvhar':    False,    
   'lorbit':      11,    
   'encut':    364.0,  
   'nlem':       100,
   'ediff':  0.1E-05,   
   'lreal':   'Auto',    
   'algo':        38,    
   'amin':      0.01,
   'addgrid':   True,
   'isif':         2,    
   'ibrion':      -1,    
   'ediffg': -0.1E-04,   
   'nsw':          0,    
   'isym':         2,    
   'ismear':      -5,
   'sigma':     0.20,  
   'lplane':    True,
   'npar':         4}
#==============================================================================
fincar="""\
#======default========
{0}

#======precise========
{1}

#======control========
#ions:
{2}

#electron:
{3}

#=====external========
{4}

#=====parallel========
{5}

"""
