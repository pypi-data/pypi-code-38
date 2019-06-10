'''
Created on Dec 11, 2017

@author: Yuhao Fu
'''
import numpy as np

def cartesian2direct(lattice, position):
    """
    convert Cartesian to Direct.
    
    Arguments:
        lattice: lattice parameter of structure. i.e.
            [[x1,y1,z1],
             [x2,y2,z2],
             [x3,y3,z3]]
             
        position: atomic position (type: Cartesian). i.e. [5.234, 0, 0]
        
    Returns:
        atomic position (type: Direct). i.e. [0.1, 0, 0]
    """
    inv=np.linalg.inv(lattice).T
    direct=np.dot(inv,position)

    return direct

def direct2cartesian(lattice, position):
    """
    convert Direct to Cartesian.
    
    Arguments:
        lattice: lattice parameter of structure. i.e.
            [[x1,y1,z1],
             [x2,y2,z2],
             [x3,y3,z3]]
             
        position: atomic position (type: Direct). i.e. [0.1, 0, 0].
        
    Returns:
        atomic position (type: Cartesian). i.e. [5.234, 0, 0]
    """
    return np.dot(position, lattice)

def any2direct(lattice, position):
    """
    convert it to Direct if type of position is Cartesian. do not anything if that is Direct.
    
    Arguments:
        lattice: lattice parameter of structure. i.e.
            [[x1,y1,z1],
             [x2,y2,z2],
             [x3,y3,z3]]
             
        position: atomic position. The valid format is :
            [0.1, 0, 0, 'Direct']
            [0.1, 0, 0] (for Direct, can not be specify)
            [5.234, 0, 0, 'Cartesian'] (for Cartesian, must be given)
    
    Returns:
        atomic position (type: Direct). i.e. [0.1, 0, 0]
    """
    if len(position) == 3:
        return position
    elif len(position) == 4:
        if position[-1].strip().lower().startswith('d'):
            return position[:3]
        elif position[-1].strip().lower().startswith('c'):
            return cartesian2direct(lattice, position[:3])
        
def any2cartesian(lattice, position):
    """
    convert it to Cartesian if type of position is Direct. do not anything if that is Cartesian.
    
    Arguments:
        lattice: lattice parameter of structure. i.e.
            [[x1,y1,z1],
             [x2,y2,z2],
             [x3,y3,z3]]
             
        position: atomic position. The valid format is:
            [0.1, 0, 0, 'Direct']
            [0.1, 0, 0] (for Direct, can not be specify)
            [5.234, 0, 0, 'Cartesian'] (for Cartesian, must be given)
            
    Returns:
        atomic position (type: Cartesian). i.e. [5.234, 0, 0]
    """
    if len(position) == 3:
        return direct2cartesian(lattice, position)
    elif len(position) == 4:
        if position[-1].strip().lower().startswith('d'):
            return direct2cartesian(lattice, position[:3])
        elif position[-1].strip().lower().startswith('c'):
            return position[:3]    

