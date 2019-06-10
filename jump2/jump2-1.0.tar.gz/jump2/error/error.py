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
This module defines the classes relating to basical errors.
"""

__author__ = "Xin-Gang Zhao"
__contributor__ = 'Xingang Zhao'
__date__ = "2017.05.01"


class GrepError:
    pass
class CalError:
    pass

class VaspError:
    """
    
    """
    @property
    def error_algo(self):
        """
         `WARNING: Sub-Space-Matrix is not hermitian in DAV`
         
        SOVLE:
             reduce POTIM & ALGO 
        """
        pass

    """
    WARNING: dimensions on CHGCAR file are different
    ERROR: charge density could not be read from file CHGCAR for ICHARG>10
    """
    
    """
    WARNING: Sub-Space-Matrix is not hermitian in DAV
    """
    
class NoFoundError:
    pass 
class FinishTask:

    pass
class ImportError:

    pass

class InputError:

    pass

class RunError:

    pass

class ExtractError:

    pass 

class ParseError:

    pass


class MODError:

    pass 

class DATAError:
    pass 
