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
This module defines the classes relating to periodic table.
"""


__author__ = "Xin-Gang Zhao"

class Ptable(object):

    """
    cls: Ptable (Periodic Table) contains the elements and atomic number of each elements.

    tributes:
        get_elements: return the elements symbol after input the atomic number,
                      chemical symbols.
        get_mass: return the mass of given elements:
        get_valence: return the common valence of the elements.
        get_radii: return the shamnon atomic radii of the given elements.
        get_atomic_number: return the atomic number of given elements.
        get_ionic_energy: return the inonic energy of given elements.

    """

    def __init__(self, *args, **kwargs):

       #self.table = {1: 'H', 2: 'He', \
       #         3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne', \
       #         11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar', \
       #         19: 'K', 20: 'Ca', 21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni',
       #         29: 'Cu', 30: 'Zn', 31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr', \
       #         37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb', 42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd',
       #         47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn', 51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', \
       #         55: 'Cs', 56: 'Ba', 71: 'Lu', 72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt',
       #         79: 'Au', 80: 'Hg', 81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn', \
       #         87: 'Fr', 88: 'Ra', 103: 'Lr', 104: 'Rf', 105: 'Db', 106: 'Sg', 107: 'Bh', 108: 'Hs', 109: 'Mt',
       #         110: 'Ds', 111: 'Uuu', 112: 'Uub', \
 #\
       #         57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd', 61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy',
       #         67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb', \
       #         89: 'Ac', 90: 'Th', 91: 'Pa', 92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm', 97: 'Bk', 98: 'Cf',
       #         99: 'Es', 100: 'Fm', 101: 'Md', 102: 'No' \
       #         }
        if not args:
            raise IOError ("No elements or atomic number input.")
        else:
            self.elements = []
            for elements in args:
                if isinstance(elements, list):
                    for e in elements: self.elements.append(e)
                elif isinstance(elements,str):
                    self.elements.append(elements)
                elif isinstance(elements,int):
                    self.elements.append(elements)

            self.__periodic_table__()

    def get_mass(self):
        """ Return the masses of given elements."""

        return self._mass

    def get_radii(self):

        """Return the ionic_radius; covalent_radius; ligent_radius"""

        return self._radii

    def get_valence(self):
        """Return the common valences of the given elements."""

        return self._valence

    def isotope(self):
        """Return the isotope of the given elements if exists"""

        if self._isotope is None: return None
        return self._isotope

    def __periodic_table__(self):
       
        """Return the chemical symbol and atomic number of given elements."""

        value = self.elements
        elements = {}    # templete dict to store the search elements
        convtable = {}   # templete dict of the converted periodic table.
        for k, v in self.__table__.iteritems(): convtable[v] = k

        if isinstance(value, list):
            for e in value:
		try:
                    e = int(e)
                except:
                    pass
                if isinstance(e,int) and table.has_key(e):
                    elements[self.__table__[e]] = e
                elif convtable.has_key(e.capitalize()):
                    elements[e] = convtable[e]
                else:
                    raise IOError("There is no {0} elements in perodic table".format(e))

        self.elements = elements
        return self.elements

    __table__ = {1: 'H', 2: 'He', \
             3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne', \
         11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar', \
         19: 'K', 20: 'Ca', 21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni',
         29: 'Cu', 30: 'Zn', 31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr', \
         37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb', 42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd',
         47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn', 51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', \
         55: 'Cs', 56: 'Ba', 71: 'Lu', 72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt',
         79: 'Au', 80: 'Hg', 81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn', \
         87: 'Fr', 88: 'Ra', 103: 'Lr', 104: 'Rf', 105: 'Db', 106: 'Sg', 107: 'Bh', 108: 'Hs', 109: 'Mt',
         110: 'Ds', 111: 'Uuu', 112: 'Uub', \
\
         57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd', 61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy',
         67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb', \
         89: 'Ac', 90: 'Th', 91: 'Pa', 92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm', 97: 'Bk', 98: 'Cf',
         99: 'Es', 100: 'Fm', 101: 'Md', 102: 'No' \
         }




# waiting for update
mass = {\
        1:{'each':[None],'averaged':1.0},\
        2:{},\
        }

class Mass(Ptable):

    """
    cls: Jump2Mass contains the masses of each elements.
    contribute:
        get_mass: return the mass of each given elements, 
	          default, averaged mass of all isotopes.
    """

    def get_mass(self,elements,averaged=True,*args, **kwargs):
        """Get the mass of each elements."""

        mass = {}

        elements = self.periodic_table(elements)

        for k,v in elements.iteritems():
            if averaged:
                mass[k] = self.mass[v]['averaged']
            else:
                mass[k] = self.mass[v]['each']

        self.__mass = mass