def normalize_position(position, dtype, **kwargs):
#def normalize_position(position, **kwargs):
    """
    remove the translation periodicty of atomic position, ensure coordinate's values are between 0 and 1.
    i.e. for Direct type, [1.1, 0, 0] -> [0.1, 0, 0]
    
    Arguments:
        position: atomic position. the valid format:
            [0.1, 0.0, 0.0, 'Direct']
            [0.1, 0.0, 0.0]
            [5.234, 0.0, 0.0, 'Cartesian']
        dtype: type of coordinate after translating ('Direct' or 'Cartesian').
            
        kwargs:
            lattice: lattice parameter of structure. need to be given when dtype is Cartesian. i.e.
                [[x1,y1,z1],
                 [x2,y2,z2],
                 [x3,y3,z3]]
            precision (default=1e-5): used to determine whether the component of position is very close to 1.
                    from other atoms.
                    
    Returns:
        converted positionincluded the type (list). i.e. [0.1, 0, 0, 'Direct'], [5.234, 0.0, 0.0, 'Cartesian']
    """
    from jump2.db.utils.check import check_formated_position
    
    new_position=[]
    if check_formated_position(position):
        if len(position) == 4 and position[-1].strip().lower().startswith('c'): # Cartesian
            if not 'lattice' in kwargs:
                raise Exception("can't find the 'lattice' parameter")
            lattice=np.array(kwargs['lattice'])
            
            for i in xrange(0, 3):
                length=np.linalg.norm(lattice[i]) # module of lattice. i.e. a, b, c
                proj=np.dot(position, lattice[i]/length) # project length on the corresponding to the direction of the lattice parameter.
                
                if proj >= 0:
                    nperiodic=int(np.divide(proj, length)) # number of periodic on this direction.
                    new_position -= lattice[i]*nperiodic
                elif proj < 0:
                    if proj > -length:
                        new_position += lattice[i]
                    else:
                        nperiodic=np.abs(np.around(np.divide(proj, length))) # needed number of periodic on this direction. i.e. for proj=-3.2, length=2 -> nperiodic=2
                        new_position += lattice[i]*nperiodic
        elif len(position) == 3 or (len(position) == 4 and position[-1].strip().lower().startswith('d')): # Direct
            
            for v in position[:3]:
                new_v=v-int(v) # fraction of v
                if new_v < 0:
                    new_v += 1
                new_position.append(new_v)
            new_position.append('Direct')
    
    # check
    precision=1e-5
    if 'precision' in kwargs:
        precision=kwargs['precision']
    for i in xrange(0, len(new_position)-1):
        if np.linalg.norm(1-new_position[i]) <= precision:
            new_position[i]=0.0
    if dtype.strip().lower().startswith('d'): # Direct
        return new_position
    elif dtype.strip().lower().startswith('c'): # Cartesian
        lattice=np.array(kwargs['lattice'])
        position=new_position
        new_position=any2cartesian(lattice, position)
        return new_position


def cell2poscar(cell):
    """
    convert cell to poscar.
    
    Arguments:
        cell: cell-typed structure. The valid format is:
            {'lattice':lattice,
             'positions':positions,
             'numbers':numbers,
             'magmoms':magmoms(optional)}
             
    Returns:
        poscar-typed structure. The valid format is:
            {'lattice': lattice,
             'elements': elements,
             'numbers': numbers,
             'type': 'Direct',
             'positions': positions}
    """
    from collections import OrderedDict
    from jump2.db.materials.element import Element
    
    lattice=cell['lattice']
    
    # elements, numbers and position
    atom_set=OrderedDict() # elements and its positions
    
    for i in xrange(0, len(cell['numbers'])):
        symbol=Element.objects.filter(z=cell['numbers'][i])[0].symbol
        if symbol in atom_set:
            tmp=atom_set[symbol]
            tmp.append(cell['positions'][i].tolist())
            atom_set[symbol]=tmp
        else:
            atom_set[symbol]=[cell['positions'][i].tolist()]
    elements=[]
    numbers=[]
    positions=[]
    for k in atom_set.keys():
        elements.append(k)
        numbers.append(len(atom_set[k]))
        if positions ==[]:
            positions=atom_set[k]
        else:
            positions=np.vstack((positions, atom_set[k]))
    elements=np.array(elements)
    numbers=np.array(numbers)
    
    poscar={'lattice': lattice,
            'elements': elements,
            'numbers': numbers,
            'type': 'Direct',
            'positions': positions}
    return poscar

def poscar2cell(poscar):
    """
    convert poscar to cell.
    
    Arguments:
        poscar: poscar-typed structure. The valid format is:
            {'lattice': lattice,
             'elements': elements,
             'numbers': numbers,
             'type': 'Direct',
             'positions': positions}
             
    Returns:
        cell-typed structure. The valid format is:
            {'lattice':lattice,
             'positions':positions,
             'numbers':numbers,
             'magmoms':magmoms(optional)}
    """
    from jump2.db.utils.fetch import get_z_by_symbol
    
    lattice=poscar['lattice']
    positions=poscar['positions']
    numbers=[]
    for i in xrange(0, len(poscar['elements'])):
        for j in xrange(0, poscar['numbers'][i]):
            numbers.append(get_z_by_symbol(poscar['elements'][i]))
    cell={'lattice':lattice, 'positions':positions, 'numbers':numbers}
    return cell

