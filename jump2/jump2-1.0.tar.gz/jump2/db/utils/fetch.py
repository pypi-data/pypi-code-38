'''
Created on Dec 11, 2017

@author: Yuhao Fu
'''
import numpy as np

def get_entity_from_collection(entity, collection, entity_type, **kwargs):
    """
    get a entity's object from collection.
        
    Arguments:
        entity: 
            for atom: 
                atom's object or formated string. For formated string, if type of coordinate is 'Direct', you 
                    can not specify the type. But, for 'Cartesian', must be given. the valid formation:
                        ['Na', 0.1, 0.0, 0.0, 'Direct']
                        ['Na', 0.1, 0.0, 0.0]
                        ['Na', 5.234, 0.0, 0.0, 'Cartesian']
            
            for site:
                site's position. Note that type of coordinate is 'Direct',  you can not specify
                    the type. The valid formation:
                        [0.1, 0.0, 0.0, 'Direct']
                        [0.1, 0.0, 0.0]
                        [5.234, 0.0, 0.0, 'Cartesian']
                
        kwargs:
            isNormalizingCoordinate (default=True): whether to remove the periodic boundary condition, 
                    ensure the value of atomic coordinate is between 0 and 1 (i.e. 1.3 -> 0.3).
            precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                    to determine whether this atom is in collection by comparing its distance 
                    from other atoms.
            lattice: this structure's lattice parameter.
                
    Returns:
        entity's object if exist. Conversely, None.
    """
    from jump2.db.utils.check import check_formated_atom, check_formated_atom_only_cartesian
    from jump2.db.utils.check import check_formated_position, check_formated_position_only_cartesian
    from jump2.db.utils.convert import any2direct, normalize_position
    
    result=None
    if entity_type == 'atom':
        # remove atomic translation periodicity
        isNormalizingCoordinate=True
        if 'isNormalizingCoordinate' in kwargs:
            isNormalizingCoordinate=kwargs['isNormalizingCoordinate']
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
            
        if check_formated_atom(entity):
            for i in xrange(0, len(collection)):
                if collection[i].element.symbol == entity[0]:
                    position=None
                    #if len(entity) == 5 and entity[-1].strip().lower().startswith('c'): # Cartesian
                    if check_formated_atom_only_cartesian(entity):
                        if not 'lattice' in kwargs:
                            raise ValueError("need to be given the 'lattice'")
                        lattice=kwargs['lattice']
                        position=any2direct(lattice, entity[1:5])
                    else:
                        position=entity[1:]
                        
                    if isNormalizingCoordinate:
                        position=normalize_position(position, 'Direct')[:-1]
                    distance=collection[i].position-np.array(position)
                    if np.linalg.norm(distance) <= precision:
                        result=collection[i]
    elif entity_type == 'site':
        # remove atomic translation periodicity
        isNormalizingCoordinate=True
        if 'isNormalizingCoordinate' in kwargs:
            isNormalizingCoordinate=kwargs['isNormalizingCoordinate']
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
            
        position=entity
        if check_formated_position(position):
            for site in collection:
                if check_formated_position_only_cartesian(position):
                    position=any2direct(site.structure.lattice, position)
                
                if isNormalizingCoordinate:
                    position=normalize_position(position, 'Direct')[:-1]
                distance=site.position-np.array(position)
                if np.linalg.norm(distance) <= precision:
                    result=site
            
    return result

def get_entity_from_collection4molecule(entity, collection, entity_type, **kwargs):
    """
    get a entity's object from collection.
        
    Arguments:
        entity: 
            for atom: 
                atom's object or formated string. For formated string, if type of coordinate is only 'Cartesian', you 
                    must specify the type. The valid formation:
                        ['Na', 2.3, 1.4, 0.0, 'Cartesian']
                
        kwargs:
            precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                    to determine whether this atom is in collection by comparing its distance 
                    from other atoms.
                
    Returns:
        entity's object if exist. Conversely, None.
    """
    from jump2.db.utils.check import check_formated_atom_only_cartesian
    
    result=None
    if entity_type == 'atom':
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
            
        if check_formated_atom_only_cartesian(entity):
            for i in xrange(0, len(collection)):
                if collection[i].element.symbol == entity[0]:
                    distance=collection[i].position-np.array(entity[1:4])
                    if np.linalg.norm(distance) <= precision:
                        result=collection[i]
        return result  
                    
