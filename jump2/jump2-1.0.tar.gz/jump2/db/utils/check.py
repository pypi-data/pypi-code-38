#coding=utf-8
'''
Created on Dec 11, 2017

@author: Yuhao Fu
'''
import numpy as np

def exist(entity, collection, entity_type, **kwargs):
        """
        whether to exit this entity in this collection.
        
        Examples:
            >>> comp=Composition.objects.get(formula='PbTiO3')
            >>> exist('Na', comp.atoms, 'element')
                False
        
        Arguments:
            entity:
                for structure:
                    entity: structure's object.
                
                for composition:
                    entity: composition's object or its formula. i.e. PbTiO3
                      
                for element:
                    entity: element's object or its symbol. i.e. 'Na'.
                
                for species:
                    entity: species's name or object. i.e. 'Fe2+'
                    
                for atom:
                    entity: atom's object or formated string. i.e. if type of coordinate is 'Direct',  you 
                        can not specify the type. But, for 'Cartesian', must be given. the valid formation:
                            ['Na', 0.1, 0.0, 0.0, 'Direct']
                            ['Na', 0.1, 0.0, 0.0]
                            ['Na', 5.234, 0.0, 0.0, 'Cartesian']
                    lattice: this structure's lattice parameter. It need to be given when the type of atomic coordinate is 'Cartesian'.     
                    precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                        to determine whether this atom is in collection by comparing its distance 
                        from other atoms.
                    
            
            collection: collection of entities.
            entity_type: type of entity. valid value is 'prototype', 'structure', 'composition', 'element', 'species',
                 'atom' and 'site'.
        Returns:
            True if the element exists. Conversely, False.
        """
        import warnings
        from jump2.db.utils.convert import any2direct
        
        entity_type=entity_type.strip().lower()
        if entity_type == 'prototype':
            from jump2.db.materials.prototype import Prototype
            
            if isinstance(entity, Prototype):
                for prototype in collection:
                    if prototype == entity:
                        return True
            return False
        
        elif entity_type == 'structure':
            from jump2.db.materials.structure import Structure
            
            if isinstance(entity, Structure):
                for structure in collection:
                    if structure == entity:
                        return True
            return False
        
        elif entity_type == 'composition':
            from jump2.db.materials.composition import Composition
            
            formula=None
            if isinstance(entity, Composition):
                formula=entity.formula
            elif isinstance(entity, basestring):
                formula=entity
                
            if collection == [] or (collection is None):
                return False
            else:
                for composition in collection:
                    if composition.formula == formula:
                        return True
            return False
            
        elif entity_type == 'element':
            from jump2.db.materials.element import Element
            
            symbol=None
            if isinstance(entity, Element):
                symbol=entity.symbol
            elif isinstance(entity, basestring):
                symbol=entity
            
            if collection == [] or (collection is None):
                return False
            else:
                for element in collection:
                    if element.symbol == symbol:
                        return True
            return False
        
        elif entity_type == 'species':
            from jump2.db.materials.species import Species
            
            name=None
            if isinstance(entity, Species):
                name=entity.name
            elif isinstance(entity, basestring):
                name=entity
            
            if collection == [] or (collection is None):
                return False
            else:
                for species in collection:
                    if species.name == name:
                        return True
                    
            return False
        
        elif entity_type == 'atom':
            from jump2.db.materials.atom import Atom
            
            if isinstance(entity, Atom):
                for atom in collection:
                    if atom == entity:
                        return True
            elif check_formated_atom(entity):
                precision=1e-3
                if 'precision' in kwargs:
                    precision=kwargs['precision']
                    
                for atom in collection:
                    if atom.element.symbol == entity[0]:
                        distance=None
                        if check_formated_atom_only_cartesian(entity): # Cartesian
                            if not 'lattice' in kwargs:
                                raise ValueError("need to be given the 'lattice'")
                            distance=atom.position-np.array(any2direct(kwargs['lattice'], entity[1:4]))
                        elif check_formated_atom_only_direct(entity):
                            distance=atom.position-np.array(entity[1:4])
                        else:
                            warnings.warn('invalid entity')
                        if np.linalg.norm(distance) <= precision:
                            return True
            return False
        
        elif entity_type == 'site':
            from jump2.db.materials.site import Site
            
            if isinstance(entity, Site):
                for site in collection:
                    if site == entity:
                        return True
            return False
        
        elif entity_type == 'operation':
            from jump2.db.materials.spacegroup import Operation
            
            if isinstance(entity, Operation):
                for operation in collection:
                    if operation == entity:
                        return True
            return False
        
        elif entity_type == 'spacegroup':
            from jump2.db.materials.spacegroup import Spacegroup
            
            if isinstance(entity, Spacegroup):
                for spacegroup in collection:
                    if spacegroup == entity:
                        return True
            return False
        
        elif(entity_type == 'wyckoffSite'):
            from jump2.db.materials.spacegroup import WyckoffSite
            
            if isinstance(entity, WyckoffSite):
                for wyckoffSite in collection:
                    if (wyckoffSite.symbol == entity.symbol) and (wyckoffSite.multiplicity == entity.multiplicity):
                        return True
            return False

                                