def to_poscar5x(path_of_poscar4x, path_of_poscar5x):
    """
    convert poscar4.x to poscar5.x.
    
    Arguments:
        path_of_poscar4x: path of poscar4x.
        path_of_poscar5x: path of converted poscar5.x.
    Returns:
        output new poscar5.x file.
    """
    # check
    f=open(path_of_poscar4x, 'r')
    contents=f.readlines()
    f.close()
    
    contents.insert(5, contents[0])
    
    f=open(path_of_poscar5x, 'w')
    contents=''.join(contents)
    f.write(contents)
    f.close()
    

def raw2std_position(position, transformation_matrix, origin_shift):
    """
    convert non-conventional position (raw position from input structure in IO stream) to standardized position.
    
    position_std=transformation_matrix*position_input+origin_shif (mod 1).
    
    Arguments:
        position: input position of atom [1x3].
        transformation_matrix: array-like [3x3].
        origin_shift: array-like [1x3].
    
    Returns:
        standardized position.
    """
    I=np.identity(3) # unit matrix
    
    position=np.array(position)
    transformation_matrix=np.array(transformation_matrix)
    origin_shift=np.transpose(origin_shift)
    
    position_std=None
#    for i in xrange(0,position.shape[0]):
#        tmp=np.dot(transformation_matrix, position[i]*np.transpose(I[i]))+origin_shift
#        if position_std is None:
#            position_std=tmp
#        else:
#            position_std += tmp
            
    for i in xrange(0,position.shape[0]):
        tmp=np.dot(transformation_matrix, position[i]*np.transpose(I[i]))
        if position_std is None:
            position_std=tmp
        else:
            position_std += tmp
    position_std += origin_shift
    position_std=normalize_position(position_std, dtype='Direct')[:-1]
    return position_std

def translation(position, direction):
    """
    rotation position.
    
    Arguments:
        position: atomic position. The valid format:
            [0.1, 0.0, 0.0, 'Direct']
            [0.1, 0.0, 0.0]
            [5.234, 0.0, 0.0, 'Cartesian']
        direction: direction vector to add the vacuum along lattice vector(a/b/c). The valid format is :
            [0.1, 0, 0, 'Direct']
            [0.1, 0, 0] (for Direct, can not be specify)
            [5.234, 0, 0, 'Cartesian'] (for Cartesian, must be given)
    
    Returns:
        new position.
    """
    from jump2.db.utils.check import check_formated_position_only_cartesian, check_formated_position_only_direct
    
    # check
    new=None
    if check_formated_position_only_direct(position) and check_formated_position_only_direct(direction):
        tmp=np.array(position[:3])+np.array(direction[:3])
        new=[tmp[0], tmp[1], tmp[2], 'Direct']
    elif check_formated_position_only_cartesian(position) and check_formated_position_only_cartesian(direction):
        tmp=np.array(position[:3])+np.array(direction[:3])
        new=[tmp[0], tmp[1], tmp[2], 'Cartesian']
    #else:
    #    raise ValueError('unmatched type between position and direction')
    return new
    
