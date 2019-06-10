#coding=utf-8
'''
Created on Nov 30, 2017

@author: Yuhao Fu, Bangyu Xing, qiaoling Xu
'''
import numpy as np
from numpy import absolute

class StructureFactoryError(Exception):
    pass

class StructureFactory(object):
    """
    structure factory.
    
    结构工厂类，操作结构方法的集合。注意：由于在更新对称信息时，对于一些结构在更新完对称信息后，结构会发生旋转。
    """
    def __init__(self, structure, isOperateOnSelf=False, **kwargs):
        """
        Arguments:
            structure: structure's object.
            isOperateOnSelf: Whether to operate itself.
            
            kwargs:
                isPersist (default=False): whether to save to the database.
            
        参数：
            structure:结构对象。
            isOperateOnSelf:操作结构时，是在自身上操作，还是先复制结构对象，然后在复制的对象上进行结构操作。
            
            kwargs:
                isPersist (default=False):是否持久化，即将结构保存到数据库中。注意：仅仅保存初始化的结构，后续的结构操作的保存，需要再次指定是否保存。
        """
        self.raw_structure=structure
        
        self.structure=None
        if isOperateOnSelf:
            self.structure=structure
        else:
            self.structure=structure.minimize_clone()
            
        isPersist=False
        if 'isPersist' in kwargs:
            isPersist=kwargs['isPersist']
            if not isinstance(isPersist, bool):
                raise ValueError('invalid isPersist')
        if isPersist:
            self.structure._persist()
    
    
    def zoom(self, scale, isPersist=False):
        """
        scale the lattice vector.
        
        Arguments:
            scale: coefficient of zoom for lattice parameters.
            isPersist (default=False): whether to save to the database.
            
        Returns:
            structureFactory's object.
            
        缩放晶胞基矢。
        
        参数：
            scale:缩放系数。
            isPersist (default=False):是否持久化，即更新数据库中对应的数据。
            
        返回：
            结构操作对象。
        """
        structure=self.structure
        lattice=structure.lattice
        structure.lattice=lattice*scale
        structure.volume=structure.calculate_volume()
        structure.volume_per_atom=structure.volume/structure.natoms
        if isPersist:
            structure._persist()
        self.structure=structure
        return self
 
    def add_atoms(self, atoms, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        add atoms to structure.
        
        Arguments:
            atoms: collection of atom's object or formated string. i.e. [atom0, atom1, atom2,...] 
                    ['Na', 0.1, 0.0, 0.0, 'Direct']
                    ['Na', 0.1, 0.0, 0.0]
                    ['Na', 5.234, 0.0, 0.0, 'Cartesian']
                    
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        
        Returns:
            structureFactory's object.
        """
        from jump2.db.utils.check import check_formated_atom
        from jump2.db.materials.atom import Atom
        
        structure=self.structure
        for atom in atoms:
            formated_atom=None
            if isinstance(atom, Atom):
                formated_atom=atom.to_formated()
            elif check_formated_atom(atom):
                formated_atom=atom
            else:
                raise ValueError('unrecognized atom')
            structure.add_atom(formated_atom)
        
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            structure.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            structure.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
        self.structure=structure
        return self
    
    def del_atoms(self, index_or_atoms, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        delete atoms from structure.
        
        Arguments:
            index_or_atoms: collection of atom's index, formated atom or object. i.e. [atom0, atom1, atom2,...] 
                    ['Na', 0.1, 0.0, 0.0, 'Direct']
                    ['Na', 0.1, 0.0, 0.0]
                    ['Na', 5.234, 0.0, 0.0, 'Cartesian']
                    
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        
        Returns:
            structureFactory's object.
        """
        from jump2.db.utils.check import check_formated_atom
        from jump2.db.materials.atom import Atom
        
        structure=self.structure
        for atom in index_or_atoms:
            formated_atom=None
            if isinstance(atom, int):
                index=atom
                if index < 0 or index > structure.natoms:
                    raise ValueError('beyond the range of atomic index')
                else:
                    formated_atom=structure.atoms[index].to_formated()
            elif isinstance(atom, Atom):
                formated_atom=atom.to_formated()
            elif check_formated_atom(atom):
                formated_atom=atom
            else:
                raise ValueError('unrecognized atom')
            status=structure.del_atom(formated_atom)
            if not status:
                raise StructureFactoryError('failed')
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            structure.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            structure.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
        self.structure=structure
        return self
    
    def substitute_atoms(self, index_or_atoms, symbol_of_elements, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        delete atoms from structure.
        
        Arguments:
            index_or_atoms: collection of atom's index, formated atom or object. i.e. [atom0, atom1, atom2,...] 
                    ['Na', 0.1, 0.0, 0.0, 'Direct']
                    ['Na', 0.1, 0.0, 0.0]
                    ['Na', 5.234, 0.0, 0.0, 'Cartesian']
            symbol_of_elements: element's symbol. If replacing by an element for all atom, you can only specify the a element' symbol.
                i.e. 'Na', ['Na', 'Na', 'Na']
                    
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        
        Returns:
            structureFactory's object.
        """
        from jump2.db.utils.check import check_formated_atom
        from jump2.db.materials.atom import Atom
        
        structure=self.structure
        for i in xrange(0, len(index_or_atoms)):
            formated_atom=None
            atom=index_or_atoms[i]
            if isinstance(atom, int):
                index=atom
                if index < 0 or index > structure.natoms:
                    raise ValueError('beyond the range of atomic index')
                formated_atom=structure.atoms[index].to_formated()
            elif isinstance(atom, Atom):
                formated_atom=atom.to_formated()
            elif check_formated_atom(atom):
                formated_atom=atom
            else:
                raise ValueError('unrecognized atom')
            
            if isinstance(symbol_of_elements, str):
                symbol_of_element=symbol_of_elements
                structure.substitute_atom(formated_atom, symbol_of_element)
            elif isinstance(symbol_of_elements, list) or isinstance(symbol_of_element, np.ndarray):
                symbol_of_element=symbol_of_elements[i]
                structure.substitute_atom(formated_atom, symbol_of_element)
        
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            structure.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            structure.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
        self.structure=structure
        return self
 
    def vacuum(self, direction, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        add vacuum along a direction.
        
        arguments:
            direction: direction vector to add the vacuum along lattice vector(a/b/c). The valid format is :
                [0.1, 0, 0, 'Direct']
                [0.1, 0, 0] (for Direct, can not be specify)
                [5.234, 0, 0, 'Cartesian'] (for Cartesian, must be given)
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup).
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                isCenter (default=True): whether to centralize for all atoms in structure.
                distance: moving distance for all atoms in the structure along the given direction (unit: Angstrom). i.e. 1.0 
                    Note that distance don't beyond the lattice after vacuuming (<= direction).
                #isConstraint (default=False):True/False .
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        
        Returns:
            structureFactory's object.
            
        沿着给定的方向，添加真空层。注意：当前的算法只会平移该晶胞内的原子。对于一些二维材料，层如果横跨两个晶胞，需要先移动晶胞，让层间距在晶胞边界上，确保结构的正确性。
        
        参数：
            direction:添加真空层的方向。注意：只能沿着晶胞基矢方向添加真空层。格式需要符合以下规则:
                [0.1, 0, 0, 'Direct']
                [0.1, 0, 0] (对于分数坐标，可以不用给出坐标类型)
                [5.234, 0, 0, 'Cartesian'] (对于笛卡尔坐标，必须给出坐标类型)
            isUpdatedInfo (default=False):是否更新结构的其他关联数据信息（如，化学式、不等价位置，等）。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                isCenter (default=True):添加真空层后，是否移动原子层到晶胞的中间。
                distance:添加真空层后，沿着添加真空层的方向，移动所有原子（单位：埃）。如，1.0。注意：移动的距离不能超出晶胞（<=direction）。
                symprec (default=1e-5):找结构对称性时，采用的精度。
                angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差值。
                
        返回：
            结构操作对象。
        """
        from jump2.db.utils.check import check_formated_position
        from jump2.db.utils.convert import any2cartesian
        structure=self.structure
        
        # check
        if not check_formated_position(direction):
            raise StructureFactoryError('invalid direction')
        direction=any2cartesian(structure.lattice, direction)
        mod=np.sum(direction) # summation of direction
        msod=np.sum(absolute(direction)) # summation of absolute direction
        if mod != msod or msod == 0:
            if -mod == msod:
                print 'Warning: compressing the vacuum'
            else:
                raise StructureFactoryError('invalid direction')
        
        isCenter=True
        if 'isCenter' in kwargs:
            isCenter=kwargs['isCenter']
        distance=None
        if 'distance' in kwargs:
            distance=kwargs['distance']
#         if isCenter and not(distance is None):
#             raise StructureFactoryError("can't be given between two parameters ('isCenter' and 'distance')")
        
        #isContraint=False # whether constraint atom
        #if 'isConstraint' in kwargs:
        #    isContraint=kwargs['isConstraint']
            
        lattice=structure.lattice
        lattice_parameters=structure.lattice_parameters
        # add vacuum layer
        for i in xrange(0, len(direction)):
            if direction[i] != 0: # vacuum direction
                scale=direction[i]/lattice_parameters[i] # part of vacuum
                lattice[i]=lattice[i]*(1+scale)
#                 scale2=None
#                 if distance != None:
#                     scale2=distance/structure.lattice_parameters[i]
#                 elif isCenter:
#                     scale2=0.5 # half of direction
                for atom in structure.atoms:
                    atom.position[i] /= (1+scale)
#                     if scale2 != None:  
#                         atom.position[i] += scale2
        # move atoms
        for i in xrange(0, len(direction)):
            if direction[i] != 0: # vacuum direction
                prange=[] # range of position along given direction.
                for atom in structure.atoms:
                    prange.append(atom.position[i])
                    
                scale=None
                if distance != None:
                    scale=distance/structure.lattice_parameters[i]
                    if scale+np.max(prange) > 1.0:
                        raise ValueError('distance is too large and move to the boundary')
                elif isCenter:
                    center_of_atoms=(np.max(prange)+np.min(prange))/2
                    scale=0.5-center_of_atoms
                if scale != None:
                    for atom in structure.atoms:
                        atom.position[i] += scale
        
        structure.lattice=lattice
        structure.volume=structure.calculate_volume()
        structure.volume_per_atom=structure.volume/structure.natoms
        
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            structure.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            structure.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
        self.structure=structure
        
        return self
                    
    def magnetism_order(self, element_magmoms, isPersist=False):
        """
        At present, only consider FM configuration. Other magnetic configuration need to set the atomic magnetism by hand.
        
        Arguments
            element_magmoms: dictionary of element's symbol and its magnetic moment. The valid formation:
                {'Fe':5,
                 'Cr':3,
                ...}
            isPersist (default=False): whether to save to the database.
            
        Returns:
            structureFactory's object.
            
        目前，只考虑铁磁构型。其他磁构型需要手动设置。
        
        参数：
            element_magmoms:包含元素符号和磁矩的python字典。其合法的格式：
                {'Fe':5,
                 'Cr':3,
                ...}
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
        
        返回：
            结构操作对象。
        """
        structure=self.structure
        for element in structure.elements:
            for atom in element.atoms:
                if element.symbol in element_magmoms:
                    atom.magmom=element_magmoms[element.symbol]
                else:
                    atom.magmom=0.0
        if isPersist:
            structure._persist()
        self.structure=structure
        return  self
    
    def constraint(self, index_or_atoms, isPersist=False, **kwargs):
        """
        selected dynamics. assign the constraint information to given atoms. Meanwhile, the constraint of remainder atoms 
            are set to the default [False, False, False] if don't give the value of 'constraint_of_remainder'.
        
        Arguments:
            index_or_atoms: collection of atom contain constraint information. The valid formation:
                [[1, True, True, False],
                ['Na', 0.1, 0.0, 0.0, True, True, False],
                ['Na', 0.1, 0.0, 0.0, 'Direct, True, True, False],
                ['Na', 5.234, 0.0, 0.0, 'Cartesian', True, True, False],
                [atom1, True, True, True]]
            isPersist (default=False): whether to save to the database.
                
            kwarges:
                constraint_of_remainder (default=[False, False, False]): constraint of remainder atoms.
            
        Returns:
            structureFactory's object.
            
        用于VASP的选择动力学，指定给定原子的束缚信息。同时，对于没有给出原子束缚信息的原子：
            1）没有指定束缚条件的情况下，按照默认值设置（[False, False, False]）。
            2）给出剩余原子束缚条件时，剩余原子的束缚信息全部设置为指定的值。
            
        参数：
            index_or_atom:其值可以是原子在结构的原子属性数组中的索引（index）、原子的格式化数组或原子对象。注意：原子的格式化数组的格式需要符合以下规则：
                1.程序默认晶体结构中原子坐标的类型为分数坐标。如果原子坐标为分数坐标，可以不用指定坐标类型。如，['Na', 0.1, 0.0, 0.0]。
                2.如果指定原子坐标类型，类型必须为‘Direct’或‘Cartesian’。如，['Na', 0.1, 0.0, 0.0, 'Direct']、['Na', 5.234, 0.0, 0.0, 'Cartesian']。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                constraint_of_remainder (default=[False, False, False]):剩余原子的束缚值。
                
        返回：
            结构操作对象。
        """
        import warnings
        from jump2.db.utils.check import check_constraint, check_formated_atom, compare_with_memory
        from jump2.db.materials.atom import Atom
        
        structure=self.structure
        
        atoms=[]
        constraints=[]
        for index_or_atom in index_or_atoms:
            constraint=index_or_atom[-3:]
            index_or_atom=index_or_atom[:-3]
            if len(index_or_atom) == 1:
                index_or_atom=index_or_atom[0]
            if not check_constraint(constraint):
                warnings.warn('invalid constrain in index_or_atoms')
                return False
            
            # get given atom from structure
            atom=None
            if isinstance(index_or_atom, int):
                index=index_or_atom
                if index < 0 or index > structure.natoms:
                    warnings.warn('beyond the range of atomic index')
                    return False
                atom=structure.atoms[index]
            elif check_formated_atom(index_or_atom):
                # remove atomic translation periodicity
                isNormalizingCoordinate=True
                if 'isNormalizingCoordinate' in kwargs:
                    isNormalizingCoordinate=kwargs['isNormalizingCoordinate']
                precision=1e-3
                if 'precision' in kwargs:
                    precision=kwargs['precision']
                
                formated_atom=index_or_atom    
                atom=structure.get_atom(formated_atom, isNormalizingCoordinate=isNormalizingCoordinate, precision=precision)
            elif isinstance(index_or_atom, Atom):
                atom=index_or_atom
                if not atom in structure.atoms:
                    warnings.warn("atom doesn't belong to this structure")
                    return False
            else:
                warnings.warn('unrecognized index_or_atom')
                return False
            if atom in atoms:
                warnings.warn('exist duplication in index_of_atoms')
                return False
            atoms.append(atom)
            constraints.append(constraint)
            
        for i in xrange(0, len(atoms)):    
            atoms[i].constraint=constraints[i]
        result=compare_with_memory(atoms, structure, 'atom')
        remainders=result['memory']
        constraint_of_remainder=[False, False, False]
        if 'constraint_of_remaider' in kwargs:
            constraint_of_remainder=kwargs['constraint_of_remaider']
            if not check_constraint(constraint_of_remainder):
                warnings.warn('invalid constrain in index_or_atoms')
                return False
        for atom in remainders:
            atom.constraint=constraint_of_remainder
            
        if isPersist:
            structure._persist()
        self.structure=structure
        return  self
    
    def redefine(self, operator_matrix, isPersist=False):
        """
        redefine lattcie cell: C'=C x M.
        
        Arguments:
            operator_matrix: operator matrix (M). The valid formation:
                [[0, 1, 1],
                 [1, 0, 1],
                 [1, 1, 0]]
                Note that the component of M should be integer. And the volume of M is an integer greater than 0.
            isPersist (default=False): whether to save to the database. 
                   
        Returns:
            structureFactory's object.
            
        根据给定的操作矩阵，重定义晶胞基矢。（将要添加更加详细的说明...）
        
        参数：
            operator_matrix:操作矩阵（M）。合法的格式为：
                [[0, 1, 1],
                 [1, 0, 1],
                 [1, 1, 0]]
                 注意：矩阵中的每个元素的值都必须为整数。并且，矩阵的体积必须大于0.
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
        返回：
            结构操作对象。
        """
        from jump2.db.utils.convert import any2cartesian, any2direct
        
        structure=self.structure
        
        operator_matrix=np.array(operator_matrix)
        # check
        if operator_matrix.shape != (3,3):
            raise StructureFactoryError('invalid operator_matrix')
        for i in xrange(0, operator_matrix.shape[0]):
            for j in xrange(0, operator_matrix.shape[1]):
                if not isinstance(operator_matrix[i][j], int):
                    raise StructureFactoryError('contain non-integer in operator_matrix')
        if np.linalg.det(operator_matrix) < 0:
            raise StructureFactoryError('calculated volume by operator_matrix must be larger than 0')
        
        lattice=structure.lattice
        lattice_new=[]
        for i in xrange(0, 3):
            lattice_new.append(lattice[0]*operator_matrix[i][0]+lattice[1]*operator_matrix[i][1]+lattice[2]*operator_matrix[i][2])
        
        positions=[]
        numbers=[]
        
        # suerpcell
        dim=operator_matrix[0]+operator_matrix[1]+operator_matrix[2]
        for atom in structure.atoms:
            symbol=atom.element.symbol
            position=atom.position
            for i in xrange(0, dim[0]): # x
                for j in xrange(0, dim[1]): # y
                    for k in xrange(0, dim[2]): # z
                        x=position[0]+i
                        y=position[1]+j
                        z=position[2]+k
                        p=any2cartesian(lattice, [x, y, z]).tolist()
                        p.append('Cartesian')
                        p=any2direct(lattice_new, p)
                        if not(False in [False if v < 0 or v > 1 else True for v in p]):
                            positions.append(p)
                            numbers.append(atom.element.z)
        positions=np.array(positions)
        numbers=np.array(numbers)
        cell={'lattice':lattice_new, 'positions':positions, 'numbers':numbers}
        structure.update_by_cell(cell, isPersist=isPersist)
        self.structure=structure
        return self
        
    def refine(self, symprec=1e-5, angle_tolerance=-1.0, isPersist=False):
        """
        redefine structure which may change the cell's shape. 
        
        Arguments:
            symprec (default=1e-5, symmetry tolerance): distance tolerance in Cartesian coordinates to find crystal symmetry.
            angle_tolerance (default=-1.0): An experimental argument that controls angle tolerance between basis vectors.
                Normally it is not recommended to use this argument.
            isPersist (default=False): whether to save to the database.
        
        Returns:
            structureFactory's object.
            
        通过找对称性，重新定义晶胞。注意：可能会改变晶胞形状。
        
        参数：
            symprec (default=1e-5):找结构对称性时，采用的精度。
            angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差值。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
        返回：
            结构操作对象。
        """
        import spglib
        
        structure=self.structure
        cell=structure.formatting('cell')
        cell=(cell['lattice'], cell['positions'], cell['numbers'])
        cell_new=spglib.refine_cell(cell, symprec=symprec, angle_tolerance=angle_tolerance)
        if cell_new is None:
            raise StructureFactoryError('The search is filed')
        cell_new={'lattice':cell_new[0], 'positions':cell_new[1], 'numbers':cell_new[2]}
        structure.update_by_cell(cell_new, isPersist=isPersist)
        self.structure=structure
        return self
    
    def primitive(self, symprec=1e-5, isPersist=False):
        """
        primitive structure.
        
        Arguments:
            symprec (default=1e-5, symmetry tolerance): distance tolerance in Cartesian coordinates to find crystal symmetry.
            isPersist (default=False): whether to save to the database.
        
        Returns:
            structureFactory's object.
            
        结构的原胞。
        
        参数：
            symprec (default=1e-5):找结构对称性时，采用的精度。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
        返回：
            结构操作对象。
        """
        import spglib
        
        structure=self.structure
        cell=self.structure.formatting('cell')
        cell=(cell['lattice'], cell['positions'], cell['numbers'])
        cell_new=spglib.find_primitive(cell, symprec=symprec)
        if cell_new is None:
            raise StructureFactoryError('The search is filed')
        cell_new={'lattice':cell_new[0], 'positions':cell_new[1], 'numbers':cell_new[2]}
        structure.update_by_cell(cell_new, isPersist=isPersist)
        self.structure=structure
        return self
    
    def conventional(self, symprec=1e-5, isPersist=False):
        """
        conventional structure.
        
        Arguments:
            symprec (default=1e-5, symmetry tolerance): distance tolerance in Cartesian coordinates to find crystal symmetry.buj
            isPersist (default=False): whether to save to the database.
        
        Returns:
            structureFactory's object.
            
        结构的单胞。
        
        参数：
            symprec (default=1e-5):找结构对称性时，采用的精度。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
        返回：
            结构操作对象。
        """
        import spglib
        
        structure=self.structure
        cell=self.structure.formatting('cell')
        print cell
        cell = (cell['lattice'], cell['positions'], cell['numbers'])
        cell_new=spglib.standardize_cell(cell, symprec=symprec)
        if cell_new is None:
            raise StructureFactoryError('The search is filed')
        cell_new={'lattice':cell_new[0], 'positions':cell_new[1], 'numbers':cell_new[2]}
        structure.update_by_cell(cell_new, isPersist=isPersist)
        self.structure=structure
        return self
    
    def supercell(self, dim, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        supercell structure.
        
        Arguments:
            dim: size of supercell. i.e. [2, 2, 2] (integral)
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup). 
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        
        Returns:
            structureFactory's object.
            
        超胞结构。
        
        参数：
            dim:超胞的大小。注意：数组中的每个值都必须为整数。如，[2, 2, 2]。
            isUpdatedInfo (default=False):是否更新结构的其他关联数据信息（如，化学式、不等价位置，等）。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                symprec (default=1e-5):找结构对称性时，采用的精度。
                angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差值。
                
        返回：
            结构操作对象。
        """
        structure=self.structure
        
        # check
        if len(dim) != 3:
            raise ValueError('invalid dim')
        if False in [isinstance(s0, int) and s0 >= 1 for s0 in dim]:
            raise ValueError('invalid value in dim')
        
        # lattice
        for i in xrange(0, len(dim)):
            structure.lattice[i] *= dim[i]
            
        # primitive cell
        atoms=list(structure.atoms)
        for atom in atoms:
            symbol=atom.element.symbol
            position=atom.position
            for i in xrange(0,3):
                position[i] /= dim[i]
            atom.position=position
            
        # other cell
        atoms=list(structure.atoms)
        for atom in atoms:
            symbol=atom.element.symbol
            position=atom.position
            for i in xrange(0, dim[0]): # x
                for j in xrange(0, dim[1]): # y
                    for k in xrange(0, dim[2]): # z
                        #if i != 0 and j !=0 and k != 0:
                        x=(position[0]*dim[0]+i)/dim[0]
                        y=(position[1]*dim[1]+j)/dim[1]
                        z=(position[2]*dim[2]+k)/dim[2]
                        formated_atom=[symbol, x, y, z]
                        if not(i == 0 and j == 0 and k == 0):
                            structure.add_atom(formated_atom, isUpdatedInfo=False, isPersist=False)
            #structure.del_atom(atom, isUpdatedInfo=False, isPersist=False)
        structure.volume=structure.calculate_volume()
        structure.volume_per_atom=structure.volume/structure.natoms
        
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            structure.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            structure.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
        self.structure=structure
        
        return self
    
    def joint(self, structure, direction, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        joint two structures along given direction.
        
        Arguments:
            structure: structure needed to joint.
            direction: direction vector to add the vacuum along lattice vector(a/b/c). The valid format is :
                [1, 0, 0, 'Direct']
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup).
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        
        Returns:
            structureFactory's object.    
        """
        pass
    
    def cut(self, lattce_surface, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        cut along a lattice surface.
        """
        pass
    
    def mirror(self, index_oratoms, mirror_plane, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        mirror given atoms along
        """
    
    def alloy(self):
        """
        """
        pass
    
    def surface(self):
        """
        """
        pass
    
    def adsorption(self):
        """
        """
        pass
    
    def rotation(self, index_or_atoms, axis, theta, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        rotation given atoms.
        
        arguments:
            axis: rotation axis. Note that, for molecule, the type of axis is only 'Cartesian'. The valid format:
                [0.1, 0.0, 0.0, 'Direct']
                [0.1, 0.0, 0.0]
                [5.234, 0.0, 0.0, 'Cartesian']
            theta: rotation angle. The valid format:
                [30, 'Degree']
                [0.2, 'Radian']
            index_or_atoms: collection of atom's index, formated atom or object. i.e. [atom0, atom1, atom2,...] 
                    ['Na', 0.1, 0.0, 0.0, 'Direct']
                    ['Na', 0.1, 0.0, 0.0]
                    ['Na', 5.234, 0.0, 0.0, 'Cartesian']
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup).
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
                origin: rotation origin. The valid format:
                    [0.1, 0.0, 0.0, 'Direct']
                    [0.1, 0.0, 0.0]
                    [5.234, 0.0, 0.0, 'Cartesian']
        Returns:
            structureFactory's object.
        """
        from jump2.db.utils.check import check_formated_position, check_formated_position_only_cartesian, check_formated_angle, check_formated_atom
        from jump2.db.utils.convert import any2direct, normalize_position, rotation
        from jump2.db.materials.atom import Atom
        from jump2.db.materials.structure import Structure
        from jump2.db.materials.molStructure import MolStructure
        
        structure=self.structure
        
        # check
        # axis
        if not check_formated_position(axis):
            raise ValueError('unrecognized axis')
        if isinstance(structure, Structure):
            axis=any2direct(structure.lattice, axis)
        elif isinstance(structure, MolStructure):
            if not check_formated_position_only_cartesian(axis):
                raise ValueError('unrecognized axis')
            
        # theta
        if not check_formated_angle(theta):
            raise ValueError('unrecognized theta')
        
        # origin
        origin=None
        if 'origin' in kwargs:
            origin=kwargs['origin']
        
        for atom in index_or_atoms:
            formated_atom=None
            if isinstance(atom, int):
                index=atom
                if index < 0 or index > structure.natoms:
                    raise ValueError('beyond the range of atomic index')
                else:
                    formated_atom=structure.atoms[index].to_formated()
            elif isinstance(atom, Atom):
                formated_atom=atom.to_formated()
            elif check_formated_atom(atom):
                formated_atom=atom
            else:
                raise ValueError('unrecognized atom')
            atom0=structure.get_atom(formated_atom)
            if origin is None:
                atom0.position=normalize_position(rotation(atom0.position, axis, theta), dtype='d')[:-1]
            else:
                atom0.position=normalize_position(rotation(atom0.position, axis, theta, origin=origin), dtype='d')[:-1]
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            structure.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            structure.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
        self.structure=structure
        
        return self
    
    def translation(self, index_or_atoms, direction, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        translation given atoms.
        
        arguments:
            direction: direction vector to add the vacuum along lattice vector(a/b/c). The valid format is :
                [0.1, 0, 0, 'Direct']
                [0.1, 0, 0] (for Direct, can not be specify)
                [5.234, 0, 0, 'Cartesian'] (for Cartesian, must be given)
            index_or_atoms: collection of atom's index, formated atom or object. i.e. [atom0, atom1, atom2,...] 
                    ['Na', 0.1, 0.0, 0.0, 'Direct']
                    ['Na', 0.1, 0.0, 0.0]
                    ['Na', 5.234, 0.0, 0.0, 'Cartesian']
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup).
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        
        Returns:
            structureFactory's object.
        """
        from jump2.db.utils.check import check_formated_position, check_formated_atom
        from jump2.db.utils.convert import any2direct, normalize_position, translation
        from jump2.db.materials.atom import Atom
        
        structure=self.structure
        
        # check
        if not check_formated_position(direction):
            raise StructureFactoryError('invalid direction')
        direction=any2direct(structure.lattice, direction)
        
        for atom in index_or_atoms:
            formated_atom=None
            if isinstance(atom, int):
                index=atom
                if index < 0 or index > structure.natoms:
                    raise ValueError('beyond the range of atomic index')
                else:
                    formated_atom=structure.atoms[index].to_formated()
            elif isinstance(atom, Atom):
                formated_atom=atom.to_formated()
            elif check_formated_atom(atom):
                formated_atom=atom
            else:
                raise ValueError('unrecognized atom')
            atom0=structure.get_atom(formated_atom)
            atom0.position=normalize_position(translation(atom0.position, direction), dtype='d')[:-1]
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            structure.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            structure.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
        self.structure=structure
        
        return self
    
    def images4NEB(self, struc2, nstruc, **kwargs):
        """
        """
        pass
    
    def defect(self):
        """
        """
        pass
    
    def interface(self):
        """
        """
        pass
    
    # for Molecular dynamics    
    def initializeVelocityDistribution(self, temperature, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        initialize the velocity distribution of atoms at given temperature. Note that unit of velocity is angstrom/fs.
        
        arguments:
            temperature: desired temperature.
            
        Returns:
            structureFactory's object.
        """
        structure=self.structure
        
        momentum=[0,0,0] # sum of velocities
        ke=0 # kinetic energy 
        
        velocities=np.random.random(3*structure.natoms)-0.5 # Angstrom/fs
        for i in xrange(0, structure.natoms):
            structure.atoms[i].velocity=velocities[i:i+3]
            momentum += structure.atoms[i].velocity
            ke += structure.atoms[i].element.mass*np.square(np.linalg.norm(structure.atoms[i].velocity))*1e7 # Kg x (m/s)^2
        momentum /= structure.natoms
        R=8.3144598 # Gas constant (J/Kmol)
        t0=ke/(R*3*(structure.natoms-1)) # calculated temperature
        scale=np.sqrt(temperature/t0)
        
        # scale to the desired temperature
        for atom in structure.atoms:
            atom.velocity=scale*(atom.velocity-momentum)
            
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            structure.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            structure.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
        self.structure=structure
        
        return self
    
    def perturb(self, cutoff=0.1, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        perturb the atomic position.
        
        arguments:
            cutoff (default=0.1): cutoff of perturbation (unit: angstrom).
        """
        from jump2.db.utils.convert import any2cartesian, cartesian2direct
        structure=self.structure
        
        perturbations=np.random.random(3*structure.natoms)*cutoff
        
        center_of_mass=np.array([0.0,0.0,0.0])
        for i in xrange(0, structure.natoms):
            position=cartesian2direct(structure.lattice, any2cartesian(structure.lattice, structure.atoms[i].position))#+perturbations[i:i+3])
            structure.atoms[i].position=position
            center_of_mass += structure.atoms[i].position
        center_of_mass /= structure.natoms
        # move center of mass to center of cell
        for atom in structure.atoms:
            atom.position -= (center_of_mass-[0.5,0.5,0.5])
        
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            structure.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            structure.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
        self.structure=structure
        
        return self        
    
    def removeUnit(self, unit, tolerance=0.1, isMoveAtoms=True, isPersistLattice=True, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        remove a unit with giving range.
        
        Arguments:
            unit: unit of operation. The valid format is [start, end, direction(0/1/2)]. i.e. [0.24980, 0.31235, 2]
            tolerance (default=0.1Angstrom): tolerance for unit to exclude the right atoms near boundary.
            isMoveAtoms (default=True): whether to move right atoms to fill the space caused by cutting unit.
            isPersistLattice (defalt=True): whether persist the lattice parameters when cutting unit.
            
            kwargs:
                isCenter (default=True): whether to centralize for all atoms in structure.
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        """
        from jump2.db.utils.convert import direct2cartesian
        structure=self.structure
        
        # vector of left unit
        ul=np.array([0.0,0.0,0.0])
        ul[unit[2]]=unit[0]
        # vector of left unit
        ur=np.array([0.0,0.0,0.0])
        ur[unit[2]]=unit[1]
        
        # delete unit
        unit_atoms=[]
        for atom in list(structure.atoms):
            d0=direct2cartesian(structure.lattice, atom.position-ul) # distance from left boundary
            d1=direct2cartesian(structure.lattice, atom.position-ur) # distance from right boundary
            if d0[unit[2]] >= -tolerance and d1[unit[2]] < -tolerance: # be careful on the left boundary
                unit_atoms.append(atom.to_formated())
        s1=StructureFactory(structure).del_atoms(unit_atoms, isUpdatedInfo=False, isPersist=False).structure
        structure=s1
        
        # move atoms
        if isMoveAtoms:
            moving_atoms=[]
            for atom in list(structure.atoms):
                d1=direct2cartesian(structure.lattice, atom.position-ur) # distance from right boundary
                if d1[unit[2]] >= -tolerance:
                    moving_atoms.append(atom.to_formated())
            direction=[0.0,0.0,0.0]
            direction[unit[2]]=-(unit[1]-unit[0])
            s2=StructureFactory(structure).translation(moving_atoms, direction, isUpdatedInfo=False, isPersist=False).structure
            structure=s2
        
        # shrink lattice along given direction
        if not(isPersistLattice):
            s3=StructureFactory(structure).vacuum(direction=direction, isCenter=False, isUpdatedInfo=False, isPersist=False).structure
            structure=s3
            
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            structure.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            structure.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
        self.structure=structure
        
        return self

    def addUnit(self, unit, nrepeat, tolerance=0.1, isPersistLattice=True, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        add repeat unit with giving range along a direction.
        
        Arguments:
            unit: unit of operation. The valid format is [start, end, direction(0/1/2)]. i.e. [0.24980, 0.31235, 2]
            nrepeat: number of repeat.
            tolerance (default=0.1Angstrom): tolerance for unit to exclude the right atoms near boundary.
            isPersistLattice (defalt=True): whether persist the lattice parameters when cutting unit.
            
            kwargs:
                isCenter (default=True): whether to centralize for all atoms in structure.
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        """
        from copy import deepcopy
        from jump2.db.utils.convert import direct2cartesian
        structure=self.structure
        
        # add vacuum with a length of nrepeat
        direction=[0.0,0.0,0.0]
        direction[unit[2]]=nrepeat*(unit[1]-unit[0])
        
        # prolong lattice along given direction
        if isPersistLattice:
            print 'Warning: Please check whether to have enough free space along adding direction'
            # need code
        else:
            s0=StructureFactory(structure).vacuum(direction=direction, isCenter=False, isUpdatedInfo=False, isPersist=False).structure
            structure=s0
            unit[0] /= (direction[unit[2]]+1.0)
            unit[1] /= (direction[unit[2]]+1.0)
            direction[unit[2]] /= (direction[unit[2]]+1.0)
            
        # vector of left unit
        ul=np.array([0.0,0.0,0.0])
        ul[unit[2]]=unit[0]
        # vector of left unit
        ur=np.array([0.0,0.0,0.0])
        ur[unit[2]]=unit[1]
        
        # move atoms
        moving_atoms=[]
        for atom in list(structure.atoms):
            d1=direct2cartesian(structure.lattice, atom.position-ur)
            if d1[unit[2]] >= -tolerance:
                moving_atoms.append(atom.to_formated())
        s1=StructureFactory(structure).translation(moving_atoms, direction, isUpdatedInfo=False, isPersist=False).structure
        structure=s1
        
        # add unit
        unit_atoms=[]
        for atom in list(structure.atoms):
            d0=direct2cartesian(structure.lattice, atom.position-ul) # distance from left boundary
            d1=direct2cartesian(structure.lattice, atom.position-ur) # distance from right boundary
 
            if d0[unit[2]] >= -tolerance and d1[unit[2]] < -tolerance: # be careful on the left boundary
                unit_atoms.append(atom.to_formated())

        add_atoms=[]        
        for i in xrange(1, nrepeat+1):
            for atom in unit_atoms:
                tmp=deepcopy(atom)
                tmp[unit[2]+1] += i*(unit[1]-unit[0])
                add_atoms.append(tmp)
        s2=StructureFactory(s1).add_atoms(add_atoms, isUpdatedInfo=False, isPersist=False).structure
        structure=s2

        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            structure.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            structure.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
        self.structure=structure
        
        return self
        