def check_formated_atom(atom):
    """
    check whether the format of atom is valid. 
    Arguments:
        atom: formated atom. if type of coordinate is 'Direct',  you can not specify
            the type. But, for 'Cartesian', must be given. the valid formation:
                ['Na', 0.1, 0.0, 0.0, 'Direct']
                ['Na', 0.1, 0.0, 0.0]
                ['Na', 5.234, 0.0, 0.0, 'Cartesian']
    """
    from jump2.db.utils.initialization.init_elements import elements as ptable
    
    if not(isinstance(atom, list) or isinstance(atom, np.ndarray)):
        return False
    if len(atom) != 4 and len(atom) != 5:
        #raise ValueError('invalid entity')
        return False
    if  not atom[0] in ptable: # atoms is dictionary in 'utils.initialization.init_elements'
        #raise ValueError("invalid atom's symbol in entity")
        return False
    if len(atom) == 5 and \
        not(atom[-1].strip().lower().startswith('d') or atom[-1].strip().lower().startswith('c')):
        #raise ValueError('invalid type of atomic coordinate in entity')
        return False
    #for v in atom[1:4]:
    #    if not v.isdigit():
    #        return False 
    return True

def check_formated_atom_only_direct(atom):            
    """
    check whether the format of atom is valid. 
    Arguments:
        atom: formated atom. The type of coordinate is only 'Direct',  you can not specify
            the type. The valid formation:
                ['Na', 0.1, 0.0, 0.0, 'Direct']
                ['Na', 0.1, 0.0, 0.0]
    """
    from jump2.db.utils.initialization.init_elements import elements as ptable
    
    if len(atom) != 4 and len(atom) != 5:
        return False
    if  not atom[0] in ptable: # atoms is dictionary in 'utils.initialization.init_elements'
        return False
    if len(atom) == 5 and (not atom[-1].strip().lower().startswith('d')):
        return False
    return True

def check_formated_atom_only_cartesian(atom):            
    """
    check whether the format of atom is valid. 
    Arguments:
        atom: formated atom. The type of coordinate is only 'Cartesian',  you must specify
            the type. The valid formation:
                ['Na', 2.3, 1.4, 0.0, 'Cartesian']
    """
    from jump2.db.utils.initialization.init_elements import elements as ptable
    
    if len(atom) != 5:
        return False
    if  not atom[0] in ptable: # atoms is dictionary in 'utils.initialization.init_elements'
        return False
    if not atom[-1].strip().lower().startswith('c'):
        return False
    return True

def check_formated_position(position):
    """
    check whether the format of position is valid. 
    Arguments:
        position: formated position. if type of coordinate is 'Direct',  you can not specify
            the type. But, for 'Cartesian', must be given. the valid formation:
                [0.1, 0.0, 0.0, 'Direct']
                [0.1, 0.0, 0.0]
                [5.234, 0.0, 0.0, 'Cartesian']
    """
    if len(position) != 3 and len(position) != 4:
        return False
    if len(position) == 4 and \
        not(position[-1].strip().lower().startswith('d') or position[-1].strip().lower().startswith('c')):
        return False
    #for v in position[:3]:
    #    if not v.isdigit():
    #        return False 
    return True

def check_formated_position_only_direct(position):
    """
    check whether the format of position is valid. 
    Arguments:
        position: formated position. The type of coordinate is only 'Direct',  you can not specify
            the type. The valid formation:
                [0.1, 0.0, 0.0, 'Direct']
                [0.1, 0.0, 0.0]
    """
    if len(position) != 3 and len(position) != 4:
        return False
    elif len(position) == 4 and not(position[-1].strip().lower().startswith('d')):
        return False
    return True

def check_formated_position_only_cartesian(position):
    """
    check whether the format of position is valid.
     
    Arguments:
        position: formated position. The type of coordinate is only 'Cartesian',  you must specify
            the type. The valid formation:
                [5.234, 0.0, 0.0, 'Cartesian']
    """
    if len(position) != 4:
        return False
    elif not position[-1].strip().lower().startswith('c'):
        return False
    return True

def check_constraint(constraint):
    """
    check whether the value of constraint is boolean.
    
    Arguments:
        constraint: array of boolean. The valid formation: [False, False, True].
    """
    for value in constraint:
        if not isinstance(value, bool):
            return False
    return True

