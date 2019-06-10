#coding=utf-8
'''
Created on Oct 21, 2017

@author: fu
'''
from __future__ import unicode_literals
from django.db import models
from jump2.db.utils.customField import NumpyArrayField


class Site(models.Model, object):
    """
    site.
    
    Relationships:
        site
            |- structure
            |- atom
            |- wyckoffSite
    
    Attributes:
        site
            |- structure
            |- wyckoffSite
            |- position
            |- coordination_number
            
    不等价位置。
    
    关系:
        site
            |- structure
            |- atom
            |- wyckoffSite
    
    属性:
        site
            |- structure
            |- wyckoffSite
            |- position
            |- coordination_number
    """
    
    # relationship
    structure=models.ForeignKey('Structure', blank=True, null=True)
    wyckoffSite=models.ForeignKey('WyckoffSite', blank=True, null=True)
    
    position=NumpyArrayField(blank=True, null=True) # [3, 3] (float)
    
    coordination_number=models.IntegerField(blank=True, null=True)
    
    class Meta:
        app_label='materials'
        db_table='site'
        default_related_name='site_set'
       
    def __str__(self):
        if (self.atoms is None) or (self.atoms == []):
            return '(%s) [%f %f %f]' %(str(self.wyckoffSite.multiplicity)+self.wyckoffSite.symbol, 
                                                      self.position[0], 
                                                      self.position[1], 
                                                      self.position[2])
        else:
            return '%s (%s) [%f %f %f]' %(self.atoms[0].element.symbol, 
                                                      str(self.wyckoffSite.multiplicity)+self.wyckoffSite.symbol, 
                                                      self.position[0], 
                                                      self.position[1], 
                                                      self.position[2])
    
    _atoms=None
    @property
    def atoms(self):
        """
        atoms contained the site.
        
        属于该不等价位置的原子。
        """
        if self._atoms is None:
        #    if not self.id:
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
        add a atom to this site.
        
        Arguments:
            atom: atom's object.
            
        Returns:
            True if add a atom successfully. Conversely, False.
            
        添加一个原子到不等价位置中。
        
        参数：
            atom:原子对象。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(atom, self.atoms, 'atom'):
            self.atoms.append(atom)
            atom.site=self
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
            
        从不等价位置中获取给定的原子对象。
         
        参数：
            formated_atom:原子的格式化数组。注意：原子的格式化数组的格式需要符合以下规则：
                1.程序默认晶体结构中原子坐标的类型为分数坐标。如果原子坐标为分数坐标，可以不用指定坐标类型。如，['Na', 0.1, 0.0, 0.0]。
                2.如果指定原子坐标类型，类型必须为‘Direct’或‘Cartesian’。如，['Na', 0.1, 0.0, 0.0, 'Direct']、['Na', 5.234, 0.0, 0.0, 'Cartesian']。
            
            kwargs:
                isNormalizingCoordinate (default=True):当给定原子的类型为格式化数组时，默认移除原子坐标上的平移周期性，以保证其值在0.0～1.0之间。
                precision (default=1e-3):比较原子是否重叠的精度。当“atom”参数为格式化数组时，此参数用于判断给定的原子是否在结构中（比较给定原子坐标与结构中的原子坐标之间的距离）。
                
        返回：
            如果不等价位置中存在该原子，返回原子对象。否则，返回 None。
        """
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
            return get_entity_from_collection(formated_atom, self.atoms, 'atom', lattice=self.structure.lattice, isNormalizingCoordinate=isNormalizingCoordinate, precision=precision)
        else:
            return None
    def del_atom(self, index_or_atom, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        delete a atom from this site. Note that it will delete this atom's object from other related classes's objects.
        
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
            
        从不等价位置中删除一个原子。注意：当删除原子时，基于程序效率上的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
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
            structure=self.structure
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
        
    def create(self, position, isPersist, **kwargs):
        """
        create a site's object.
        
        Arguments:
            position: site's position.
            isPersist: if True, save to database. Conversely, only run in memory.
            
            kwargs:
                structure: structure's object.
                atoms: collection of atom's object.
                wyckoffSite: wyckoffSite's object.
                coordination_nuber: 
        Returns:
            site's object.
            
        创建一个不等价位置对象。
        
        参数：
            position:不等价位置的位置坐标。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                structure:结构对象。
                atoms:原子对象集合。
                wyckoffSite:wyckoff位置对象。
                coordination_nuber:原子的配位数。
                
        返回：
            不等价位置对象。
        """
        from jump2.db.materials.structure import Structure
        from jump2.db.materials.atom import Atom
        from jump2.db.materials.spacegroup import WyckoffSite
        
        if isPersist:
            self.save()
            
        self.position=position
            
        if 'structure' in kwargs:
            structure=kwargs['structure']
            if not isinstance(structure, Structure):
                raise ValueError('unrecognized structure')
            structure.add_site(self)
            if isPersist:
                structure.site_set.add(self)
        if 'atoms' in kwargs:
            atoms=kwargs['atoms']
            for atom in atoms:
                if not isinstance(atom, Atom):
                    raise ValueError('unrecognized atom')
                self.add_atom(atom)
                if isPersist:
                    self.atom_set.add(atom)
        if 'wyckoffSite' in kwargs:
            wyckoffSite=kwargs['wyckoffSite']
            if not isinstance(wyckoffSite, WyckoffSite):
                raise ValueError('unrecognized wyckoffSite')
            wyckoffSite.add_site(self)
            if isPersist:
                wyckoffSite.site_set.add(self)
                
        if 'coordination_number' in kwargs:
            self.coordination_number=kwargs['coordination_number']
        
        if isPersist:
            self.save()
                
        return self
        
    def nearest_neighbors(self, cutoff=3.0):        
        """
        find out the nearest neighbors of a site.
        
        找出不等价位置的最近临。
        """
        return self.atoms[0].nearest_neighbors(cutoff=cutoff)
    
            