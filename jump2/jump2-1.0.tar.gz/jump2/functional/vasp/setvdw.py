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

from ...error import *

__contributor__ = 'Gaungren Na, Xingang Zhao'
__update_date__ = '2017.05.01'

"""SetVdw:: partial of JUMP2 for vdw functional setting, default is None."""

class SetVdw(object):
    """
    Common Van der Waals functional implemented in VASP:
        --D2: 
        --optB86b:
        --optB88:
        --DF2:
        --optPBE:
    args::
        vdw:: a string to describe the vdw functional name;
        elements:: species only for D2 functional;

    :return: A parameter dict.
    """

    def __init__(self, vdw=None, elements=None, *args, **kwargs):

        self.vdw = None

        # set for nothig % 
        if vdw is None: return
        
        #set for the default vdw functional % 
        if isinstance(vdw, str):
            self.vdw = self.set_vdw(vdw, elements)
        else:
            raise IOError\
            ("invalid vdw functional input {0}".format(str(vdw)))

        # customed vdw functional %
        if args and kwargs:
            self.vdw = {}
            self.vdw['type'] = args[0]
            self.vdw['param'] = kwargs

        # other input % 
        if self.vdw is None:
            raise NoFoundError ('{0} is not found'.format(vdwfuc))

    # select the vdw fnuctional % 
    def set_vdw(self, vdw, elements=None):
        """set the params according to the input"""

        usevdw = None
        vdw = vdw.lower()
        # case d2 %
        if 'd2' in vdw:
            if elements is None:
                raise NoFoundError("None elements input.")
            else:
                usevdw = self.__vdwparams__('D2', elements)
        # case b86 % 
        elif 'b86' in vdw:
            usevdw = self.__vdwparams__('B86')
        # case b88 %
        elif 'b88' in vdw:
            usevdw = self.__vdwparams__('B88')
        # case pbe %
        elif 'pbe' in vdw:
            usevdw = self.__vdwparams__('optPBE')
        # case df2 %
        elif 'df2' in vdw_func:
            usevdw = self.__vdwparams__('DF2')
        # case other %
        else:
            usevdw = None

        return usevdw
        
    def __d2vdw__(self, elements):

        r0_orig = [ 0.91e0 ,0.92e0,
                    0.75e0 ,1.28e0 ,1.35e0 ,1.32e0 ,1.27e0 ,1.22e0 ,1.17e0 ,1.13e0,
                    1.04e0 ,1.24e0 ,1.49e0 ,1.56e0 ,1.55e0 ,1.53e0 ,1.49e0 ,1.45e0,
                    1.35e0 ,1.34e0,
                    1.42e0 ,1.42e0 ,1.42e0 ,1.42e0 ,1.42e0,
                    1.42e0 ,1.42e0 ,1.42e0 ,1.42e0 ,1.42e0,
                    1.50e0 ,1.57e0 ,1.60e0 ,1.61e0 ,1.59e0 ,1.57e0,
                    1.48e0 ,1.46e0,
                    1.49e0 ,1.49e0 ,1.49e0 ,1.49e0 ,1.49e0,
                    1.49e0 ,1.49e0 ,1.49e0 ,1.49e0 ,1.49e0,
                    1.52e0 ,1.64e0 ,1.71e0 ,1.72e0 ,1.72e0 ,1.71e0,
                    1.638e0 ,1.602e0 ,1.564e0 ,1.594e0 ,1.594e0 ,1.594e0 ,1.594e0,
                    1.594e0 ,1.594e0 ,1.594e0 ,1.594e0 ,1.594e0 ,1.594e0 ,1.594e0,
                    1.594e0 ,1.594e0 ,1.594e0,
                    1.625e0 ,1.611e0 ,1.611e0 ,1.611e0 ,1.611e0 ,1.611e0 ,1.611e0,
                    1.611e0,
                    1.598e0 ,1.805e0 ,1.767e0 ,1.725e0 ,1.823e0 ,1.810e0 ,1.749e0]
        r0 = []

        for (id, rr) in enumerate(r0_orig):
            r0.append(rr * 1.1)

        c6 = [0.14e0 ,0.08e0,
              1.61e0 ,1.61e0 ,3.13e0 ,1.75e0 ,1.23e0 ,0.70e0 ,0.75e0 ,0.63e0,
              5.71e0 ,5.71e0 ,10.79e0 ,9.23e0 ,7.84e0 ,5.57e0 ,5.07e0 ,4.61e0,
              10.8e0 ,10.8e0 ,10.8e0 ,10.8e0 ,10.8e0,
              10.8e0 ,10.8e0 ,10.8e0 ,10.8e0 ,10.8e0 ,10.8e0 ,10.8e0 ,16.99e0,
              17.10e0 ,16.37e0 ,12.64e0 ,12.47e0 ,12.01e0 ,24.67e0 ,24.67e0,
              24.67e0 ,24.67e0 ,24.67e0 ,24.67e0 ,24.67e0 ,24.67e0 ,24.67e0,
              31.50e0 ,29.99e0 ,315.275e0 ,226.994e0 ,176.252e0,
              140.68e0 ,140.68e0 ,140.68e0 ,140.68e0 ,140.68e0 ,140.68e0 ,140.68e0,
              140.68e0 ,140.68e0 ,140.68e0 ,140.68e0 ,140.68e0 ,140.68e0 ,140.68e0,
              105.112e0,
              81.24e0 ,81.24e0 ,81.24e0 ,81.24e0 ,81.24e0 ,81.24e0 ,81.24e0,
              57.364e0 ,57.254e0 ,63.162e0 ,63.540e0 ,55.283e0 ,57.171e0 ,56.64e0]

        R0 = []
        C6 = []

        for (i, eleinput) in enumerate(elements):
            for (id, ele) in table.iteritems():
                if eleinput == ele:
                    R0.append(r0[id])
                    C6.append(c6[id])

        return  {'param':{\
            "lvdw": True, \
            "vdw_r0": ' '.join(str(r) for r in R0), \
            "vdw_c6": ' '.join(str(c) for c in C6)},
            "type": 'D2'}

    def __vdwparams__(self, value=None, elements=None):

        # case d2 vdw % 
        if value == 'D2':
            return self.__d2vdw__(elements)

        # case optPBE vdw % 
        if value == 'optPBE':
            return { 'param':{\
                'gga': 'RO', \
                'luse_vdw': True, \
                'aggac': 0.0000},\
                "type":'optPBE'}

        # for optvdw-B88 %
        if value == 'B88':
            return {'param':{\
                'gga': 'BO', \
                'luse_vdw': True, \
                'aggac': 0.0000, \
                'param1': 0.1833333333, \
                'param2': 0.2200000000},\
                'type':'optvdw-B88'}

        # for optvdw-B86b %
        if value == 'B86':
            return {'param':{\
                'gga': 'MK', \
                'luse_vdw': True, \
                'param1': 0.1234, \
                'param2': 1.0000, \
                'aggac': 0.0000},\
                'type':'optvdw-B86b'}

        # for DF2 %
        if value == 'DF2':
            return {'param':{\
                "gga": 'ML', \
                "luse_vdw": True, \
                "aggac": 0.0000, \
                "zab_vdw": -1.8867},\
                'type':'DF2'}