def rotation(position, axis, theta, **kwargs):            
    """
    rotation position. if giving origin, rotation axis will not through the coordinate origin [0,0,0]. given origin is start point of axis.
    
    Arguments:
        position: atomic position. The valid format:
            [0.1, 0.0, 0.0, 'Direct']
            [0.1, 0.0, 0.0]
            [5.234, 0.0, 0.0, 'Cartesian']
        axis: rotation axis. The valid format:
            [0.1, 0.0, 0.0, 'Direct']
            [0.1, 0.0, 0.0]
            [5.234, 0.0, 0.0, 'Cartesian']
        theta: rotation angle. The valid format:
            [30, 'Degree']
            [0.2, 'Radian']
            
        kwargs:
            origin: rotation origin. The valid format:
                [0.1, 0.0, 0.0, 'Direct']
                [0.1, 0.0, 0.0]
                [5.234, 0.0, 0.0, 'Cartesian']
    
    Returns:
        new position.
    """        
    import math
    from jump2.db.utils.check import check_formated_position_only_cartesian, check_formated_position_only_direct, check_formated_angle
    
    # check
    tmpa=np.array(axis[:3])/np.linalg.norm(axis[:3])
    if len(axis) == 3:
        axis=[tmpa[0], tmpa[1], tmpa[2], 'Direct']
    else:
        axis=[tmpa[0], tmpa[1], tmpa[2], axis[-1]]
    
    origin=None
    if 'origin' in kwargs:
        origin=kwargs['origin']
    
    if not check_formated_angle(theta):
        raise ValueError('unrecognized theta')
    theta=any2radian(theta)
    theta=theta[0]
    ax=float(axis[0])
    ay=float(axis[1])
    az=float(axis[2])
    rotation_matrix=[[math.cos(theta)+(1-math.cos(theta))*math.pow(ax, 2), (1-math.cos(theta))*ax*ay-az*math.sin(theta), (1-math.cos(theta))*ax*az+ay*math.sin(theta)],
                     [(1-math.cos(theta))*ax*ay+az*math.sin(theta), math.cos(theta)+(1-math.cos(theta))*math.pow(ay, 2), (1-math.cos(theta))*ay*az-ax*math.sin(theta)],
                     [(1-math.cos(theta))*ax*az-ay*math.sin(theta), (1-math.cos(theta))*ay*az+az*math.sin(theta), math.cos(theta)+(1-math.cos(theta))*math.pow(az, 2)]]                
    
    new=None
    if origin is None:
        if check_formated_position_only_cartesian(position) and check_formated_position_only_cartesian(axis):
            tmp=np.dot(position, rotation_matrix)
            new=[tmp[0], tmp[1], tmp[2], 'Cartesian']
        elif check_formated_position_only_direct(position) and check_formated_position_only_direct(axis):
            tmp=np.dot(position, rotation_matrix)
            new=[tmp[0], tmp[1], tmp[2], 'Direct']
    else:
        if check_formated_position_only_cartesian(position) and check_formated_position_only_cartesian(axis) and check_formated_position_only_cartesian(origin):
            tmp=np.dot(np.array(position[:3])-np.array(origin[:3]), rotation_matrix)+np.array(origin[:3])
            new=[tmp[0], tmp[1], tmp[2], 'Cartesian']
        elif check_formated_position_only_direct(position) and check_formated_position_only_direct(axis) and check_formated_position_only_direct(origin):
            tmp=np.dot(np.array(position[:3])-np.array(origin[:3]), rotation_matrix)+np.array(origin[:3])
            new=[tmp[0], tmp[1], tmp[2], 'Direct']
    return new

def degree2radian(theta):
    """
    convert degree to radian.
    """
    import math
    from jump2.db.utils.check import check_formated_angle_only_degree
    
    if check_formated_angle_only_degree(theta):
        return [math.pi*(float(theta[0])/180.0),'Radian']
    else:
        raise ValueError('unrecognized theta')
    
def radian2degree(theta):
    """
    convert radian to degree.
    """
    import math
    from jump2.db.utils.check import check_formated_angle_only_radian
    
    if check_formated_angle_only_radian(theta):
        return [theta*180.0/math.pi, 'Degree']
    else:
        raise ValueError('unrecognized theta')
    
def any2radian(theta):
    """
    convert to radian.
    """
    import math
    from jump2.db.utils.check import check_formated_angle, check_formated_angle_only_degree
    
    if not check_formated_angle(theta):
        raise ValueError('unrecognized theta')
    if check_formated_angle_only_degree(theta):
        return [math.pi*(float(theta[0])/180.0),'Radian']
    else:
        return theta
    
def any2degree(theta):
    """
    convert to degree.
    """
    import math
    from jump2.db.utils.check import check_formated_angle, check_formated_angle_only_radian
    
    if not check_formated_angle(theta):
        raise ValueError('unrecognized theta')
    if check_formated_angle_only_radian(theta):
        return [theta*180.0/math.pi, 'Degree']
    else:
        return theta
            
        