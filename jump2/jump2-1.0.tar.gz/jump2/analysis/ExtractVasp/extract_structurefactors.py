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
Module for extract data from vasp output: data for structure factors.
"""

__author__ = ""
import math
import cPickle as pickle 

class StructuralFactor(BasicParam):

    def __init__(self):
        self.radii = pickle.load('shannon_radii.dat', 'rb')

    def tolerance_factor(self, A_site, B_site, C_site, level=0):

        """
        A/B/C_site: ({'radii':None, 'element': Fe, 'charge': 2, 'spin': 'LS'}, ...)

        """
        
        tolerance_factor = []
        for specie_A in A_site:
            for specie_B in B_site:
                for specie_C in C_site:
                    r_a = self.get_radii('12.', **specie_A)
                    r_b = self.get_radii('6.',  **specie_B)
                    r_c = self.get_radii('6.',  **specie_C)

                    tf = self.__calc_tolerance_factor(r_a, r_b, r_c, level)

                    tolerance_factor.append((specie_A, specie_B, specie_C, tf))

        return tolerance_factor


    def get_radii(self, cn, rtype='cryst', **kwargs):
    
        option = kwargs

        return self.radii[option['element']][option['charge']][cn][option['spin']][rtype]


    def __calc_tolerance_factor(self, a, b, c, level=0):

        if level == 0:
            return (a+c)/(math.sqrt(2)*(b+c))

        if level == 1:
            pass
            """
                add the Wanjian Yin JACS paper formula;
            """

    def structural_factor(self,A_site, B_site, C_site, level=0):
        struct_factor = []
        for specie_A in A_site:
            r_a = self.get_radii('12.', **specie_A)
            for specie_B in B_site:
                r_b = self.get_radii('6.', **specie_B)
                for specie_C in C_site:
                    r_c = self.get_radii('6.',  **specie_C)

                    sf = self.__calc_tolerance_factor(r_a, r_b, r_c, level)

                    struct_factor.append((specie_B, specie_C, sf))
    
        return struct_factor