def get_index_from_collection(index_or_entity, collection, entity_type, **kwargs):
    """
    get the index of entity from the collection.
        
    Arguments:
        index_or_entity: entity's index or object.
        collection: collection of entity.
        entity_type: type of entity.
        
        kwargs:
            for position type:
                lattice: lattice parameter of structure. i.e.
                    [[x1,y1,z1],
                     [x2,y2,z2],
                     [x3,y3,z3]]
                precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                        to determine whether this atom is in collection by comparing its distance 
                        from other atoms.
    Return:
        index if exist. Conversely, False.
    """
    from jump2.db.utils.check import exist, check_formated_position_only_direct, check_formated_position_only_cartesian
    from jump2.db.utils.convert import cartesian2direct
    from jump2.db.materials.atom import Atom
    
    index=None    
    if isinstance(index_or_entity, int):
        if index_or_entity < 0 or index_or_entity > len(collection):
            raise ValueError('index out of range')
        index=index_or_entity
    elif entity_type == 'atom' and isinstance(index_or_entity, Atom) and exist(index_or_entity, collection, entity_type):
        index=collection.index(index_or_entity)
    elif entity_type == 'position':
        
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
                    
        position=index_or_entity
        if check_formated_position_only_cartesian(position):
            if not 'lattice' is kwargs:
                raise ValueError('lattice must be given')
            lattice=kwargs['lattice']
            position=cartesian2direct(lattice, position)
        if check_formated_position_only_direct(position):
            collection=np.array(collection)
            for i in xrange(0, collection.shape[0]):
                distance=collection[i]-np.array(position)
                
                # note the periodic boundary condition. like [0.0, 0.0, 0.0] vs. [0.999999, 0.0, 0.0]
                for j in xrange(0, len(distance)):
                    if distance[j] > 0.5:
                        distance[j]=1-distance[j]
                    elif distance[j] < -0.5:
                        distance[j]=1+distance[j]
                
                if np.linalg.norm(distance) <= precision:
                    if index is None:
                        index=i
                    else:
                        raise ValueError('exist reduplicative positon')

    return index
    

def get_formated_atom(atom):
    """
    get the formated atom from its object.
    
    Arguments:
        atom: atom's object.
        
    Returns:
        return formated atom. Note that the type of atomic coordinate is only 'Direct'. 
            Inside the jump2, the atomic coordinate is saved by type 'Direct' for crystal structure.
    """
    from jump2.db.materials.atom import Atom
    
    if not isinstance(atom, Atom):
        raise ValueError("atom is not a instance of class Atom")
    
    return [atom.element.symbol, atom.position[0], atom.position[1], atom.position[2]]
               

def get_time():
    """
    Returns:
        current time.
    """
    import time
    
    return time.strftime("%m-%d-%Y %H:%M:%S:", time.localtime(time.time()))




# -------------------- for database --------------------
def get_operation_from_db(operation, **kwargs):
    """
    get given operation's object in database.
    
    Arguments:
        operation: {'translation': np.ndarray ([3] (float)), 'rotation': np.ndarray ([3,3] (int))}
                
        kwargs:
            precision (default=1e-3): used to determine whether the two vector of translation are overlapped. Note that, 
                to determine whether this translation is in database by comparing its distance from other operations.
    
    Returns:
        operation's object if exist. Conversely, None.
    """
    from jump2.db.materials.spacegroup import Operation
    
    precision=1e-3
    if 'precision' in kwargs:
        precision=kwargs['precision']
        
    operations_in_db=list(Operation.objects.all())
    if operations_in_db != []:
        for obj in operations_in_db:
            distance=np.array(operation['translation'])-obj.operation['translation']
                
            if (np.linalg.norm(distance) <= precision) and \
                (not(False in (obj.operation['rotation'] == operation['rotation']))):
                return obj
    return None

