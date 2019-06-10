#coding=utf-8
'''
Created on Oct 21, 2017

@author: Yuhao Fu
'''
from __future__ import unicode_literals
from django.db import models

class Species(models.Model):
    """
    species.
    
    Relationships:
        species
            |- structure
            |- element
            |- atom
            
    Attributes:
        species
            |- element
            |- name
            |- ox
            # ---------- database ----------
            |- structure_set
            |- atom_set
            # ---------- build-in ----------
            |- structures
            |- atoms
            
    元素种类。
    
    关系:
        species
            |- structure
            |- element
            |- atom
            
    属性:
        species
            |- element
            |- name
            |- ox
            # ---------- database ----------
            |- structure_set
            |- atom_set
            # ---------- build-in ----------
            |- structures
            |- atoms
    """
    # relationship 
    element=models.ForeignKey('Element', blank=True, null=True)
    name=models.CharField(max_length=8, primary_key=True) # i.e. Na+
    ox=models.IntegerField(blank=True, null=True) # oxidation state
    
    class Meta:
        app_label='materials'
        db_table='species'
        default_related_name='species_set'
    
    def __str__(self):
        return self.name
    
    _structures=None
    @property
    def structures(self):
        """
        structures contained the species.
        
        包含该元素种类的结构。
        """
        #from cache.cachedSpeciesProvider import CachedSpeciesProvider
        
        if self._structures is None:
        #    if not CachedSpeciesProvider().get(self.name):
        #        self._structures=[]
        #    else:
        #        self._structures=list(self.structure_set.all())
            self._structures=[]
        return self._structures
    @structures.setter
    def structures(self, structures):
        """
        assign the value. Note that it will cover the previous value.
        
        Arguments:
            structures: collection of strucutre's object.
            
        Returns:
            True if the assignment is successful. Conversely, False.
            
        ‘structures’属性的set方法。注意：该方法将会清除以前的数据。
        
        参数：
            structures:结构对象集合。
            
        返回：
            布尔值（True/False）。
        """
        import warnings
        from jump2.db.materials.structure import Structure
        
        for structure in structures:
            if not isinstance(structure, Structure):
                warnings.warn('invalid type')
                return False
        self._structures=[]
        return True
    def add_structure(self, structure):
        """
        add a structure to this species.
        
        Arguments:
            structure: structure's object.
            
        Returns:
            True if add a structure successfully. Conversely, False.
            
        添加一个结构到元素种类中。
        
        参数：
            structure:结构对象。
        
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(structure, self.structures, 'structure'):
            self.structures.append(structure)
            structure.species.append(self)
            return True
        else:
            return False

    _atoms=None
    @property
    def atoms(self):
        """
        atoms contained the species.
        
        属于该元素种类的原子。
        """
        #from cache.cachedSpeciesProvider import CachedSpeciesProvider
        
        if self._atoms is None:
        #    if not CachedSpeciesProvider().get(self.name):
        #        self._atoms=[]
        #    else:
        #        self._atoms=list(self.atom_set.all())
            self._atoms=[]
        return self._atoms
    @atoms.setter
    def atoms(self, atoms):
        """
        assign the value. Note that it will cover the previous value.
        
        Arguments:
            atoms: collection of atom's object.
            
        Returns:
            True if the assignment is successful. Conversely, False.
            
        ‘atoms’属性的set方法。注意：该方法将会清除以前的数据。
        
        参数：
             atoms:原子对象集合。
             
        返回：
            布尔值（True/False）。
        """
        import warnings
        from jump2.db.materials.atom import Atom
        
        for atom in atoms:
            if not isinstance(atom, Atom):
                warnings.warn('invalid type')
                return False
        self._atoms=[]
        return True
    def add_atom(self, atom):
        """
        add a atom to this species.
        
        Arguments:
            atom: atom's object.
        
        Returns:
            True if add a atom successfully. Conversely, False.
            
        添加一个原子到元素种类中。
        
        参数：
            atom:原子对象。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(atom, self.atoms, 'atom'):
            self.atoms.append(atom)
            atom.species=self
            return True
        else:
            return False
    def get_atom(self, formated_atom, **kwargs):
        """
        get a atom by formated atomic list.
        
        Arguments:
            formated_atom: formated atom. Note that type of coordinate is 'Direct',  you can not specify
                the type. The valid formation:
                    ['Na', 0.1, 0.0, 0.0, 'Direct']
                    ['Na', 0.1, 0.0, 0.0]
                    ['Na', 5.234, 0.0, 0.0, 'Cartesian']
                
            kwargs:
                isNormalizingCoordinate (default=True): whether to remove the periodic boundary condition, 
                    ensure the value of atomic coordinate is between 0 and 1 (i.e. 1.3 -> 0.3).
                precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                        to determine whether this atom is in collection by comparing its distance 
                        from other atoms.
        Returns:
            atom's object if exist. Conversely, return None.
            
        从元素种类中获取给定的原子对象。
         
        参数：
            formated_atom:原子的格式化数组。注意：原子的格式化数组的格式需要符合以下规则：
                1.程序默认晶体结构中原子坐标的类型为分数坐标。如果原子坐标为分数坐标，可以不用指定坐标类型。如，['Na', 0.1, 0.0, 0.0]。
                2.如果指定原子坐标类型，类型必须为‘Direct’或‘Cartesian’。如，['Na', 0.1, 0.0, 0.0, 'Direct']、['Na', 5.234, 0.0, 0.0, 'Cartesian']。
            
            kwargs:
                isNormalizingCoordinate (default=True):当给定原子的类型为格式化数组时，默认移除原子坐标上的平移周期性，以保证其值在0.0～1.0之间。
                precision (default=1e-3):比较原子是否重叠的精度。当“atom”参数为格式化数组时，此参数用于判断给定的原子是否在结构中（比较给定原子坐标与结构中的原子坐标之间的距离）。
                
        返回：
            如果元素种类中存在该原子，返回原子对象。否则，返回 None。
        """
        import warnings
        from jump2.db.utils.check import check_formated_atom_only_direct, check_formated_atom_only_cartesian
        from jump2.db.utils.fetch import get_entity_from_collection
        
        # remove atomic translation periodicity
        isNormalizingCoordinate=True
        if 'isNormalizingCoordinate' in kwargs:
            isNormalizingCoordinate=kwargs['isNormalizingCoordinate']
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
        
        if check_formated_atom_only_direct(formated_atom):
            return get_entity_from_collection(formated_atom, self.atoms, 'atom', isNormalizingCoordinate=isNormalizingCoordinate, precision=precision)
        elif check_formated_atom_only_cartesian(formated_atom):
            if len(self.structures) != 1:
                warnings.warn("exist more than one structure in element.structures array, don't know which structure the element belong to")
                return None
            return get_entity_from_collection(formated_atom, self.atoms, 'atom', lattice=self.structures[0].lattice, isNormalizingCoordinate=isNormalizingCoordinate, precision=precision)
        else:
            return None
    def del_atom(self, index_or_atom, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        delete a atom from this species. Note that it will delete this atom's object from other related classes's objects.
        
        Arguments:
            index_or_atom: atom's index, formated atom and object.
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup). 
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                isNormalizingCoordinate (default=True): whether to remove the periodic boundary condition, 
                    ensure the value of atomic coordinate is between 0 and 1 (i.e. 1.3 -> 0.3).
                precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                        to determine whether this atom is in collection by comparing its distance 
                        from other atoms.
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
            
        Returns:
            True if delete a atom successfully. Conversely, False.
            
        从元素种类中删除一个原子。注意：当删除原子时，基于程序效率上的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
        程序默认不会更新结构（更新化学式，更新空间群和WyckoffSite，等）。
        
        参数：
            index_or_atom:其值可以是原子在结构的原子属性数组中的索引（index）、原子的格式化数组或原子对象。注意：原子的格式化数组的格式需要符合以下规则：
                1.程序默认晶体结构中原子坐标的类型为分数坐标。如果原子坐标为分数坐标，可以不用指定坐标类型。如，['Na', 0.1, 0.0, 0.0]。
                2.如果指定原子坐标类型，类型必须为‘Direct’或‘Cartesian’。如，['Na', 0.1, 0.0, 0.0, 'Direct']、['Na', 5.234, 0.0, 0.0, 'Cartesian']。
            isUpdatedInfo (default=False):是否更新结构的其他关联数据信息（如，化学式、不等价位置，等）。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                isNormalizingCoordinate (default=True):当给定原子的类型为格式化数组时，默认移除原子坐标上的平移周期性，以保证其值在0.0～1.0之间。
                precision (default=1e-3):比较原子是否重叠的精度。当“atom”参数为格式化数组时，此参数用于判断给定的原子是否在结构中（比较给定原子坐标与结构中的原子坐标之间的距离）。
                symprec (default=1e-5):找结构对称性时，采用的精度。
                angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差值。
        
        返回：
            布尔值（True/False）。
        """
        import warnings
        from jump2.db.utils.check import check_formated_atom
        from jump2.db.materials.atom import Atom
        
        atom=None
        if isinstance(index_or_atom, int):
            index=index_or_atom
            if index < 0 or index > len(self.atoms):
                warnings.warn('beyond the range of atomic index')
                return False
            atom=self.atoms[index]
        elif check_formated_atom(index_or_atom):
            # remove atomic translation periodicity
            isNormalizingCoordinate=True
            if 'isNormalizingCoordinate' in kwargs:
                isNormalizingCoordinate=kwargs['isNormalizingCoordinate']
            precision=1e-3
            if 'precision' in kwargs:
                precision=kwargs['precision']
                    
            formated_atom=index_or_atom
            atom=self.get_atom(formated_atom, isNormalizingCoordinate=isNormalizingCoordinate, precision=precision)
        elif isinstance(index_or_atom, Atom):
            atom=index_or_atom
        else:
            warnings.warn('unrecognized index_or_atom')
            return False
        
        if not atom is None:
            if len(self.structures) != 1:
                warnings.warn("exist more than one structure in element.structures array, don't know which structure the element belong to")
                return None
            structure=self.structures[0]
            structure.del_atom(atom, isUpdatedInfo=False, isPersist=False)
            
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
            
            return True
        else:
            return False
                
    def create(self, name, isPersist, **kwargs):
        """
        create species's object. Note that oxidation state (ox) of this species is extracted from the variable 'name'.
        
        Arguments:
            name: name of species. i.e. Fe2+
            isPersist: if True, save to database. Conversely, only run in memory.
            
            kwargs:
                structures: collection of structure's object.
                atoms: collection of atom's object.
                
        Returns:
            species's object.
                
        创建一个元素种类对象。注意：元素种类的氧化态（ox）提取自元素名称中的信息。
        
        参数：
            name:元素种类名称。如，Fe2+。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                structures:结构对象集合。
                atoms:原子对象集合。
                
        返回：
            元素种类对象。
        """
        import re
        import warnings
        from jump2.db.cache.cachedElementProvider import CachedElementProvider
        from jump2.db.materials.structure import Structure
        from jump2.db.materials.atom import Atom
        
        self.name=name
        if isPersist:
            self.save()
        
        raw_name=re.split('([0-9.+-]+)', name)
        if len(raw_name) == 1:
            raise ValueError('invalid name: %s' %name)
        elif raw_name[1] == '+':
            ox=1
        elif raw_name[1] == '-':
            ox=-1
        else:
            raw_ox=re.split('([+-])+', raw_name[1])[:-1]
            if not raw_ox:
                warnings.warn("ox will be set to %s in '%s'" %(raw_name[1], name))
                ox=float(raw_name[1])
            elif raw_ox[-1] == '+':
                ox=float(raw_ox[0])
            elif raw_ox[-1] == '-':
                ox=-float(raw_ox[0])
        self.ox=ox

        self.element=CachedElementProvider().get(raw_name[0])
                                     
        if 'structures' in kwargs:
            structures=kwargs['structures']
            for structure in structures:
                if not isinstance(structure, Structure):
                    raise ValueError('unrecognized structure in structures')
                self.add_structure(structure)
                if isPersist:
                    self.strucutre_set.add(structure)
        if 'atoms' in kwargs:
            atoms=kwargs['atoms']
            for atom in atoms:
                if not isinstance(atom, Atom):
                    raise ValueError('unrecognized atom in atoms')
                self.add_atom(atom)
                if isPersist:
                    self.atom_set.add(atom)
        if isPersist:
            self.save()
                
        return self
            
        