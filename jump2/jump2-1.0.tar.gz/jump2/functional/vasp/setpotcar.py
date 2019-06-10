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

__contributor__ = 'Gaungren Na, Xingang Zhao'
__update_date__ = '2017.05.01'

"""partial of JUMP2 for psudopotentials functional setting."""


class SetPotcar(object):

    """
    class SetPotcar:: to organize and output the potcar for VASP.
    args:
        species:: elements contained in the structures.

    return a dict, including,
        {'type':[],
         'path':[],
         'species':[],
         'enmax':[]}

    """
    def setpotcar(self, species, path=None, *args, **kwargs):
        """
        collect the all the potcar and relative info from POTCAR.

        kwargs:
            pot_type:: atomic psudopotential;
            orbital:: with external orbital for valence;
            radius:: atomic radius of H; 
            
        """
        from jump2.utils.io import is_exist
        import numpy as np 
 
        species = list(species)
        if path is None:
            try: 
                from jump2.config import cluster 
                a = cluster.Cluster()
                path = a.potential_path
            except: 
                raise IOError ('No invalid path of atomic potential')
            
        if not isinstance(species, list): 
            raise IOError ('not elements input')

        potcar = {}
        potcar['type'] = []
        potcar['species'] = species
        potcar['path'] = []
        potcar['enmax'] = []

        # loop all the elements % 
        for e in species:
            object_path = self.__element_potcar(path, e, **kwargs)
            if is_exist(object_path):
                potcar['path'].append(object_path)
                param = self.get_parameter(object_path, 'enmax','lexch')
                potcar['enmax'].append(float(param['ENMAX']))
                potcar['type'].append(param['LEXCH'])
            else:
                raise NoFoundError\
                ('No {0} was found'.format(object_path))
        
        # indenfy type of POTCAR%
        potcar['type'] = set(potcar['type'])
        if len(potcar['type']) > 1:
            raise IOError\
            ("Multi-type potentials were found. {0}".format\
            ('_'.join(potcar['type'])))
	
        return potcar 
    
    # obtained the parses embeded in POTCAR (under developed)%
    def get_parameter(self, path, *args, **kwargs):

        """
        Method to get the given parameters of set in each atomic potential.
        
        args:
            need args is the path way of atomic potential;
            optional args are the keywords set in the atomic potential.
        
        return a dict contained the keywords and values,
            for instance, {'ENMAX':400, 'LEXCH': 'CA'}, default is None.
        """

        parse = {}

        if args is not None:
            for p in args:
                parse[p.upper()] = self.__potcar_parses(path, p)[p.upper()]

            return parse
        else:
            return None
    

    # abstract the parses from POTCAR (under developed)%
    def __potcar_parses(self, path, value=None):
	"""
        Get the common parses in POTCAR.

        args:
            path:: the location of atomic psudopotential;
            value:: the key word to selected the parameters;
        """   
        import re
        import os 
        content = os.popen('grep {value} {path}'.format(value=value.upper(), 
                                                path=path)).readline()
        keys=re.findall(r'(\w+|w+\s?)\s*(?<=)=', content)
        vals=re.findall(r'=(?=)+\s*(\d+\.?\d+|\S+)', content)
        
        params = dict(zip(keys, vals))

        return params

    # search for the path of given element % 
    def __element_potcar(self, path, element, **kwargs):
        
        """
        kwargs:
            pot_type: type of psudopotential;
            orbital: external considered orbital;
            radius: radius of atomic psudopotential (for hydrogen);
        """

        import os 
        pot_type=None; orbital=None; radius=None

        external = False   # global bool for selecting parse %
        case_elm = element # temple varbile of elements % 
        tag = None         # warning tag for select potential % 

        # external parameters % 
        if 'pot_type' in kwargs:
            pot_type= kwargs['pot_type']
        elif 'orbital' in kwargs:
            orbital= kwargs['orbital']
        elif 'radius' in kwargs:
            radius= kwargs['radius']
        if any([pot_type, orbital, radius]):
            external = True
        # add radius % 
        if all([radius, external]):
            radius = str(radius)
            case_elm = ''.join([element, str(radius)])
            external = False
        #add orbital % 
        if all([orbital, external]):
            if 's' in orbital:
                case_elm = '_'.join([element, 'sv'])
            if 'p' in orbital:
                case_elm = '_'.join([element, 'pv'])
            else:
                case_elm = '_'.join([element, 'd'])
            external = False
        # add type of potential % 
        if all([pot_type, external]):
            if 's' in pot_type.lower():
                pot_type = 's'
            else:
                pot_type = 'd'
            case_elm = '_'.join([element, pot_type])
            external = False
        
        # path % 
        path1 = os.path.join(path, case_elm)
        path2 = os.path.join(path, element)
        if os.path.exists(path1):
            path = path1
        else:
            path = path2
            tag = 'No {0}'.format(case_elm)

        if os.path.exists(path):
            pot = os.path.join(path, 'POTCAR')
            if os.path.exists(pot):
                return pot
            else:
                tmp = os.path.join(path, 'POTCAR.Z')
                try:
                    os.system('gunzip {0}'.format(tmp))
                except:
                    print "No POTCAR.Z"

            return pot