def get_wyckoffSite_from_db(formated_wyckoffSite, **kwargs):
    """
    get given wyckoffSite's object in database.
    
    Arguments:
        formated_wyckoffSite: [symbol, multiplicity, x, y, z]. i.e. ['a', 6, 0.000000, 0.000000, 0.250000]
        
        kwargs:
            precision (default=1e-3): used to determine whether the two vector of translation are overlapped. Note that, 
                to determine whether this translation is in database by comparing its distance from other wyckoffSites.
    
    Returns:
        wyckoffSite's object if exist. Conversely, None.
    """
    from jump2.db.materials.spacegroup import WyckoffSite
    
    # check
    if len(formated_wyckoffSite) != 5:
        raise ValueError('invalid formated_wyckoffSite')
    
    precision=1e-3
    if 'precision' in kwargs:
        precision=kwargs['precision']
    
    wyckoffSites_in_db=list(WyckoffSite.objects.all())
    if wyckoffSites_in_db != []:
        for obj in wyckoffSites_in_db:
            symbol=formated_wyckoffSite[0]
            multiplicity=formated_wyckoffSite[1]
            distance=obj.position-np.array(formated_wyckoffSite[2:])
            if (obj.symbol == symbol) and (obj.multiplicity == multiplicity) and (np.linalg.norm(distance) <= precision):
                return obj
    return None

def get_site_from_db(position, **kwargs):
    """
    get given site's object in database.
    
    Arguments:
        position: position of site. i.e. [0.000000, 0.000000, 0.250000]
        
        kwargs:
            precision (default=1e-3): used to determine whether the two vector of translation are overlapped. Note that, 
                to determine whether this translation is in database by comparing its distance from other wyckoffSites.
    
    Returns:
        site's object if exist. Conversely, None.
    """
    from jump2.db.materials.site import Site
    
    precision=1e-3
    if 'precision' in kwargs:
        precision=kwargs['precision']

    sites_in_db=list(Site.objects.all())
    if sites_in_db != []:
        for obj in sites_in_db:
            distance=obj.position-np.array(position)
            if np.linalg.norm(distance) <= precision:
                return obj
    return None

def get_atoms_from_cell(cell):
    """
    fetch atoms from cell-type structure.
    
    Arguments:
        cell: cell-type structure. The valid format is:
            {'lattice':lattice,
             'positions':positions,
             'numbers':numbers,
             'magmoms':magmoms(optional)}
        
    Returns:
        collection of atoms.
    """
    from jump2.db.materials.element import Element
    
    positions=cell['positions']
    numbers=cell['numbers'] # z of atoms
    
    atoms=[]
    for i in xrange(0, len(numbers)):
        symbol=Element.objects.filter(z=numbers[i])[0].symbol
        atoms.append([symbol]+positions[i].tolist())
    return atoms

def get_symbol_by_z(z):
    """
    get element's symbol by given atomic number (z).
    
    Arguments:
        z: atomic number.
        
    Returns:
        element's symbol if exist. Conversely, None.
    """
    import warnings
    from jump2.db.utils.initialization.init_elements import elements
    
    result=None
    for key in elements.keys():
        if elements[key][0] == z:
            result=key
    return result

def get_z_by_symbol(symbol):
    """
    get atomic number (z) by element's symbol.
    
    Arguments:
        symbol: element's symbol. i.e. Na
        
    Returns:
        atomic number if exist. Conversely, None.
    """
    import warnings
    from jump2.db.utils.initialization.init_elements import elements
    
    result=None
    
    if symbol in elements:
       result=elements[symbol][0]
    return result 
            