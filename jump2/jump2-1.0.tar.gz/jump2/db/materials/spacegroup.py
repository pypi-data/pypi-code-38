#coding=utf-8
'''
Created on Oct 21, 2017

@author: Yuhao Fu
'''
from __future__ import unicode_literals
from django.db import models

from jump2.db.utils.customField import NumpyArrayField
from jump2.db.utils.customField import DictField

    
class Operation(models.Model):
    """
    operation.
    
    Relationships:
        operation
            |- spacegroup
            
    Attributes:
        operation
            |- operation
            # ---------- database ----------
            |- spacegroup_set
            # ---------- build-in ----------
            |- spacegroups
            
    操作类。
    
    关系:
        operation
            |- spacegroup
            
    属性:
        operation
            |- operation
            # ---------- database ----------
            |- spacegroup_set
            # ---------- build-in ----------
            |- spacegroups
    """
    operation=DictField(blank=True, null=True) # i.e. {'translation': np.ndarray ([3] (float)), 'rotation': np.ndarray ([3,3] (int))}
    
    class Meta:
        app_label='materials'
        db_table='operation'
        default_related_name='operation_set'
        
    def __str__(self):
        return str(self.operation)
    
    _spacegroups=None
    @property
    def spacegroups(self):
        """
        spacegroups contained the operation.
        
        含有该操作的空间群。
        """
        if self._spacegroups is None:
        #    if not self.id:
        #        self._spacegroups=[]
        #    else:
        #        self._spacegroups=list(self.spacegroup_set.all())
            self._spacegroups=[]
        return self._spacegroups
    @spacegroups.setter
    def spacegroups(self, spacegroups):
        """
        assign the value. Note that it will cover the previous value.
        
        Arguments:
            spacegroups: collection of spacegroup's object.
            
        Returns:
            True if the assignment is successful. Conversely, False.
            
        ‘spacegroups’属性的set方法。注意：该方法将会清除以前的数据。
        
        参数：
             spacegroups:空间群对象集合。
             
        返回：
            布尔值（True/False）。
        """
        import warnings
        
        for spacegroup in spacegroups:
            if not isinstance(spacegroup, Spacegroup):
                warnings.warn('invalid type')
                return False
        self._spacegroups=spacegroups
        return True
    def add_spacegroup(self, spacegroup):
        """
        add a spacegroup to this operation.
        
        Arguments:
            spacegroup: spacegroup's object.
            
        Returns:
            True if add a operation successfully. Conversely, False.
            
        添加一个空间群到操作中。
        
        参数：
            spacegroup:空间群对象。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(spacegroup, self.spacegroups, 'spacegroup'):
            self.spacegroups.append(spacegroup)
            spacegroup.operations.append(self)
            return True
        else:
            return False
        
    def create(self, operation, isPersist, **kwargs):
        """
        create a operation object.
        
        Arguments:
            operation: python dictionary. {'translation':translation, 'rotation':rotation}
            isPersit: if True, save to database. Conversely, only run in memory.
            
            kwargs:
                spacegroups: collection of spacegroup's object.
                
        Returns:
            operation's object.
                
        创建一个操作对象。
        
        参数：
            operation:操作的python字典。{'translation':translation, 'rotation':rotation}
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                spacegroups:空间群对象集合。
                
        返回：
            操作对象。
        """
        from jump2.db.utils.fetch import get_operation_from_db
        
        operation_obj=get_operation_from_db(operation)
        if operation_obj is None:
            self.operation=operation
        else:
            self=operation_obj
            
        if isPersist:
            self.save()
        if 'spacegroups' in kwargs:
            spacegroups=kwargs['spacegroups']
            for spacegroup in spacegroups:
                if isinstance(spacegroup, Spacegroup):
                    self.add_spacegroup(spacegroup)
                    if isPersist:
                        self.spacegroup_set.add(spacegroup)
        
        if isPersist:
            self.save()
       
        return self
    
class WyckoffSite(models.Model):
    """
    wyckoffSite.
    
    Relationships:
        wyckoffSite
            |- spacegroup
            |- site
            |- atom
            
    Attributes:
        wyckoffSite
            |- spacegroup
            |- symbol
            |- multiplicity
            |- position
            # ---------- database ----------
            |- site_set
            |- atom_set
            # ---------- build-in ----------
            |- sites
            |- atoms
            
    wyckoff位置。
    
    关系:
        wyckoffSite
            |- spacegroup
            |- site
            |- atom
            
    属性:
        wyckoffSite
            |- spacegroup
            |- symbol
            |- multiplicity
            |- position
            # ---------- database ----------
            |- site_set
            |- atom_set
            # ---------- build-in ----------
            |- sites
            |- atoms
    """
    
    # relationship
    spacegroup=models.ForeignKey('Spacegroup', blank=True, null=True)
    #structure=models.ForeignKey('Spacegroup', blank=True, null=True)
    
    symbol=models.CharField(max_length=1)
    multiplicity=models.IntegerField(blank=True, null=True)
    position=NumpyArrayField(blank=True, null=True) # [3, 3] (float)
    
    class Meta:
        app_label='materials'
        db_table='wyckoffSite'
        default_related_name='wyckoffSite_set'
        #unique_together=('symbol', 'multiplicity') need to consider position
    
    def __str__(self):
        return '%d%s [%f, %f, %f]' %(self.multiplicity, self.symbol, self.position[0], self.position[1], self.position[2])
    
    _sites=None
    @property
    def sites(self):
        """
        sites contained the wyckoffSite.
        
        属于该wyckoff位置的不等价位置。
        """
        if self._sites is None:
        #    if not self.id:
        #        self._sites=[]
        #    else:
        #        self._sites=list(self.site_set.all())
            self._sites=[]
        return self._sites
    @sites.setter
    def sites(self, sites):
        """
        assign the value. Note that it will cover the previous value.
        
        Arguments:
            sites: collection of site's object.
            
        Returns:
            True if the assignment is successful. Conversely, False.
            
        ‘sites’属性的set方法。注意：该方法将会清除以前的数据。
        
        参数：
             sites:不等价位置对象集合。
             
        返回：
            布尔值（True/False）。
        """
        import warnings
        from jump2.db.materials.site import Site
        
        for site in sites:
            if not isinstance(site, Site):
                warnings.warn('invalid type')
                return False
        self._sites=sites
        return True
    def add_site(self, site):
        """
        add site to this wyckoffSite.
        
        Arguments:
            site: site's object.
            
        Returns:
            True if add a site successfully. Conversely, False.
        
        添加一个不等价位置到wyckoffSite中。
        
        参数：
            site:不等价位置对象。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(site, self.sites, 'site'):
            self.sites.append(site)
            site.wyckoffSite=self
            return True
        else:
            return False
        
    _atoms=None
    @property
    def atoms(self):
        """
        atoms contained the wyckoffSite.
        
        属于该wyckoff位置的原子。
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
        self._atoms=atoms
        return True
    def add_atom(self, atom):
        """
        add atom to this wyckoffSite.
        
        Arguments:
            atom: atom's object.
            
        Returns:
            True if add a atom successfully. Conversely, False.
            
        添加一个原子到wyckoff位置中。
        
        参数：
            atom:原子对象。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(atom, self.atoms, 'atom'):
            self.atoms.append(atom)
            atom.wyckoffSite=self
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
            
        从wyckoff位置中获取给定的原子对象。
         
        参数：
            formated_atom:原子的格式化数组。注意：原子的格式化数组的格式需要符合以下规则：
                1.程序默认晶体结构中原子坐标的类型为分数坐标。如果原子坐标为分数坐标，可以不用指定坐标类型。如，['Na', 0.1, 0.0, 0.0]。
                2.如果指定原子坐标类型，类型必须为‘Direct’或‘Cartesian’。如，['Na', 0.1, 0.0, 0.0, 'Direct']、['Na', 5.234, 0.0, 0.0, 'Cartesian']。
            
            kwargs:
                isNormalizingCoordinate (default=True):当给定原子的类型为格式化数组时，默认移除原子坐标上的平移周期性，以保证其值在0.0～1.0之间。
                precision (default=1e-3):比较原子是否重叠的精度。当“atom”参数为格式化数组时，此参数用于判断给定的原子是否在结构中（比较给定原子坐标与结构中的原子坐标之间的距离）。
                
        返回：
            如果wyckoff位置中存在该原子，返回原子对象。否则，返回 None。
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
            if len(self.spacegroup.structures) != 1:
                warnings.warn("exist more than one structure in element.structures array, don't know which structure the element belong to")
                return None
            return get_entity_from_collection(formated_atom, self.atoms, 'atom', lattice=self.spacegroup.structures[0].lattice, isNormalizingCoordinate=isNormalizingCoordinate, precision=precision)
        else:
            return None
    def del_atom(self, index_or_atom, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        delete a atom from this wyckoffSite. Note that it will delete this atom's object from other related classes's objects.
        
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
            
        从wyckoff位置中删除一个原子。注意：当删除原子时，基于程序效率上的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
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
            if len(self.spacegroup.structures) != 1:
                warnings.warn("exist more than one structure in element.structures array, don't know which structure the element belong to")
                return None
            structure=self.spacegroup.structures[0]
            structure.del_atom(atom, isUpdatedInfo=False, isPersist=False)
            
            # default
            symprec=1e-5 # symprec
            angle_tolerance=-1.0 # angle_tolerance
            if 'symprec' in kwargs:
                symprec=kwargs['symprec']
            if 'angle_tolerance' in kwargs:
                angle_tolerance=kwargs['angle_tolerance']
            if isPersist:
                self.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
            elif isUpdatedInfo and not isPersist:
                self.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
            
            return True
        else:
            return False            
    
    def create(self, symbol, multiplicity, position, isPersist, **kwargs):
        """
        create a wyckoffSite's object.
        
        Arguments:
            symbol: symbol of Wyckoff site.
            multiplicity: 
            position:
            isPersist: if True, save to database. Conversely, only run in memory.
            
            kwargs:
                spacegroup: spacegroup's object.
                #structure: structure's object.
                sites: collection of site's object.
                atoms: collection of atom's object.
                
        Returns:
            wyckoffSite's object.
                
        创建一个wyckoff位置对象。
        
        参数：
            symbol:wyckoff位置的符号。
            multiplicity:
            position:
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                spacegroup:空间群对象。
                sites:不等价位置对象集合。
                atoms:原子对象集合。
                
        返回：
            wyckoff位置对象。
        """
        from jump2.db.materials.site import Site
        from jump2.db.materials.atom import Atom
        
        #formated_wyckoffSite=[symbol, multiplicity, position[0], position[1], position[2]]
        #wyckoffSite=get_wyckoffSite_from_db(formated_wyckoffSite)
        #if wyckoffSite is None:
        #    self.symbol=symbol
        #    self.multiplicity=multiplicity
        #    self.position=position
        #else:
        #    self=wyckoffSite
        
        #wyckoffSites_in_db=list(WyckoffSite.objects.all())
        #if wyckoffSites_in_db != []:
        #    for obj in wyckoffSites_in_db:
        #        if obj.symbol == symbol and \
        #            obj.multiplicity == multiplicity and \
        #            not(False in (obj.position == position)):
        #            self=obj
        
        self.symbol=symbol
        self.multiplicity=multiplicity
        self.position=position
        
        if isPersist:
            self.save()
            
        if 'spacegroup' in kwargs:
            spacegroup=kwargs['spacegroup']
            if isinstance(spacegroup, Spacegroup):
                spacegroup.add_wyckoffSite(self)
                if isPersist:
                    spacegroup.wyckoffSite_set.add(self)
        #if 'structure' in kwargs:
        #    structure=kwargs['structure']
        #    if isinstance(structure, Structure):
        #        structure.add_wyckoffSite(self)
        #        if isPersist:
        #            structure.wyckoffSite_set.add(self)
        if 'sites' in kwargs:
            sites=kwargs['sites']
            for site in sites:
                if isinstance(site, Site):
                    self.add_site(site)
                    if isPersist:
                        self.site_set.add(site)
        if 'atoms' in kwargs:
            atoms=kwargs['atoms']
            for atom in atoms:
                if isinstance(atom, Atom):
                    self.add_atom(atom)
                    if isPersist:
                        self.atom_set.add(atom)
        if isPersist:
            self.save()
                
        return self
        
class Spacegroup(models.Model):
    """
    spacegroup.
    
    Relationships:
        spacegroup
            |- structure
            |- operation
            |- wyckoffSite
            
    Attributes:
        spacegroup
            |- number
            |- international
            |- hm
            |- hall
            |- pearson
            |- schoenflies
            |- lattice_system
            
    空间群类。
    
    关系:
        spacegroup
            |- structure
            |- operation
            |- wyckoffSite
            
    属性:
        spacegroup
            |- number
            |- international
            |- hm
            |- hall
            |- pearson
            |- schoenflies
            |- lattice_system
    """    
    
    # relationship
    operation_set=models.ManyToManyField('Operation', blank=True)
    
    number=models.IntegerField(primary_key=True)
    international=models.CharField(max_length=20, blank=True, null=True)
    #hm=models.CharField(max_length=20, blank=True, null=True) # hall number
    hm=models.IntegerField(blank=True, null=True) # hall number
    hall=models.CharField(max_length=20, blank=True, null=True)
    pearson=models.CharField(max_length=20, blank=True, null=True)
    schoenflies=models.CharField(max_length=20, blank=True, null=True)
    lattice_system=models.CharField(max_length=20, blank=True, null=True)
    centerosymmetric=models.NullBooleanField(blank=True, null=True)
    
    class Meta:
        app_label='materials'
        db_table='spacegroup'
        default_related_name='spacegroup_set'
    
    def __str__(self):
        return '%s (%d)' %(self.international, self.number)
    
    _operations=None
    @property
    def operations(self):
        """
        operations for the spacegroup.
        
        空间群包含的操作。
        """
        if self._operations is None:
        #    if not Spacegroup.objects.filter(number=self.number).exists():
        #        self._operations=[]
        #    else:
        #        self._operations=list(self.operation_set.all())
            self._operations=[]
        return self._operations
    @operations.setter
    def operations(self, operations):
        """
        assign the value. Note that it will cover the previous value.
        
        Arguments:
            operations: collection of operation's object.
            
        Returns:
            True if the assignment is successful. Conversely, False.
            
        ‘operations’属性的set方法。注意：该方法将会清除以前的数据。
        
        参数：
            operations:操作对象集合。
            
        返回：
            布尔值（True/False）。
        """
        import warnings
        
        for operation in operations:
            if not isinstance(operation, Operation):
                warnings.warn('invalid type')
                return False
        self._operations=[]
        return True
    def add_operation(self, operation):
        """
        add operation to this spacegroup.
        
        Arguments:
            operation: operation's object.
            
        Returns:
            True if add a operation successfully. Conversely, False.
            
        添加一个操作到这个空间群中。
        
        参数：
            operation:操作对象。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(operation, self.operations, 'operation'):
            self.operations.append(operation)
            operation.spacegroups.append(self)
            return True
        else:
            return False
        
    _wyckoffSites=None
    @property
    def wyckoffSites(self):
        """
        wyckoffSites for the spacegroup.
        
        空间群包含的wyckoff位置。
        """
        if self._wyckoffSites is None:
        #    if not Spacegroup.objects.filter(number=self.number).exists():
        #        self._wyckoffSites=[]
        #    else:
        #        self._wyckoffSites=list(self.wyckoffSite_set.all())
            self._wyckoffSites=[]
        return self._wyckoffSites
    @wyckoffSites.setter
    def wyckoffSites(self, wyckoffSites):
        """
        assign the value. Note that it will cover the previous value.
        
        Arguments:
            wyckoffSites: collection of wyckoffSite's object.
            
        Returns:
            True if the assignment is successful. Conversely, False.
            
        ‘wyckoffSites’属性的set方法。注意：该方法将会清除以前的数据。
        
        参数：
            wyckoffSites:wyckoff位置对象集合。
            
        返回：
            布尔值（True/False）。
        """
        import warnings
        
        for wyckoffSite in wyckoffSites:
            if not isinstance(wyckoffSite, WyckoffSite):
                warnings.warn('invalid type')
                return False
        self._wyckoffSites=[]
        return True
    def add_wyckoffSite(self, wyckoffSite):
        """
        add a wyckoffSite to this spacegroup.
        
        Arguments:
            wyckoffSite: wyckoffSite's object.
            
        Returns:
            True if add a operation successfully. Conversely, False.
            
        添加一个wyckoff位置到这个空间群中。
        
        参数：
            wyckoffSite:wyckoff位置对象。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(wyckoffSite, self.wyckoffSites, 'wyckoffSite'):
            self.wyckoffSites.append(wyckoffSite)
            wyckoffSite.spacegroup=self
            return True
        else:
            return False
    
    _structures=None
    @property
    def structures(self):
        """
        structures with the spacegroup.
        
        具有该空间群的结构。
        """
        if self._structures is None:
        #    if not Spacegroup.objects.filter(number=self.number).exists():
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
            structures: collection of structure's object.
            
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
        add a structure to this spacegroup.
        
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
            structure.spacegroup=self
            return True
        else:
            return False

    def create(self, number, isPersist, **kwargs):
        """
        create spacegroup's object.
        
        Arguments:
            number: number of spacegroup.
            isPersist: if True, save to database. Conversely, only run in memory.
            
            kwargs:
                operations: collection of operation's object.
                wyckoffSites: collection of wyckoffSite's object.
                structures: collection of structure's object.
                
                international: international short symbol.
                hm: hall number.
                hall: hall symbol.
                pearson: 
                schoenflies:
                lattice_system:
                centerosymmetric:
                
        Returns:
            spacegroup's object.
                
        创建一个空间群对象。
        
        参数：
            number:空间群号。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                operations:操作对象集合。
                wyckoffSites:wyckoff位置对象集合。
                structures:结构对象集合。
                
                international:空间群国际符号。
                hm: hall数字。
                hall: hall符号。
                pearson: 
                schoenflies:
                lattice_system:
                centerosymmetric:
                
        返回：
            空间群对象。
        """
        from jump2.db.materials.structure import Structure
        
        self.number=number
        
        if isPersist:
            self.save()
        
        if 'operations' in kwargs:
            operations=kwargs['operations']
            for operation in operations:
                if isinstance(operation, Operation):
                    self.add_operation(operation)
                    if isPersist:
                        self.operation_set.add(operation)
        if 'wyckoffSites' in kwargs:
            wyckoffSites=kwargs['wyckoffSites']
            for wyckoffSite in wyckoffSites:
                if isinstance(wyckoffSite, WyckoffSite):
                    self.add_wyckoffSite(wyckoffSite)
                    if isPersist:
                        self.wyckoffSite_set.add(wyckoffSite)
        if 'structures' in kwargs:
            structures=kwargs['structures']
            for structure in structures:
                if isinstance(structure, Structure):
                    self.add_structure(structure)
                    if isPersist:
                        self.structure_set.add(structure)
        
        if 'international' in kwargs:
            self.international=kwargs['international']
        if 'hm' in kwargs:
            self.hm=kwargs['hm']
        if 'hall' in kwargs:
            self.hall=kwargs['hall']
        if 'pearson' in kwargs:
            self.pearson=kwargs['pearson']
        if 'schoenflies' in kwargs:
            self.schoenflies=kwargs['schoenflies']
        if 'lattice_system' in kwargs:
            self.lattice_system=kwargs['lattice_system']
        if 'centerosymmetric' in kwargs:
            self.centerosymmetric=kwargs['centerosymmetric']
            
        if isPersist:
            self.save()
                
        return self
            
    
    