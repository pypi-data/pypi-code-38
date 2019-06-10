#coding=utf-8
'''
Created on Oct 21, 2017

@author: Yuhao Fu
'''
from __future__ import unicode_literals
from django.db import models


class Element(models.Model):
    """
    element.
    
    Relationships:
        element
            |- structure
            |- composition
            |- species
            |- atom
            
    Attributes:
        element
            |- symbol: element's symbol. i.e. H
            |- z: atomic number.
            |- name: element's name. i.e. Hydrogen
            |- group: element's group in period table.
            |- period: element's period in period table.
            |- mass: atomic mass.
            |- electronegativity: electronegativity of element.
            # ---------- database ----------
            |- structure_set: collection of structures contained the element.
            |- composition_set: collection of compositions contained the element.
            |- species_set: collection of species contained the element.
            |- atom_set: collection of atoms contained the element.
            # ---------- build-in ----------
            |- structures: collection of structures contained the element.
            |- compositions: collection of compositions contained the element.
            |- species: collection of species contained the element.
            |- atoms: collection of atoms contained the element.
    
    元素类。
    
    关系：
        element
            |- structure
            |- composition
            |- species
            |- atom
            
    属性:
        element
            |- symbol:元素符号。如，H。
            |- z:原子序数。
            |- name:元素名称。如，Hydrogen。
            |- group:周期表中元素所属的族。
            |- period:周期表中元素所属的周期。
            |- mass:原子质量。
            |- electronegativity:元素的电负性。
            # ---------- database ----------
            |- structure_set:包含该元素的结构对象集合。
            |- composition_set:包含该元素的化学式对象集合。
            |- species_set:包含该元素的元素种类对象集合。
            |- atom_set:包含该元素的原子对象集合。
            # ---------- build-in ----------
            |- structures:包含该元素的结构对象集合。
            |- compositions:包含该元素的化学式对象集合。
            |- species:包含该元素的元素种类对象集合。
            |- atoms:包含该元素的原子对象集合。
    """
    symbol=models.CharField(primary_key=True, max_length=4)
    z=models.IntegerField()
    name=models.CharField(max_length=20)
    
    group=models.IntegerField()
    period=models.IntegerField()
    
    mass=models.FloatField(null=True)
    electronegativity=models.FloatField(null=True)
    
    
    class Meta:
        app_label='materials'
        db_table='element'
        default_related_name='element_set'
        ordering=('z',)
    
    #_isAssociatedDatabase=None
    #@property
    #def isAssociatedDatabase(self):
    #    """
    #    whether to associate with the database for the build-in relationships (default=False).
    #    """
    #    if self._isAssociatedDatabase is None:
    #        self._isAssociatedDatabase=False
    #    return self._isAssociatedDatabase
    #@isAssociatedDatabase.setter
    #def isAssociatedDatabase(self, value):
    #    """
    #    Arguments:
    #        value: boolean type (True/False).
    #    """
    #    if not isinstance(value, bool):
    #        raise ValueError('must be boolean type (True or False)')
    #    self._isAssociatedDatabase=value
            
            
    def __str__(self):
        return self.symbol
    
    _structures=None
    @property
    def structures(self):
        """
        structures contained the element.
        
        包含该元素的结构。
        """
        #from cache.cachedElementProvider import CachedElementProvider
        
        if self._structures is None:
            #if not CachedElementProvider().get(self.symbol):
            #    self._structures=[]
            #else:
            #    self._structures=list(self.structure_set.all())
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
        self._structures=structures
        return True
    def add_structure(self, structure):
        """
        add a structure to this element.
        
        Arguments:
            structure: structure's object.
            
        Returns:
            True if add a structure successfully. Conversely, False.
            
        添加一个结构到元素中。
        
        参数：
            structure:结构对象。
        
        返回：
            布尔值（True/False）。
        """    
        from jump2.db.utils.check import exist
        
        if not exist(structure, self.structures, 'structure'):
            self.structures.append(structure)
            structure.elements.append(self)
            return True
        else:
            return False
        
    _compositions=None
    @property
    def compositions(self):
        """
        compositions contained the element.
        
        包含该元素的化学式。
        """
        #from cache.cachedElementProvider import CachedElementProvider
        
        if self._compositions is None:
            #if not CachedElementProvider().get(self.symbol):
            #    self._compositions=[]
            #else:
            #    self._compositions=list(self.composition_set.all())
            self._compositions=[]
        return self._compositions
    @compositions.setter
    def compositions(self, compositions):
        """
        assign the value. Note that it will cover the previous value.
        
        Arguments:
            compositions: collection of composition's object.
            
        Returns:
            True if the assignment is successful. Conversely, False.
            
        ‘compositions’属性的set方法。注意：该方法将会清除以前的数据。
        
        参数：
            compositions:化学式对象集合。
            
        返回：
            布尔值（True/False）。
        """
        import warnings
        from jump2.db.materials.composition import Composition
        
        for composition in compositions:
            if not isinstance(composition, Composition):
                warnings.warn('invalid type')
                return False
        self._compositions=compositions
        return True
    def add_composition(self, composition):
        """
        add a composition to this element.
        
        Arguments:
            composition: composition's object or formula.
            
        Returns:
            True if add a composition successfully. Conversely, False.
            
        添加一个化学式到元素中。
        
        参数：
            composition:化学式对象或化学式字符串。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        from jump2.db.cache.cachedCompositionProvider import CachedCompositionProvider
        
        if not exist(composition, self.compositions, 'composition'):
            if isinstance(composition, basestring): # formula
                formula=composition
                composition=CachedCompositionProvider().get(formula)
                if composition is None:
                    composition=CachedCompositionProvider().set(formula)
            self.compositions.append(composition)
            composition.elements.append(self)
            return True
        else:
            return False
    
    _species=None
    @property
    def species(self):
        """
        species contained the element.
        
        属于该元素的元素种类。
        """
        #from cache.cachedElementProvider import CachedElementProvider
        
        if self._species is None:
            #if not CachedElementProvider().get(self.symbol):
            #    self._species=[]
            #else:
            #    self._species=list(self.species_set.all())
            self._species=[]
        return self._species
    @species.setter
    def species(self, species):
        """
        assign the value. Note that it will cover the previous value.
        
        Arguments:
            species: collection of species's object.
            
        Returns:
            True if the assignment is successful. Conversely, False.
            
        ‘species’属性的set方法。注意：该方法将会清除以前的数据。
        
        参数：
            species:元素种类对象集合。
            
        返回：
            布尔值（True/False）。
        """
        import warnings
        from jump2.db.materials.species import Species
        
        for species0 in species:
            if not isinstance(species0, Species):
                warnings.warn('invalid type')
                return False
        self._species=species
        return True
    def add_species(self, species):
        """
        add a species to this element.
        
        Arguments:
            species: species's object or name.
        
        Returns:
            True if add a species successfully. Conversely, False.
            
        添加一个元素种类到这个元素中。
        
        参数：
            species:元素种类对象或元素名称。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        from jump2.db.cache.cachedSpeciesProvider import CachedSpeciesProvider
        
        if not exist(species, self.species, 'species'):
            if isinstance(species, basestring): # name
                name=species
                species=CachedSpeciesProvider().get(name)
            self.species.append(species)
            species.element=self
            return True
        else:
            return False
    def get_species(self, name):
        """
        get the species's object with the given name.
        
        Arguments:
            name: species's name.
        
        Returns:
            species's object if it exists. Conversely, return the None.
            
        从元素中获得给定名称的元素种类对象。
        
        参数：
            name:元素种类的名称。如，Fe2+。
            
        返回：
            如果元素中存在该元素种类，返回元素种类对象。否则，返回 None。
        """
        for species in self.species:
            if species.name == name:
                return species
        return None
    def del_species(self, index_or_species, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        delete a species from this element. Note that it will delete this specise's object from other related classes's objects.
        
        Arguments:
            index_or_species: species's index, name or object.
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup). 
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        
        从元素中删除一个元素种类。注意：当删除元素种类时，基于程序效率上的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
        程序默认不会更新结构（更新化学式，删除与该元素种类关联的所有原子对象，更新不等价位置、空间群和WyckoffSite，等）
        
        参数：
            index_or_species:其值可以是元素种类在结构的元素种类属性数组中的索引（index）、元素种类的名称或元素种类对象。
            isUpdatedInfo (default=False): 是否更新结构的其他关联数据信息（化学式、不等价位置，等）。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                symprec (default=1e-5):找结构对称性时，采用的精度。
                angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差值。
        
        返回：
            布尔值（True/False）。
        """
        import warnings
        from jump2.db.materials.species import Species
        
        species=None
        if isinstance(index_or_species, int):
            index=index_or_species
            if index < 0 or index > len(self.species):
                warnings.warn("beyond the range of species' array")
                return False
            species=self.species[index]
        elif isinstance(index_or_species, basestring):
            name=index_or_species
            species=self.get_species(name)
            if species is None:
                warnings.warn("don't have %s in the structure" %name)
                return False
        elif isinstance(index_or_species, Species):
            species=index_or_species
            if not species in self.species:
                warnings.warn("don't have this instance of species in the structure")
                return False
        else:
            warnings.warn('unrecognized index_or_species')
            return False
        
        # delete all atoms of this species
        if len(self.structures) != 1:
            warnings.warn("exist more than one structure in element.structures array, don't know which structure the element belong to")
            return None
        structure=self.structures[0]
        for atom in list(species.atoms):
            self.del_atom(atom, isUpdatedInfo=False, isPersist=False)
        
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
              
    _atoms=None
    @property
    def atoms(self):
        """
        atoms contained the element.
        
        属于该元素的原子。
        """
        #import warnings
        #from cache.cachedElementProvider import CachedElementProvider
        
        #if self.isAssociatedDatabase and CachedElementProvider().get(self.symbol):
        #    if not self._atoms and len(self._atoms) > 0:
        #        warnings.warn('atoms is changing')
        #    self._atoms=list(self.atom_set.all())  
        #elif self._atoms is None:
        #    self._atoms=[]
        if self._atoms is None:
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
        self._atoms=atoms
        return True
    def add_atom(self, atom):
        """
        add a atom to this element.
        
        Arguments:
            atom: atom's object.
            
        Returns:
            True if add a atom successfully. Conversely, False.
            
        添加一个原子到元素中。
        
        参数：
            atom:原子对象。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(atom, self.atoms, 'atom'):
            self.atoms.append(atom)
            atom.element=self
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
            
        从元素中获取给定的原子对象。
         
        参数：
            formated_atom:原子的格式化数组。注意：原子的格式化数组的格式需要符合以下规则：
                1.程序默认晶体结构中原子坐标的类型为分数坐标。如果原子坐标为分数坐标，可以不用指定坐标类型。如，['Na', 0.1, 0.0, 0.0]。
                2.如果指定原子坐标类型，类型必须为‘Direct’或‘Cartesian’。如，['Na', 0.1, 0.0, 0.0, 'Direct']、['Na', 5.234, 0.0, 0.0, 'Cartesian']。
            
            kwargs:
                isNormalizingCoordinate (default=True):当给定原子的类型为格式化数组时，默认移除原子坐标上的平移周期性，以保证其值在0.0～1.0之间。
                precision (default=1e-3):比较原子是否重叠的精度。当“atom”参数为格式化数组时，此参数用于判断给定的原子是否在结构中（比较给定原子坐标与结构中的原子坐标之间的距离）。
                
        返回：
            如果元素中存在该原子，返回原子对象。否则，返回 None。
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
        delete a atom from this element. Note that it will delete this atom's object from other related classes's objects.
        
        Arguments:
            index_or_atom: atom's index, formated atom and object.
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup). 
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                isNormalizingCoordinate (default=True): whether to remove the periodic boundary condition, 
                    ensure the value of atomic coordinate is between 0 and 1 (i.e. 1.3 -> 0.3).
                precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                        to determine whether this atom is in collection by comparing its distance from other atoms.
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
            
        Returns:
            True if delete a atom successfully. Conversely, False.
            
        从元素中删除一个原子。注意：当删除原子时，基于程序效率上的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
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
            
    def create(self, symbol, isPersist, **kwargs):
        """
        create a element object.
        
        Arguments:
            symbol: element's symbol. i.e. 'Na'
            isPersit: if True, save to database. Conversely, only run in memory.
            
            kwargs:
                structures: collection of structure's object.
                compositions: collection of composition's object or formula. i.e. ['FeSb3', 'CoSb3',...]
                species: collection of species's name.
                atoms: collection of atom's object.
                
        Returns:
            element's object.
                
        创建一个元素对象。
        
        参数：
            symbol:元素符号。如，Na。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                structures:结构对象集合。
                compositions:化学式对象集合。
                species:元素种类对象集合。
                atoms:原子对象集合。
                
        返回：
            元素对象。
        """   
        from jump2.db.utils.initialization.init_elements import elements
        from jump2.db.cache.cachedCompositionProvider import CachedCompositionProvider
        from jump2.db.cache.cachedSpeciesProvider import CachedSpeciesProvider
        from jump2.db.materials.structure import Structure
        from jump2.db.materials.composition import Composition
        from jump2.db.materials.species import Species
        from jump2.db.materials.atom import Atom
        
        
            
        value=elements.get(symbol)
        if value == None:
            raise ValueError("unrecognized element's symbol")
    
        self.symbol=symbol
        
        if isPersist:
            self.save()
            
        self.z=value[0]
        self.name=value[1]
        self.period=value[2]
        self.group=value[3]
        mass=value[4]
        electronegativity=value[6]
        
        if mass != '*':
            self.mass=mass                         
        if electronegativity != '*':
            self.electronegativity=electronegativity
            
        if 'structures' in kwargs:
            structures=kwargs['structures']
            for structure in structures:
                if not isinstance(structure, Structure):
                    raise ValueError('unrecognized structure in structures')
                self.add_structure(structure)
                if isPersist:
                    self.structure_set.add(structure)
        if 'compositions' in kwargs:
            compositions=kwargs['compositions']
            for composition in compositions:
                if isinstance(composition, basestring):
                    formula_of_composition=composition
                    composition=CachedCompositionProvider().get(formula_of_composition)
                elif not isinstance(composition, Composition):
                    raise ValueError('unrecognized composition in compositions')
                self.add_composition(composition)
                if isPersist:
                    self.composition_set.add(composition)
        if 'species' in kwargs:
            raw_species=kwargs['species']
            for species in raw_species:
                if isinstance(species, basestring):
                    name_of_species=species
                    species=CachedSpeciesProvider().get(name_of_species)
                elif not isinstance(species, Species):
                    raise ValueError('unrecognized species in species')
                self.add_species(species)
                if isPersist:
                    self.species_set.add(species)
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
    
    
    
    
    