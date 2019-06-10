#coding=utf-8
'''
Created on Oct 24, 2017

@author: fu
'''
from __future__ import unicode_literals
from django.db import models

class MolElement(models.Model):
    """
    molecular element。
    
    Relationships:
        element
            |- structure
            |- composition
            |- atom
            
    Attrubitues:
        element
            |- symbol
            |- z
            |- name
            |- group
            |- period
            |- mass
            |- electronegativity
            # ---------- database ----------
            |- structure_set: collection of structures contained the element.
            |- composition_set: collection of compositions contained the element.
            |- atom_set: collection of atoms contained the element.
            # ---------- build-in ----------
            |- structures: collection of structures contained the element.
            |- compositions: collection of compositions contained the element.
            |- atoms: collection of atoms contained the element.
            
    分子的元素类。
    
    关系：
        element
            |- structure
            |- composition
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
            |- atom_set:包含该元素的原子对象集合。
            # ---------- build-in ----------
            |- structures:包含该元素的结构对象集合。
            |- compositions:包含该元素的化学式对象集合。
            |- atoms:包含该元素的原子对象集合
    """
    symbol=models.CharField(primary_key=True, max_length=4)
    z=models.IntegerField()
    name=models.CharField(max_length=20)
    
    group=models.IntegerField()
    period=models.IntegerField()
    
    mass=models.FloatField(blank=True, null=True)
    electronegativity=models.FloatField(blank=True, null=True)
    
    class Meta:
        app_label='materials'
        db_table='molElement'
        default_related_name='element_set'
            
    def __str__(self):
        return self.symbol
    
    _structures=None
    @property
    def structures(self):
        """
        structures contained the element.
        
        包含该元素的结构。
        """
        if self._structures is None:
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
        from jump2.db.materials.molStructure import MolStructure
        
        for structure in structures:
            if not isinstance(structure, MolStructure):
                warnings.warn('invalid type')
                return False
        self._structures=[]
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
        if self._compositions is None:
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
        from jump2.db.materials.molComposition import MolComposition
        
        for composition in compositions:
            if not isinstance(composition, MolComposition):
                warnings.warn('invalid type')
                return False
        self._compositions=[]
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
        from jump2.db.cache.cachedMolCompositionProvider import CachedMolCompositionProvider
        
        if not exist(composition, self.compositions, 'composition'):
            if isinstance(composition, basestring): # formula
                formula=composition
                composition=CachedMolCompositionProvider().get(formula)
                if composition is None:
                    composition=CachedMolCompositionProvider().set(formula)
            self.compositions.append(composition)
            composition.elements.append(self)
            return True
        else:
            return False    
        
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
        from jump2.db.materials.molAtom import MolAtom
        
        for atom in atoms:
            if not isinstance(atom, MolAtom):
                warnings.warn('invalid type')
                return False
        self._atoms=[]
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
            formated_atom: formated atom. Note that type of coordinate is only 'Cartesian'  you must specify the type. The valid formation: ['Na', 2.3, 1.4, 0.0, 'Cartesian']
                
            kwargs:
                precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                        to determine whether this atom is in collection by comparing its distance from other atoms.
        Returns:
            atom's object if exist. Conversely, return None.
            
        从元素中获取给定的原子对象。
         
        参数：
            formated_atom:原子的格式化数组。注意：原子的格式化数组必须指定原子坐标类型（‘Cartesian’），其合法的格式为: ['Na', 5.234, 0.0, 0.0, 'Cartesian']。
            
            kwargs:
                precision (default=1e-3):比较原子是否重叠的精度。当“atom”参数为格式化数组时，此参数用于判断给定的原子是否在结构中（比较给定原子坐标与结构中的原子坐标之间的距离）。
                
        返回：
            如果元素中存在该原子，返回原子对象。否则，返回 None。
        """
        from jump2.db.utils.check import check_formated_atom_only_cartesian
        from jump2.db.utils.fetch import get_entity_from_collection4molecule
        
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
        
        if check_formated_atom_only_cartesian(formated_atom):
            return get_entity_from_collection4molecule(formated_atom, self.atoms, 'atom')
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
                precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                    to determine whether this atom is in collection by comparing its distance from other atoms.
                        
        Returns:
            True if delete a atom successfully. Conversely, False.
            
        从元素中删除一个原子。注意：当删除原子时，基于程序效率上的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
        程序默认不会更新结构（更新化学式，更新空间群和WyckoffSite，等）。
        
        参数：
            index_or_atom:其值可以是原子在结构的原子属性数组中的索引（index）、原子的格式化数组或原子对象。注意：原子的格式化数组必须指定原子坐标类型（‘Cartesian’），其合法的格式为: ['Na', 5.234, 0.0, 0.0, 'Cartesian']。
            isUpdatedInfo (default=False):是否更新结构的其他关联数据信息（如，化学式、不等价位置，等）。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                precision (default=1e-3):比较原子是否重叠的精度。当“atom”参数为格式化数组时，此参数用于判断给定的原子是否在结构中（比较给定原子坐标与结构中的原子坐标之间的距离）。
        
        返回：
            布尔值（True/False）。
        """
        import warnings
        from jump2.db.utils.check import check_formated_atom_only_cartesian
        from jump2.db.materials.molAtom import MolAtom
        
        atom=None
        if isinstance(index_or_atom, int):
            index=index_or_atom
            if index < 0 or index > len(self.atoms):
                warnings.warn('beyond the range of atomic index')
                return False
            atom=self.atoms[index]
        elif check_formated_atom_only_cartesian(index_or_atom):
            # remove atomic translation periodicity
            isNormalizingCoordinate=True
            if 'isNormalizingCoordinate' in kwargs:
                isNormalizingCoordinate=kwargs['isNormalizingCoordinate']
            precision=1e-3
            if 'precision' in kwargs:
                precision=kwargs['precision']
                    
            formated_atom=index_or_atom
            atom=self.get_atom(formated_atom, precision=precision)
        elif isinstance(index_or_atom, MolAtom):
            atom=index_or_atom
        else:
            warnings.warn('unrecognized index_or_atom')
            return False
        
        if not atom is None:
            if len(self.structures) != 1:
                warnings.warn("exist more than one structure in element.structures array, don't know which structure the element belong to")
                return None
            structure=self.structures[0]
            structure.del_atom(atom, isUpdatedInfo=isUpdatedInfo, isPersist=isPersist)
            if isPersist:
                structure.update(isPersist=isPersist)
            elif isUpdatedInfo and not isPersist:
                structure.update(isPersist=False)   
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
                atoms: collection of atom's object.
                
        创建一个元素对象。
        
        参数：
            symbol:元素符号。如，Na。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                structures:结构对象集合。
                compositions:化学式对象集合。
                atoms:原子对象集合。
                
        返回：
            元素对象。
        """
        from jump2.db.utils.initialization.init_elements import elements
        from jump2.db.cache.cachedMolCompositionProvider import CachedMolCompositionProvider
        from jump2.db.materials.molStructure import MolStructure
        from jump2.db.materials.molComposition import MolComposition
        from jump2.db.materials.molAtom import MolAtom
        
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
                if not isinstance(structure, MolStructure):
                    raise ValueError('unrecognized structure in structures')
                self.add_structure(structure)
                if isPersist:
                    self.structure_set.add(structure)
        if 'compositions' in kwargs:
            compositions=kwargs['compositions']
            for composition in compositions:
                if isinstance(composition, basestring):
                    formula_of_composition=composition
                    composition=CachedMolCompositionProvider().get(formula_of_composition)
                elif not isinstance(composition, MolComposition):
                    raise ValueError('unrecognized composition in compositions')
                self.add_composition(composition)
                if isPersist:
                    self.composition_set.add(composition)
        if 'atoms' in kwargs:
            atoms=kwargs['atoms']
            for atom in atoms:
                if not isinstance(atom, MolAtom):
                    raise ValueError('unrecognized atom in atoms')
                self.add_atom(atom)
                if isPersist:
                    self.atom_set.add(atom)
                    
        if isPersist:
            self.save()
                    
        return self
        
           
        
        
        