def compare_with_memory(collection, structure, dtype, **kwargs):
    """
    compare between given collection and build-in array in memory.
    
    Arguments:
        collection: given collection. i.e. structure.atoms
            for atom:
                [[symbol_of_element0, x0, y0, z0],
                 [symbol_of_element1, x1, y1, z1],
                 [symbol_of_element2, x2, y2, z2],...]
                 
        structure: structure's object.
        dtype: type of data in collection. i.e. 'atom'
    
    Returns:
        different parts in given collection and build-in array in memory {'collection':[xxx,xxx,...], 'memory':[xxx,xxx,...]}
    """
    from copy import copy
    from jump2.db.materials.atom import Atom
    
    result=None
    
    if dtype.strip().lower() == 'atom':
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
        
        egas=copy(collection) # exclusive given atoms
        ebas=copy(structure.atoms) # exclusive build-in atoms
    
        for ga in copy(egas): # ga: given atom
            for ba in copy(ebas): # ba: build-in atom
                symbol=None
                position=None
                if isinstance(ga, list) or isinstance(ga, np.ndarray):
                    symbol=ga[0]
                    position=ga[1:4]
                elif isinstance(ga, Atom):
                    atom=ga
                    symbol=atom.element.symbol
                    position=atom.position
                distance=ba.position-np.array(position)
                if ba.element.symbol == symbol and np.linalg.norm(distance) <= precision:
                    egas.remove(ga)
                    ebas.remove(ba)
        result={'collection':egas, 'memory':ebas}
        return result

def compare_with_db(collection, structure, dtype, **kwargs):
    """
    compare between build-in array and array in database.
    
    Arguments:
        collection: collection of build-in array. i.e. structure.atoms
        structure: structure's object.
        dtype: type of data in collection. i.e. 'atom'
    
    Returns:
        different parts in memory and database {'memory':[xxx,xxx,...], 'db':[xxx,xxx,...]}
    """
    from copy import copy
    
    result={'memory':None, 'db':None}
    
    if not structure.id: # non-existent in database
        result['memory']=collection
        result['db']=None
        return result
        
    if dtype.strip().lower() == 'element':
        eims=copy(collection) # elements in memory
        eibs=list(structure.element_set.all()) # elements in database
        for eim in copy(collection):
            for eib in copy(eibs):
                if eib.symbol == eim.symbol:
                    eims.remove(eim)
                    eibs.remove(eib)
        result={'memory':eims, 'db':eibs}
        return result
    elif dtype.strip().lower() == 'species':
        sims=copy(collection) # species in memory
        sibs=list(structure.species_set.all()) # species in database
        for sim in copy(collection):
            for sib in copy(sibs):
                if sib.name == sim.name:
                    sims.remove(sim)
                    sibs.remove(sib)
        result={'memory':sims, 'db':sibs}
        return result
    elif dtype.strip().lower() == 'atom':
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
            
        aims=copy(collection) # atoms in memory
        aibs=list(structure.atom_set.all()) # atoms in database
        for aim in copy(collection):
            for aib in copy(aibs):
                distance=aib.position-aim.position
                if aib.element.symbol == aim.element.symbol and np.linalg.norm(distance) <= precision:
                    aims.remove(aim)
                    aibs.remove(aib)
        result={'memory':aims, 'db':aibs}
        return result
    elif dtype.strip().lower() == 'site':
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
            
        sims=copy(collection) # sites in memory
        sibs=list(structure.site_set.all()) # sites in database
        for sim in copy(collection):
            for sib in copy(sibs):
                distance=sib.position-sim.position
                if np.linalg.norm(distance) <= precision:
                    sims.remove(sim)
                    sibs.remove(sib)
        result={'memory':sims, 'db':sibs}
        return result
        
def check_formated_angle(theta):
    """
    check whether the format of angle is valid. 
    Arguments:
        theta: formated angle. The valid formation:
                [90, 'Degree']
                [1.2, 'Radian']
    """
    if (isinstance(theta, list) or isinstance(theta, np.ndarray)) and len(theta) == 2 and (theta[-1].strip().lower().startswith('d') or theta[-1].strip().lower().startswith('r')):
        return True
    else:
        return False

def check_formated_angle_only_degree(theta):
    """
    check whether the format of angle is valid. 
    Arguments:
        theta: formated angle. The valid formation:
                [90, 'Degree']
    """
    if (isinstance(theta, list) or isinstance(theta, np.ndarray)) and len(theta) == 2 and theta[-1].strip().lower().startswith('d'):
        return True
    else:
        return False

def check_formated_angle_only_radian(theta):
    """
    check whether the format of angle is valid. 
    Arguments:
        theta: formated angle. The valid formation:
                [90, 'Radia']
    """
    
    if (isinstance(theta, list) or isinstance(theta, np.ndarray)) and len(theta) == 2 and theta[-1].strip().lower().startswith('r'):
        return True
    else:
        return False
    
    
