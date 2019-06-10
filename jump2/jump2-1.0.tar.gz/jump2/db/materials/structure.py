#coding=utf-8
'''
Created on Oct 19, 2017

@author: Yuhao Fu, Shulin Luo, Bangyu Xing, qiaoling Xu
'''
from __future__ import unicode_literals
from django.db  import models

from fractions import gcd
from itertools import groupby
import numpy as np

from jump2.db.utils.customField import NumpyArrayField

from jump2.db.utils.convert import any2cartesian

from jump2.db.materials.case import Case
from jump2.db.materials.element import Element
from jump2.db.materials.species import Species
from jump2.db.materials.atom import Atom
from jump2.db.materials.spacegroup import WyckoffSite
from jump2.db.materials.site import Site


class StructureError(Exception):
    pass

class Structure(models.Model):
    """
    crystal structure.
    Note that:
        1.the type of atomic position is 'Direct' inside the jump2.
        2.default, removing the translation periodicity. for example, 
            if atomic coordinate is 1.2, the program will change the 
            value to 0.2 in creating structure's instance.
            
    Relationships:
        structure
            |- prototype
            |- case
            |- composition
            |- element
            |- species
            |- atom
            |- site
            |- spacegroup
            
    Attributes:
        structure
            |- composition: composition of structure.
            |- spacegroup: specaegroup of structure.
            |- prototype: prototype of structure.
            |- label: label of structure.
            |- comment: comment of structure
            |- natoms: number of atoms in structure.
            |- nsites: number of sites in structure.
            |-ntypes: number of element's types in structure.
            |- multiple: number of formula in structure.
            |- lattice: lattice vector of structure. 
            |- volume: volume of lattice for the structure.
            |- volume_per_atom: volume of lattice per atom for the structure.
            # ---------- many-to-many in database ----------
            |- case_set: cases contained the structure.
            |- element_set: elements of structure in database.
            |- species_set: species of structure in database.
            |- site_set: sites of structure in database.
            |- atom_set: atoms of structure in database.
            # ---------- build-in in memory ----------
            |- cases: collection of cases.
            |- elements: collection of elements in structure.
            |- species: collection of species in structure.
            |- sites: collection of sites in structure.
            |- atoms: collection of atoms in structure.
            
    Examples:
        >>> raw=Read('../examples/structures/In4Te3.cif').run()
        >>> s=Structure().create(raw)
    
    # （only read）也许这部分文档，需要更加详细说明整个数据的语法规则，如何使用jump2数据库。
    
    晶体结构类。
    注意：1.在jump2数据库内部，晶体结构中原子坐标的类型是‘Direct’。
         2.在读取、创建晶体结构对象时，默认会移除原子的平移周期性，让晶胞中的所有原子都在同一个胞内，即原子的分数坐标都在0.0～1.0之间。
             比如： 创建结构时，读入原子的分数坐标为1.2，程序默认将其坐标转换为0.2。
             
    关系：
        structure
            |- prototype
            |- case
            |- composition
            |- element
            |- species
            |- atom
            |- site
            |- spacegroup
            
    属性:
        structure
            |- composition:结构的化学式。
            |- spacegroup:结构的空间群。
            |- prototype:结构所属的结构原型。
            |- label:结构的标签。
            |- comment:对结构的注释。
            |- natoms:结构中的原子数。
            |- nsites:结构中的不等价位置数。
            |-ntypes:结构中的元素种类数。
            |- multiple:结构包含的分子式倍数。
            |- lattice:结构的晶胞基矢。
            |- volume:晶胞体积
            |- volume_per_atom:每原子的晶胞体积。
            # ---------- database ----------
            |- case_set:包含该结构的计算实例。
            |- element_set:结构中的元素。
            |- species_set:结构中的元素种类。
            |- site_set:结构中的不等价位置。
            |- atom_set:结构中的原子。
            # ---------- build-in ----------
            |- cases:包含该结构的计算实例。
            |- elements:结构中的元素。
            |- species:结构中的元素种类。
            |- sites:结构中的不等价位置。
            |- atoms:结构中的原子。
             
    例子：
        1.获得结构对象有两个途径：1）读取结构文件；2）查询jump2数据库中的结构。
            读取结构文件：
                >>> from jump2.db.iostream.read import Read
                >>> raw=Read('../examples/structures/In4Te3.cif').run()
                >>> s=Structure().create(raw, isPersist=True)
            查询jump2数据库中的结构：
                >>> from jump2.db.utils.initialization import initialize_relationships
                >>> s=Structure.object.get(id=1) # get structure by its id.
                >>> initialize_relationships(s) # initialize build-in relationships in memory.
                注意：从数据库得到结构，需要调用utils/initialization目录下的initialize_relationships方法，初始化内建关系。
                
            输出结构文件：
                >>> from jump2.db.iostream.write import Write
                >>> Write(s1, 'xxx/examples/structures/In4Te3.vasp', dtype='poscar').run()
        
        2.structure对象中保存了与该结构相关的信息（比如，化学式、元素、原子、不等价位置，等）。
            1）如果其属性为数组（比如，structure下包含多个elments，等）时，有两种查询机制：
                I.内建的、只针对跟该结构本身相关的属性数组，不关联其他结构，其查询方法：object.xxxs (比如，strucutre.elements)；
                    只与该结构关联的信息：
                    structure
                        |- cases
                        |- elements
                        |- species
                        |- atoms
                        |- sites
                    >>> s.elements # get all elements in this structure.
                    >>>> s.atoms[0] # get the first atom in this structure.
                    >>> s.elements[0].atoms # get all atoms of the first element in this structure.
                
                    
                II.采用Django框架，关联其他结构，查询整个数据库与之相关的信息，其查询方法：object.xxx_set.all() (比如，structure.element_set.all())。
                    查询整个数据库与之相关的信息：
                    structure
                        |- case_set.all()
                        |- element_set.all()
                        |- specie_set.all()
                        |- atom_set.all()
                        |- site_set.all()
                    >>> s.element_set.all()[0].structure_set.all() # get all structures related with the first element of 's' structure.
            2)对于其属性为单值时，可以通过以下方法查询：
                >>> s.composition # get composition.
                >>> s.composition.formula # get composition's formula.
        3. 对结构进行操作。
            >>>> s.add_atom(['Na', 0.1, 0.0, 0.0], isUpdatedInfo=True, isPersist=True) # add a atom, and synchronize the database of jump2.
                
            >>>> s.del_atom(1, isUpdatedInfo=True, isUpdatedInfo=True, isPersist=True) # delete a atom, and synchronize the database of jump2.
            >>>> s.del_atom(['Na', 0.1, 0.0, 0.0], isUpdatedInfo=True, isPersist=True) # delete a atom, and synchronize the database of jump2.
                
            >>>> s.del_element(1, isUpdatedInfo=True, isPersist=True) # delete a element, and synchronize the database of jump2.
            >>>> s.del_element('Na', isUpdatedInfo=True, isPersist=True) # delete a element, and synchronize the database of jump2.
            
            >>> s.del_species('Na+', isUpdatedInfo=False, isPersist=False) # delete a species, don't update the build-in relationships in memory and don't synchronize the database of jump2.
            >>> s.update(isPersist=False) # update the build-in relationships in memory and don't synchronize the database of jump2.
            
            >>> s.substitute_atom(['Na', 0.1, 0.0, 0.0], 'Sb', isUpdatedInfo=False, isPersist=False) # change a atom's element, don't update the build-in relationships in memory and don't synchronize the database of jump2.
            >>> s.update(isPersist=True) # update the build-in relationships in memory and synchronize the database of jump2.
    """

    # relationship
    composition=models.ForeignKey('Composition', null=True)
    element_set=models.ManyToManyField('Element')
    species_set=models.ManyToManyField('Species')
    spacegroup=models.ForeignKey('Spacegroup', blank=True, null=True)
    
    #prototype=models.ForeignKey('Prototype', blank=True, null=True, related_name='+')
    prototype=models.ForeignKey('Prototype', blank=True, null=True)
    
    label=models.CharField(null=True, blank=True, max_length=80)
    comment=models.CharField(default='', max_length=80) # comment line in POSCAR (Line: 1)
    
    natoms=models.IntegerField(blank=True, null=True)
    nsites=models.IntegerField(blank=True, null=True)
    ntypes=models.IntegerField(blank=True, null=True)
    
    multiple=models.IntegerField(blank=True, null=True) # times of formula
    
    lattice=NumpyArrayField(blank=True, null=True) # [3, 3] (float)
    volume=models.FloatField(blank=True, null=True)
    volume_per_atom=models.FloatField(blank=True, null=True)
    
    class Meta:
        app_label='materials'
        db_table='structure'
        default_related_name='structure_set'
    
    def __str__(self):
        return self.composition.formula

    _cases=None
    @property
    def cases(self):
        """
        cases in structure.
        
        结构的计算实例。
        """
        if self._cases is None:
            if not self.id:
                self._cases=[]
            else:
                self._cases=list(self.case_set.all())
        return  self._cases
    def add_case(self, case, isPersist=False):
        """
        add a case to this structure.
        
        Arguments:
            case: case of calculation.
            isPersist (default=False): whether to save to the database.
            
        Returns:
            True if add a case successfully. Conversely, False.
        
        添加一个计算实例到结构的属性数组（cases）中。
        
        参数：
            case: 计算实例对象。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(case, self.cases, 'case'):
            self.cases.append(case)
            case.structure=self
            if isPersist:
                if not Case.objects.filter(name=case.name).exists():
                    case.save()
                self.save()
            return True
        else:
            return False
    def get_case(self, name):
        """
        get the case's object with the given name.
        
        Arguments:
            name: case's name.
        
        Returns:
            case's object if it exists. Conversely, return the None.
            
        从结构中获取给定名称的实例对象。
        
        参数：
            name:实例的名称。
        
        返回：
            如果结构中存在该名称的实例，返回实例对象。否则，返回 None。
        
        """
        for case in self.cases:
            if case.name == name:
                return case
        return None
    def del_case(self, index_or_case, isPersist=False):
        """
        delete a case from this structure.
        
        Arguments:
            index_or_case: case's index, name or object.
            isPersist (default=False): whether to save to the database.
            
        returns:
            True if delete a case successfully. Conversely, False.
            
        从结构中删除一个计算实例。
        
        参数：
            index_or_case:参数的值可以是计算实例在结构的实例属性数组中的索引（index）、名称或实例对象。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
        返回：
            布尔值（True/False）。
        """
        import warnings
        
        case=None
        if isinstance(index_or_case, int):
            index=index_or_case
            if index < 0 or index > len(self.cases):
                warnings.warn("beyond the range of cases' array")
                return False
            case=self.cases[index]
        elif isinstance(index_or_case, basestring):
            name=index_or_case
            case=self.get_case(name)
            if case is None:
                warnings.warn("don't have %s in the structure" %name)
                return False
        elif isinstance(index_or_case, Case):
            case=index_or_case
            if not case in self.cases:
                warnings.warn("don't have this instance of case in the structure")
                return False
        else:
            warnings.warn('unrecognized index_or_case')
            return False
            
        self.cases.remove(case)
        if isPersist:
            case.delete()
        return True
        
    _elements=None
    @property
    def elements(self):
        """
        elements in structure.
        
        结构的元素。
        """
        if self._elements is None:
            if not self.id: # don't exist in database
                self._elements=[]
            else:
                self._elements=list(self.element_set.all())
        return self._elements
    def add_element(self, element):
        """
        add a element to this composition.
        
        Arguments:
            element: element's object.
            
        Returns:
            True if add a element successfully. Conversely, False.
            
        添加一个元素到结构对象的属性数组（elements）中。
        
        参数：
            element:元素对象。
        
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(element, self.elements, 'element'):
            self.elements.append(element)
            element.structures.append(self)
            return True
        else:
            return False
    def get_element(self, symbol):
        """
        get the element's object with the given symbol.
        
        Arguments:
            symbol: element's symbol.
        
        Returns:
            element's object if it exists. Conversely, return the None.
            
        从结构中获取给定符号的元素对象。
        
        参数：
            symbol:元素符号。比如，H
        
        返回：
            如果结构中存在该元素，返回元素对象。否则，返回：None。
        """
        for element in self.elements:
            if element.symbol == symbol:
                return element
        return None
    def del_element(self, index_or_element, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        delete a element from this structure. Note that it will delete this element's object from other related classes's objects.
        
        Arguments:
            index_or_element: element's index, symbol or object.
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup). 
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
                
        Returns:
            True if add a element successfully. Conversely, False.
        
        从结构中删除一个元素。注意：当删除元素时，处于效率的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
        程序默认不会更新结构（更新化学式，删除与该元素关联的所有元素种类、原子对象，更新不等价位置、空间群和WyckoffSite，等）。
        
        参数：
            index_or_element:其值可以是元素在结构的元素属性数组中的索引（index）、元素符号或元素对象。
            isUpdatedInfo (default=False): 是否更新与结构的数据信息（比如，化学式和对称信息，等）。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                symprec (default=1e-5):找结构对称性时，采用的精度。
                angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差值。
            
        返回：
            布尔值（True/False）。
        """
        import warnings
        
        element=None
        if isinstance(index_or_element, int): # index
            index=index_or_element
            if index < 0 or index > self.ntypes:
                warnings.warn("beyond the range of elements' array")
                return False
            element=self.elements[index]
        elif isinstance(index_or_element, basestring): # symbol
            symbol=index_or_element
            element=self.get_element(symbol)
            if element is None:
                warnings.warn("don't have %s in the structure" %symbol)
                return False
        elif isinstance(index_or_element, Element): # instance
            element=index_or_element
            if not element in self.elements:
                warnings.warn("don't have this instance of element in the structure")
                return False
        else:
            warnings.warn('unrecognized index_or_element')
            return False
        
        # delete all atoms of this element
        for atom in list(element.atoms):
            self.del_atom(atom, isUpdatedInfo=False, isPersist=False)
        
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
        
    _species=None
    @property
    def species(self):
        """
        species in structure.
        
        结构的元素种类。
        """
        if self._species is None:
            if not self.id:
                self._species=[]
            else:
                self._species=list(self.species_set.all())
        return self._species
    def add_species(self, species):
        """
        add a species to the structure.
        
        Arguments:
            species: element's species in this structure.
        
        Returns:
            True if add a species successfully. Conversely, False.
            
        添加一个元素种类到结构对象的属性数组（species）中。
        
        参数：
            species:元素种类对象。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(species, self.species, 'species'):
            self.species.append(species)
            species.structures.append(self)
    def get_species(self, name):
        """
        get the species's object with the given name.
        
        Arguments:
            name: species's name.
        
        Returns:
            species's object if it exists. Conversely, return the None.
            
        从结构中获得给定名称的元素种类对象。
        
        参数：
            name:元素种类的名称。比如，Fe2+
            
        返回：
            如果结构中存在该元素种类，返回元素种类对象。否则，返回：None。
        """
        for species in self.species:
            if species.name == name:
                return species
        return None
    def del_species(self, index_or_species, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        delete a species from this structure. Note that it will delete this specise's object from other related classes's objects.
        
        Arguments:
            index_or_species: species's index, name or object.
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup). 
            isPersist (default=False): whether to save to the database.
        
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
                
        从结构中删除一个元素种类。注意：当删除元素种类时，基于程序效率上的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
        程序默认不会更新结构（更新化学式，删除与该元素种类关联的所有原子对象，更新不等价位置、空间群和WyckoffSite，等）。
        
        参数：
            index_or_species:其值可以是元素种类在结构的元素种类属性数组中的索引（index）、元素种类的名称或元素种类对象。
            isUpdatedInfo (default=False): 是否更新结构的其他关联数据信息（化学式（composition）、不等价位置，等）。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                symprec (default=1e-5):找结构对称性时，采用的精度。
                angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差值。
        
        返回：
            布尔值（True/False）。
        """
        import warnings
        
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
            self.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)
        elif isUpdatedInfo and not isPersist:
            self.update(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance)
            
        return True

    _sites=None
    @property
    def sites(self):
        """
        sites in structure.
        
        结构的不等价位置。
        """
        if self._sites is None:
            if not self.id:
                self._sites=[]
            else:
                self._sites=list(self.site_set.all())
        return self._sites
    def add_site(self, site):
        """
        add a site to this structure.
        
        Arguments:
            site: site's object.
            
        Returns:
            True if add a site successfully. Conversely, False.
            
        添加一个不等价位置到结构对象的属性数组（sites）中。
        
        参数：
            site:不等价位置对象。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(site, self.sites, 'site'):
            self.sites.append(site)
            site.structure=self
            return True
        else:
            return False
    def get_site(self, position, **kwargs):
        """
        get a site by its position.
        
        Arguments:
            position: position of site. Note that type of coordinate is 'Direct',  you can not specify
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
        Returns:
            site's object if exist. Conversely, return None.
            
        从结构中获得给定位置的不等价位置对象。
        
        参数：
            position:不等价位置的坐标。注意：不等价位置的坐标的格式需要符合以下规则：
                1.程序默认晶体结构中坐标的类型为分数坐标。如果坐标为分数坐标，可以不用指定坐标类型。如，[0.1, 0.0, 0.0]。
                2.如果指定坐标类型，类型必须为‘Direct’或‘Cartesian’。如，[0.1, 0.0, 0.0, 'Direct']、[5.234, 0.0, 0.0, 'Cartesian']。
                
                kwargs：
                    isNormalizingCoordinate (default=True):当给定原子的类型为格式化数组时，默认移除原子坐标上的平移周期性，以保证其值在0.0～1.0之间。
                    precision (default=1e-3):比较原子是否重叠的精度。此参数用于判断给定的坐标是否在结构的不等价位置数组中（比较给定坐标与结构中的不等价位置坐标之间的距离）。
                    
        返回：
            如果结构中存在该不等价位置，返回不等价位置对象。否则，返回 None。
        """
        from jump2.db.utils.fetch import get_entity_from_collection
        
        # remove atomic translation periodicity
        isNormalizingCoordinate=True
        if 'isNormalizingCoordinate' in kwargs:
            isNormalizingCoordinate=kwargs['isNormalizingCoordinate']
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
        return get_entity_from_collection(position, self.sites, 'site', isNormalizingCoordinate=isNormalizingCoordinate, precision=precision)
    def del_site(self, index_or_site, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        delete a site from this structure. Note that it will delete this site's object from other related classes's objects.
        
        Arguments:
            index_or_site: site's index, position or object.
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
            True if delete a site successfully. Conversely, False.
            
        从结构中删除一个不等价位置。注意：当删除不等价位置时，基于程序效率上的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
        程序默认不会更新结构（更新化学式，删除与该不等价位置关联的所有原子对象，更新空间群和WyckoffSite，等）。
        
        参数：
            index_or_site:其值可以是不等价位置在结构的不等价位置属性数组中的索引（index）、不等价位置的坐标或不等价位置对象。注意：不等价位置的坐标的格式需要符合以下规则
                1.程序默认晶体结构中坐标的类型为分数坐标。如果坐标为分数坐标，可以不用指定坐标类型。如，[0.1, 0.0, 0.0]。
                2.如果指定坐标类型，类型必须为‘Direct’或‘Cartesian’。如，[0.1, 0.0, 0.0, 'Direct']、[5.234, 0.0, 0.0, 'Cartesian']。
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
        from jump2.db.utils.check import check_formated_position
        
        site=None
        if isinstance(index_or_site, int):
            index=index_or_site
            if index < 0 or index > self.nsites:
                warnings.warn("beyond the range of site's index")
                return False
            site=self.sites[index]
        elif check_formated_position(index_or_site):
            position=index_or_site
            
            # remove atomic translation periodicity
            isNormalizingCoordinate=True
            if 'isNormalizingCoordinate' in kwargs:
                isNormalizingCoordinate=kwargs['isNormalizingCoordinate']
            precision=1e-3
            if 'precision' in kwargs:
                precision=kwargs['precision']
            
            site=self.get_site(position, isNormalizingCoordinate=isNormalizingCoordinate, precision=precision)
            if site is None:
                return False
        elif isinstance(index_or_site, Site):
            site=index_or_site
            if not site in self.sites:
                warnings.warn("site doesn't belong to this structure")
                return False
            
        # delete all atoms of this site
        for atom in list(site.atoms):
            self.del_atom(atom, isUpdatedInfo=False, isPersist=False)
            
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
                   
    _atoms=None
    @property
    def atoms(self):
        """
        atoms in structure.
        
        结构的原子。
        """
        if self._atoms is None:
            if not self.id:
                self._atoms=[]
            else:
                self._atoms=list(self.atom_set.all())
        return self._atoms
    def add_atom(self, atom, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        add a atom to this structure.
        Arguments:
            atom: atom's object or formated string. i.e. if type of coordinate is 'Direct',  you 
                        can not specify the type. But, for 'Cartesian', must be given. The valid formation:
                            ['Na', 0.1, 0.0, 0.0, 'Direct']
                            ['Na', 0.1, 0.0, 0.0]
                            ['Na', 5.234, 0.0, 0.0, 'Cartesian']
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup). 
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                isNormalizingCoordinate (default=True): whether to remove the periodic boundary condition, 
                    ensure the value of atomic coordinate is between 0 and 1 (i.e. 1.3 -> 0.3).
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
                species: species's name. i.e. Fe2+

        Returns:
            True if add a atom successfully. Conversely, False.
            
        添加一个原子到结构对象的属性数组（atoms）中。
        
        参数：
            atom:参数的值可以是原子的格式化数组或原子对象。原子的格式化数组的格式需要符合以下条件：
                1.程序默认晶体结构中原子坐标的类型为分数坐标。如果原子坐标为分数坐标，可以不用指定坐标类型。如，['Na', 0.1, 0.0, 0.0]。
                2.如果指定原子坐标类型，类型必须为‘Direct’或‘Cartesian’。如，['Na', 0.1, 0.0, 0.0, 'Direct']；['Na', 5.234, 0.0, 0.0, 'Cartesian']。
                3.‘Cartesian’类型的原子坐标，必须显式指定其类型。
            isUpdatedInfo (default=False): 是否更新结构的其他关联数据信息（如，化学式、不等价位置，等）。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs：
                isNormalizingCoordinate (default=True):是否移除原子坐标上的平移周期性，以保证其值在0.0～1.0之间。
                symprec (default=1e-5):找结构对称性时，采用的精度。
                angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差值。
                species:元素种类的名称。如，Fe2+
        返回：
            布尔值（True/False）。
        """
        import warnings
        from jump2.db.utils.check import exist, check_formated_atom, check_formated_atom_only_direct, check_formated_atom_only_cartesian
        from jump2.db.utils.convert import any2direct, normalize_position
        from jump2.db.cache.cachedElementProvider import CachedElementProvider
        from jump2.db.cache.cachedSpeciesProvider import CachedSpeciesProvider
        
        if not exist(atom, self.atoms, 'atom'):
            if isinstance(atom, Atom):
                if self.get_element(atom.element.symbol) is None:
                    self.add_element(atom.element)
                elif not atom.element in self.elements:
                    warnings.warn("element's object of given atom isn't in the structure, but have the same element's symbol")
                    return False
                self.atoms.append(atom)
                atom.structure=self
            elif check_formated_atom(atom):
                formated_atom=atom
                #if len(formated_atom) == 5 and formated_atom[-1].strip().lower().startswith('c'): # Cartesian
                if check_formated_atom_only_cartesian(formated_atom):
                    position=any2direct(self.lattice, formated_atom[1:5])
                    formated_atom=[formated_atom[0], position[0], position[1], position[2]]
                #elif len(formated_atom) == 5 and formated_atom[-1].strip().lower().startswith('d'): # Direct
                elif check_formated_atom_only_direct(formated_atom):
                    formated_atom=formated_atom[:4]
                
                symbol_of_element=formated_atom[0]
                element=self.get_element(symbol_of_element)
                position=formated_atom[1:]
                
                # remove atomic translation periodicity
                isNormalizingCoordinate=True
                if 'isNormalizingCoordinate' in kwargs:
                    isNormalizingCoordinate=kwargs['isNormalizingCoordinate']
                    if isinstance(isNormalizingCoordinate, bool):
                        warnings.warn('isNormalizingCoordinate must be boolean')
                        return False
                # normalize atomic coordinate
                if isNormalizingCoordinate: # revome translation periodicity
                    position=normalize_position(position, 'Direct')[:3]
                
                # check
                if not self.get_atom([symbol_of_element]+position) is None:
                    warnings.warn('exit given atom')
                    return False
                    
                if element is None: # don't exist in the structure
                    element=CachedElementProvider().get(symbol_of_element)
                    atom=Atom().create(element, position, isPersist=isPersist, structure=self)
                    self.ntypes=len(self.elements)
                else:
                    atom=Atom().create(element, position, isPersist=isPersist, structure=self)
            # atom
            self.natoms=len(self.atoms)
                
            # spcies
            if 'species' in kwargs:
                name=kwargs['species']
                species=self.get_species(name)
                if species is None:
                    species=CachedSpeciesProvider().get(name)
                    element.add_species(species)
                self.add_species(species)
                species.add_atom(atom)
            
            if isUpdatedInfo:
                # delete old composition
                #structures_of_composition=list(composition_old.structure_set.all())
                #if (structures_of_composition == []) or (len(structures_of_composition) == 1 and structures_of_composition[0].id == self.id):
                #    composition_cache='composition_%s' %composition_old.formula
                #    cache.expire(composition_cache, timeout=0)
                #    composition_old.delete()
                
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
            warnings.warn('exit given atom')
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
            
        从结构中获得给定的原子对象。
        
        参数：
            formated_atom:原子的格式化数组。注意：原子的格式化数组的格式需要符合以下规则：
                1.程序默认晶体结构中原子坐标的类型为分数坐标。如果原子坐标为分数坐标，可以不用指定坐标类型。如，['Na', 0.1, 0.0, 0.0]。
                2.如果指定原子坐标类型，类型必须为‘Direct’或‘Cartesian’。如，['Na', 0.1, 0.0, 0.0, 'Direct']、['Na', 5.234, 0.0, 0.0, 'Cartesian']。
                
                kwargs：
                    isNormalizingCoordinate (default=True):当给定原子的类型为格式化数组时，默认移除原子坐标上的平移周期性，以保证其值在0.0～1.0之间。
                    precision (default=1e-3):比较原子是否重叠的精度。当“atom”参数为格式化数组时，此参数用于判断给定的原子是否在结构中（比较给定原子坐标与结构中的原子坐标之间的距离）。
        
        返回：
            如果结构中存在该原子，返回原子对象。否则，返回 None。
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
            return get_entity_from_collection(formated_atom, self.atoms, 'atom', lattice=self.lattice, isNormalizingCoordinate=isNormalizingCoordinate, precision=precision)
        else: 
            return None
    def del_atom(self, index_or_atom, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        delete a atom from this structure. Note that it will delete this atom's object from other related classes's objects.
        
        Arguments:
            index_or_atom: atom's index, formated atom or object.
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
            
        从结构中删除一个原子。注意：当删除原子时，基于程序效率上的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
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
        
        atom=None
        if isinstance(index_or_atom, int):
            index=index_or_atom
            if index < 0 or index > self.natoms:
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
            if not atom in self.atoms:
                warnings.warn("atom doesn't belong to this structure")
                return False
        else:
            warnings.warn('unrecognized index_or_atom')
            return False
        
        # remove atom
        # structure
        structure=atom.structure
        if self.natoms == 1:
            warnings.warn("don't remove the last atom")
            return False
        structure.atoms.remove(atom)
        structure.natoms=len(structure.atoms)
        # species
        species=atom.species
        if not species is None:
            species.atoms.remove(atom)
        # element
        element=atom.element
        element.atoms.remove(atom)

        # speices
        if not species is None:
            if species.atoms == []:
                # structure
                structure.species.remove(species)
                # element
                element.species.remove(species)
        
        # element
        if element.atoms == []:
            # structure
            structure.elements.remove(element)
        
        if isUpdatedInfo:
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
    def substitute_atom(self, index_or_atom, symbol_of_element, isUpdatedInfo=False, isPersist=False, **kwargs):
        """
        substitute element of a atom by new element.
        
        Arguments:
            index_or_atom: atom's index, formated atom or object.
            symbol_of_element: element's symbol.
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
            True if substitute a atom successfully. Conversely, False.
            
        替换结构中给定原子的元素。基于程序效率上的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
        程序默认不会更新结构（更新化学式，更新空间群和WyckoffSite，等）。
        
        参数：
            
            index_or_atom: 其值可以是原子在结构的原子属性数组中的索引（index）、原子的格式化数组或原子对象。注意：原子的格式化数组的格式需要符合以下规则：
                1.程序默认晶体结构中原子坐标的类型为分数坐标。如果原子坐标为分数坐标，可以不用指定坐标类型。如，['Na', 0.1, 0.0, 0.0]。
                2.如果指定原子坐标类型，类型必须为‘Direct’或‘Cartesian’。如，['Na', 0.1, 0.0, 0.0, 'Direct']、['Na', 5.234, 0.0, 0.0, 'Cartesian']。
            symbol_of_element: 将要替换为的元素名.
            isUpdatedInfo (default=False):是否更新结构的其他关联数据信息（如，化学式、不等价位置，等）。
            isPersist (default=False): 是否持久化，即将结构保存到数据库中。
            
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

        atom=None
        if isinstance(index_or_atom, int):
            index=index_or_atom
            if index < 0 or index > self.natoms:
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
            if not atom in self.atoms:
                warnings.warn("atom doesn't belong to this structure")
                return False
        else:
            warnings.warn('unrecognized index_or_atom')
            return False
        
        formated_atom_new=[symbol_of_element, atom.position[0], atom.position[1], atom.position[2]]
        self.add_atom(formated_atom_new, isUpdatedInfo=False, isPersist=False)
        self.del_atom(atom, isUpdatedInfo=False, isPersist=False)
        
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
                    
   
    def _clear_related_symmetry_info(self, isPersist=False):
        """
        clear the information related symmetry. It'll clear the site, wyckoffSite, spacegroup,...
        
        Arguments:
            isPersist (default=False): whether to save to the database.
        
        清除结构中与对称信息相关的数据。
        
        参数：
            isPersist (default=False):是否持久化，即更新数据库中对应的数据。
        """
        # related to site
        for site in list(self.sites): # Here, must convert to list.
            self.sites.remove(site)
            if isPersist:
                if not site.id is None:
                    site.wyckoffSite.delete()
                    site.delete()
        if isPersist:
            for site in list(self.site_set.all()):
                site.wyckoffSite.delete()
                site.delete()    
        for i in xrange(0, len(self.atoms)):
            self.atoms[i].site=None
            self.atoms[i].wyckoffSite=None
            
        # related to spacegroup
        self.spacegroup=None
    
    def _update_related_symmetry_info(self, symprec, angle_tolerance, isPersist=False, **kwargs):
        """
        update the information related symmetry.
        
        Arguments:
            symprec: precision when to find the symmetry.
            angel_tolerance: a experimental argument that controls angle tolerance between basis vectors.
            isPersist (default=False): whether to save to the database.

            kwargs:
                precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that,
                    to determine whether this atom is in collection by comparing its distance from other atoms.

        更新结构的对称信息。
        
        参数：
            symprec:找结构对称性时，采用的精度。
            angle_tolerance:找结构对称性时，控制晶胞基矢之间的角度容差。
            isPersist (default=False):是否持久化，即更新数据库中对应的数据。
            
            kwargs:
                precision (default=1e-3):比较原子是否重叠的精度。当“atom”参数为格式化数组时，此参数用于判断给定的原子是否在结构中（比较给定原子坐标与结构中的原子坐标之间的距离）。
        """
        import collections
        import spglib
        from jump2.db.utils.fetch import get_symbol_by_z, get_index_from_collection
        from jump2.db.utils.convert import raw2std_position
        from jump2.db.cache.cachedSpacegroupProvider import CachedSpacegroupProvider
        from jump2.db.cache.cachedOperationProvider import CachedOperationProvider
        
        if not self.id:
            isPersist=False
            
        # Firstly, clear data related symmetry information. Then, initialize these values related with symmetry.
        self._clear_related_symmetry_info(isPersist=isPersist)
        
        cell=self.formatting(dtype='cell')
        cell=(cell['lattice'], cell['positions'], cell['numbers'])
        positions=cell[1]
        numbers=cell[2]
        ordered_atoms=[] # ordered atoms' object according to cell
        for i in xrange(0, len(positions)):
            formated_atom=[get_symbol_by_z(cell[2][i]), positions[i][0], positions[i][1], positions[i][2]]
            ordered_atoms.append(self.get_atom(formated_atom))
        dataset=spglib.get_symmetry_dataset(cell, symprec=symprec, angle_tolerance=angle_tolerance)
        #for i in xrange(dataset['hall_number'], 531):
        #    tmp=spglib.get_symmetry_dataset(cell, symprec=symprec, angle_tolerance=angle_tolerance, hall_number=i)
        #    if tmp is None:
        #        break
        #    else:
        #        print tmp
        #        for position in cell[1]:
        #            position_std=raw2std_position(position, tmp['transformation_matrix'], tmp['origin_shift'])
        #            print position, '>>',position_std
        spacegroup=CachedSpacegroupProvider().get(dataset['number'])
        if spacegroup is None:
            #spacegroup=CachedSpacegroupProvider().set(dataset['number'], international=dataset['international'], hm=dataset['hall_number'], hall=dataset['hall'])
            spacegroup=CachedSpacegroupProvider().set(dataset['number'], international=dataset['international'])
        spacegroup.add_structure(self)
        
        # pearson
        # schoenflies
        # lattice_system
        # centerosymmetric
        
        for i in xrange(0, len(dataset['translations'])):
            translation=dataset['translations'][i]
            rotation=dataset['rotations'][i]
            
            operation=CachedOperationProvider().get({'translation':translation, 'rotation':rotation})
            operation.add_spacegroup(spacegroup)
        
        # wyckoffSite, site
        # note that wyckoffs correspond to the standardize structure by spglib, 
        # while the equivalent_atoms correspond to the raw structure.
        wyckoff=dataset['wyckoffs']
        equivalent_atoms=dataset['equivalent_atoms']
        wyckoff_symbol=[]
        wyckoff_symbol_number=[]
        
        iequivalent_atoms=collections.OrderedDict() # {iequivalent_atom:[equivalent_atoms]}
        for i in xrange(0, len(equivalent_atoms)):
            if not equivalent_atoms[i] in iequivalent_atoms:
                iequivalent_atoms[equivalent_atoms[i]]=[i]
            else:
                value=iequivalent_atoms[equivalent_atoms[i]]
                value.append(i)
                iequivalent_atoms[equivalent_atoms[i]]=value
        for i in iequivalent_atoms.keys():
            position=positions[i]
            position_std=raw2std_position(position, dataset['transformation_matrix'], dataset['origin_shift'])
            index_std=get_index_from_collection(position_std, dataset['std_positions'], entity_type='position')
            wyckoff_symbol.append(wyckoff[index_std])
            wyckoff_symbol_number.append(len(iequivalent_atoms[i]))
        
        site_index=iequivalent_atoms.keys()
        
        wyckoff_set=collections.OrderedDict() # wyckoff's object set {index:object}
        site_set=collections.OrderedDict() # site's object set {index:object}
        for i in xrange(0, len(wyckoff_symbol)):
            wyckoffSite=WyckoffSite().create(symbol=wyckoff_symbol[i], 
                                             multiplicity=wyckoff_symbol_number[i], 
                                             position=positions[site_index[i]], 
                                             isPersist=isPersist,
                                             spacegroup=spacegroup) # site, atom
            #wyckoff_set.append(wyckoffSite)
            wyckoff_set[iequivalent_atoms.keys()[i]]=wyckoffSite
            site=Site().create(position=positions[site_index[i]], 
                               isPersist=isPersist,
                               structure=self,
                               wyckoffSite=wyckoffSite) # atom
            #site_set.append(site)
            site_set[iequivalent_atoms.keys()[i]]=site
        self.nsites=len(self.sites) 
        for i in xrange(0, len(numbers)):
            formated_atom=[get_symbol_by_z(numbers[i])]+positions[i].tolist()
            atom=self.get_atom(formated_atom)
            wyckoff_set[equivalent_atoms[i]].add_atom(atom)
            site_set[equivalent_atoms[i]].add_atom(atom)
            if isPersist:
                wyckoff_set[equivalent_atoms[i]].atom_set.add(atom)
                site_set[equivalent_atoms[i]].atom_set.add(atom)
                wyckoff_set[equivalent_atoms[i]].save()
                site_set[equivalent_atoms[i]].save()
                atom.save()
        
    def _update_composition_info(self):
        """
        update the information related composition. Note that the method need access to element and atom information.
        
        更新结构中跟化学式相关的信息。注意该方法是依据结构中的元素和对应的原子信息来更新结构的化学式等数据。所以，在执行该方法前，需确保结构的元素和原子信息的正确性。
        """
        from django.core.cache import cache
        from jump2.db.cache.cachedCompositionProvider import CachedCompositionProvider
        from jump2.db.materials.composition import Composition
        
        # old composition
        #composition_old=self.composition
        #structures_of_composition=list(composition_old.structure_set.all())
        #if (structures_of_composition == []) or (len(structures_of_composition) == 1 and structures_of_composition[0].id == self.id):
        #    composition_cache='composition_%s' %composition_old.formula
        #    cache.expire(composition_cache, timeout=0)
        #    composition_old.delete()
        
        # composition, multiple
        elements=self.elements
        element_symbols=[]
        numbers=[]
        for element in elements:
            element_symbols.append(element.symbol)
            numbers.append(len(element.atoms))
        multi=reduce(gcd, numbers) # number of formula
                
        formula=''
        for i in xrange(0, len(element_symbols)):
            formula += element_symbols[i]+str(numbers[i]/multi)
        self.composition=CachedCompositionProvider().get(formula)
        self.composition.add_structure(self)
        self.composition.elements=self.elements
        self.multiple=multi
        self.ntypes=len(self.elements)

    def update_by_cell(self, cell, isPersist=False, **kwargs):
        """
        update structure by cell-type structure. Note that it will lost previous species information in old structure.
        
        Arguments:
            cell: cell-type structure. The valid format is:
                {'lattice':lattice,
                 'positions':positions,
                 'numbers':numbers,
                 'magmoms':magmoms(optional)}
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                        to determine whether this atom is in collection by comparing its distance 
                        from other atoms.
                        
        依据给定的‘cell’字典更新结构。注意：更新后会丢失更改过的原子的元素种类信息（‘cell’数组中没有给出原子对应的元素种类信息）。
        
        参数：
            cell:‘cell’类型的结构。其合法的形似为：
                {'lattice':lattice,
                 'positions':positions,
                 'numbers':numbers,
                 'magmoms':magmoms(optional)}
            isPersist (default=False):是否持久化，即更新数据库中对应的数据。
            
            kwargs:
                precision (default=1e-3):比较原子是否重叠的精度。当“atom”参数为格式化数组时，此参数用于判断给定的原子是否在结构中（比较给定原子坐标与结构中的原子坐标之间的距离）。
        """
        from copy import copy
        from jump2.db.utils.check import compare_with_memory
        from jump2.db.utils.fetch import get_atoms_from_cell
        
        lattice=np.array(cell['lattice'])
        positions=np.array(cell['positions'])
        numbers=np.array(cell['numbers'])
        
        if lattice.shape != (3,3):
            raise StructureError('invalid lattice in cell')
        if len(positions) != len(numbers):
            raise StructureError("don't consistent between 'positions' and 'numbers'")
        
        self.lattice=lattice
        
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
        result=compare_with_memory(get_atoms_from_cell(cell), self, dtype='atom', precision=precision)
        egas=result['collection'] # exclusive given atoms
        ebas=result['memory'] # exclusive build-in atoms
        for atom in egas:
            self.add_atom(atom, isUpdatedInfo=True, isPersist=False)
        for atom in ebas:
            self.del_atom(atom, isUpdatedInfo=True, isPersist=False)
                
        self.volume=self.calculate_volume()
        self.volume_per_atom=self.volume/self.natoms
        
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        if isPersist:
            self.update(isPersist=isPersist, symprec=symprec, angle_tolerance=angle_tolerance)

    def update(self, isPersist=False, **kwargs):
        """
        update structure by build-in atoms of structure in memory.
        
        Arguments:
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angel_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        
        根据内存中内建关系里的原子信息，更新结构。
        
        参数：
            isPersist (default=False):是否持久化，即更新数据库中对应的数据。
            
            kwargs:
                symprec (default=1e-5):找结构对称性时，采用的精度。
                angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差。
        
        """
        # composition-related information
        self._update_composition_info()
                
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']

        self._update_related_symmetry_info(symprec, angle_tolerance, isPersist=isPersist)
        
        if isPersist:
            self._persist()

    def _persist(self, **kwargs):
        """
        save to database. If data between build-in relation and database is not consistent. It will replace the database's data by build-in memory.
        
        Arguments:
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angel_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
        
        将内存中的结构保存到数据库中。注意：在保存前，会对比该结构在内存和数据库中的数据，依据内存中的结构信息，更新数据库中的数据。
        
        参数：
            kwargs:
                symprec (default=1e-5):找结构对称性时，采用的精度。
                angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差。
        """
        from jump2.db.utils.check import compare_with_db
        
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']

        self._update_related_symmetry_info(symprec, angle_tolerance, isPersist=True)
        
        # spacegroup
        spacegroup=self.spacegroup
        spacegroup.save()
        # operation
        for operation in spacegroup.operations:
            operation.save()
        for wyckoffSite in spacegroup.wyckoffSites:
            wyckoffSite.save()
        # structure
        self.save()
        # site
        for site in self.sites:
            site.save()
        result=compare_with_db(self.sites, self, 'site')
        #sims=result['memory']
        sibs=result['db']
        if not sibs is None:
            for site in sibs:
                site.delete()
            
        # atom
        for atom in self.atoms:
            atom.save()
        result=compare_with_db(self.atoms, self, 'atom')
        #aims=result['memory']
        aibs=result['db']
        if not aibs is None: 
            for atom in aibs:
                atom.wyckoffSite.delete()
                atom.delete()
             
        # structure
        # element
        for element in self.elements:
            self.element_set.add(element)
        result=compare_with_db(self.elements, self, 'element')
        #eims=result['memory']
        eibs=result['db']
        if not eibs is None:
            for element in eibs:
                self.element_set.remove(element)
        
        # species
        for species in self.species:
            self.species_set.add(species)
        result=compare_with_db(self.species, self, 'species')
        #sims=result['memory']
        sibs=result['db']
        if not sibs is None:
            for species in sibs:
                self.species_set.remove(species)
        # atom
        for atom in self.atoms:
            self.atom_set.add(atom)
            atom.site.atom_set.add(atom)
            atom.wyckoffSite.atom_set.add(atom)
            
        # site
        for site in self.sites:
            self.site_set.add(site)
            site.wyckoffSite.site_set.add(site)
        
        # site
        # atom
        for atom in site.atoms:
            site.atom_set.add(atom)
            
        # spacegroup
        for operation in spacegroup.operations:
            spacegroup.operation_set.add(operation)
        for wyckoffSite in spacegroup.wyckoffSites:
            spacegroup.wyckoffSite_set.add(wyckoffSite)


    def create(self, raw_structure, isPersist=False, **kwargs):
        """
        create a structure's object.
        Note that the type of atomic coordinate is Direct for crystal inside the jump2.
        
        Arguments:
            raw_structure: formated structure from Read method's returned dictionary.
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                isNormalizingCoordinate (default=True): whether to remove the periodic boundary condition, 
                    ensure the value of atomic coordinate is between 0 and 1 (i.e. 1.3 -> 0.3). 
                    
                isContainedConstraints (default=False): whether to write the constrain information to this structure when raw_structure contain them.
                isContainedVelocities (default=False): whether to write the velocity information to this structure when raw_structure contain them.
                   
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
                
                # ---------- composition ----------
                generic:
                
                # ---------- atom --------
                species: collection of species's name for each atom. i.e. ['Fe2+', 'Fe3+', 'Sb-',...]
        
        Returns:
            structure's object.
            
        创建结构对象。注意，在jump2数据库内部，晶体结构的原子坐标类型为“Direct”。
        
        参数：
            raw_structure:Read方法返回的结构的格式化字典数组。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                isNormalizingCoordinate (default=True):是否移除原子坐标上的平移周期性，以保证其值在0.0～1.0之间。
                isContainedConstraints (default=False):当输入的结构字典数组中包含原子束缚信息时，是否写到结构对象中。
                isContainedVelocities (default=False)
                   
                symprec (default=1e-5):找结构对称性时，采用的精度。
                angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差值。
                
                # ---------- composition ----------
                generic:化学式的一般式。
                
                # ---------- atom --------
                species: 结构中每个原子所属的元素种类。 如，['Fe2+', 'Fe3+', 'Sb-',...]。
        
        返回：
            结构对象。
        
        """
        from jump2.db.cache.cachedCompositionProvider import CachedCompositionProvider
        from jump2.db.cache.cachedSpeciesProvider import CachedSpeciesProvider
        from jump2.db.utils.convert import normalize_position
        from jump2.db.materials.prototype import Prototype
        
        if isPersist:
            self.save()
            
        element_symbols=raw_structure['elements']
        numbers=raw_structure['numbers'] # atomic number of each element
        if len(element_symbols) != len(numbers):
            raise StructureError('inconsistent between elements and numbers')
        
        # 1. composition
        multi=reduce(gcd, numbers) # number of formula
        
        formula=''
        generic=None
        if 'generic' in kwargs:
            generic=kwargs[generic]
        
        # 1. composition
        for i in xrange(0, len(element_symbols)):
            formula += element_symbols[i]+str(numbers[i]/multi)
        composition=CachedCompositionProvider().get(formula)
        self.composition=composition
        
        # 2. elements
        for element in composition.elements:
            element.atoms=[]
            self.add_element(element)
            if isPersist:
                self.element_set.add(element)

        if not generic:
            composition.generic=generic
        composition.add_structure(self) # bidirectional add
        
        # prototype
        if 'prototpye' in kwargs:
            prototype=kwargs['prototype']
            if not isinstance(prototype, Prototype):
                raise ValueError('unrecognized prototype')
            prototype.add_structure(self)
            if isPersist:
                prototype.structure_set(self)
            
        # label
        if 'label' in kwargs:
            self.label=kwargs['label']
        
        if 'comment' in raw_structure:
            self.comment=raw_structure['comment']
            
        self.ntypes=len(element_symbols)
        self.natoms=np.sum(numbers)
        
        self.lattice=raw_structure['lattice']
        self.volume=self.calculate_volume()
        self.volume_per_atom=self.volume/self.natoms
        
        self.multiple=multi
        
        # 4. atom
        # remove translation periodicity
        isNormalizingCoordinate=True
        if 'isNormalizingCoordinate' in kwargs:
            isNormalizingCoordinate=kwargs['isNormalizingCoordinate']
        
        # constrain    
        constraints=None
        if 'constraints' in raw_structure:
            constraints=raw_structure['constraints']
        isContainedConstraints=False            
        if ('isContainedConstraints' in kwargs) and kwargs['isContainedConstraints']:
            isContainedConstraints=kwargs['isContainedConstraints']
            if not isinstance(isContainedConstraints, bool):
                raise ValueError("unrecognized value of 'isContainedConstraints'")
            
        # velocity
        velocities=None
        if 'velocities' in raw_structure:
            velocities=raw_structure['velocities']
        isContainedVelocities=False
        if ('isContainedVelocities' in kwargs) and kwargs['isContainedVelocities']:
            isContainedVelocities=kwargs['isContainedVelocities']
            if not isinstance(isContainedVelocities, bool):
                raise ValueError("unrecognized value of 'isContainedVelocities'")

        raw_species=None
        if 'species' in kwargs:
            raw_species=kwargs['species']
            if len(raw_species) != self.natoms:
                raise ValueError('inconsistent dimensions between species and atoms')

        atom_index=0 # index of atom    
        for i in xrange(0, len(element_symbols)): # element
            for j in xrange(0, numbers[i]): # number of element
                position=None
                if raw_structure['type'].strip().lower().startswith('d'): # Direct
                    position=raw_structure['positions'][atom_index]
                elif raw_structure['type'].strip().lower().startswith('c'): # Cartesian'
                    position=any2cartesian(self.lattice, raw_structure['positions'][atom_index])
                else:
                    raise StructureError('unrecognized type of atomic coordinate')
                    
                # normalize atomic coordinate
                if isNormalizingCoordinate: # revome translation periodicity
                    position=normalize_position(position, 'Direct')[:3]
                
                if not raw_species is None:
                    species=self.get_species(raw_species[atom_index])
                    if species is None:
                        species=CachedSpeciesProvider().get(raw_species[atom_index])
                    atom=Atom().create(self.get_element(element_symbols[i]), position, isPersist=False, structure=self, species=species) # site, species, wyckoffSite
                    self.add_species(atom.species)
                    atom.element.add_species(atom.species)
                    if isPersist:
                        self.species_set.add(atom.species)
                else:
                    atom=Atom().create(self.get_element(element_symbols[i]), position, isPersist=False, structure=self)
                    
                if isContainedConstraints and ((not constraints is None) or constraints != []):
                    atom.constraint=constraints[atom_index]
                
                if isContainedVelocities and ((not velocities is None) or velocities != []):
                    atom.velocity=velocities[atom_index]
                
                if isPersist:
                    atom.save()
                           
                atom_index += 1

        # ox
        # force
        # magmom
        # occupancy
        # constrain
        # species
        
        # 5. spacegroup
        
        # default
        symprec=1e-5 # symprec
        angle_tolerance=-1.0 # angle_tolerance
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
            
        self._update_related_symmetry_info(symprec, angle_tolerance, isPersist=isPersist)
        
        if isPersist:
            for wyckoffSite in self.spacegroup.wyckoffSites:
                wyckoffSite.save()
            for operation in self.spacegroup.operations:
                operation.save()
            self.spacegroup.save()
            self.save()
            #for species in self.species:
            #    species.save()
            #for site in self.sites:
            #    site.save()
            #for atom in self.atoms:
            #    atom.save()
            #    atom.structure=self
            #    atom.save()
                
            # more code
            
        return self

    def standardize(self, isPersist=False, **kwargs):
        """
        convert to standardized structure. 
        Note that if not specify the hall number, always the first one (the smallest serial number corresponding to 
        the space-group-type in list of space groups (Seto’s web site)) among possible choices and settings is chosen as default.
        
        Arguments:
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                symprec (default=1e-5): precision when to find the symmetry.
                angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
                hall_number (default=0): hall number.
                
        Returns:
            standardized structure's object.
            
        将结构转化为标准结构。
        注意：如果不指定hall数，默认将始终输出该空间群对应的第一个hall符号对于的标准结构。
        
        参数：
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                symprec (default=1e-5):找结构对称性时，采用的精度。
                angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差值。
                hall_number (default=0): 该空间群对应的一个hall数。详细解释请看spglib中get_symmetry_dataset()方法的参数--hall_number的说明。
                    https://atztogo.github.io/spglib/python-spglib.html#get-symmetry-dataset
        """
        import spglib
        from jump2.db.utils.fetch import get_symbol_by_z
        from jump2.db.utils.convert import raw2std_position
        
        cell=self.formatting(dtype='cell')
        cell=(cell['lattice'], cell['positions'], cell['numbers'])
            
        symprec=1e-5
        if 'symprec' in kwargs:
            symprec=kwargs['symprec']
        angle_tolerance=-1.0
        if 'angle_tolerance' in kwargs:
            angle_tolerance=kwargs['angle_tolerance']
        hall_number=0
        if 'hall_nmber' in kwargs:
            hall_number=kwargs['hall_number']
        dataset=spglib.get_symmetry_dataset(cell, symprec=symprec, angle_tolerance=angle_tolerance, hall_number=hall_number)
        lattice_std=dataset['std_lattice']
        
        self.lattice=lattice_std
        
        for atom in self.atoms:
            position=atom.position
            atom.position=raw2std_position(position, dataset['transformation_matrix'], dataset['origin_shift'])
        
        self.update(isPersist)
        
        self.spacegroup.hall=dataset['hall']
        self.spacegroup.hm=dataset['hall_number']
        self.spacegroup.save()    
         
    def clone(self, isPersist=False, **kwargs):
        """
        clone a structure.
        
        Arguments:
            isPersist (default=False): whether to save to the database.
            
            kwrages:
                precision (default=1e-3): used to determine whether the two positions are overlapped.
                    from other atoms.
        Returns:
            cloned structure's object.
            
        复制一个结构对象。
        
        参数：
            isPersist (default=False):是否持久化，即更新数据库中对应的数据。
            
            kwargs:
                precision (default=1e-3):比较两个不等价位置是否重叠的精度。
                
        返回：
            如果克隆成功，则返回克隆的结构对象。否则，返回 None。
        """
        import warnings
        from jump2.db.cache.cachedSpeciesProvider import CachedSpeciesProvider
        
        raw_structure=self.formatting(dtype='poscar')
        structure=Structure().create(raw_structure, isPersist=isPersist)
        
        # structure
        structure.label=self.label
        structure.comment=self.comment
        for species in self.species: # species in self
            name=species.name
            species2=CachedSpeciesProvider().get(name) # species2 in cache
            structure.add_species(species2)
            if isPersist:
                structure.species_set.add(species2)
            for atom in species.atoms: # atom in self
                formated_atom=[atom.element.symbol]+atom.position
                atom=structure.get_atom(formated_atom) # atom in structure
                species2.add_atom(atom)
                if isPersist:
                    species2.atom_set.add(atom)
        # cases
        for case in self.cases:
            structure.add_case(case, isPersist=isPersist)
        # prototype
        structure.prototype=self.prototype
        if isPersist:
            structure.save()
        
        # composition
        structure.composition.generic=self.composition.generic
        if isPersist:
            structure.composition.save()
            
        # sites
        for i in xrange(0, self.nsites):
            precision=1e-3
            if 'precision' in kwargs:
                precision=kwargs['precision']
                
            distance=structure.sites[i].position-self.sites[i].position
            #if False in (structure.sites[i].position == self.sites[i].position):
            if np.linalg.norm(distance) > precision:    
                warnings.warn("site is not consistent between two structures")
                return None
            structure.sites[i].coordination_number=self.sites[i].coordination_number
            if isPersist:
                structure.sites[i].save()
        
        return structure # temporal
    
    def minimize_clone(self, isPersist=False):
        """
        clone a structure contains only the most basis information.
        
        Arguments:
            isPersist (default=False): whether to save to the database.
            
        Reurns:
            cloned structure's object.
            
        复制一个结构对象，只包含最基本的信息（化学式、元素、原子及对称性等）。注意：会丢失一些信息。如，元素种类、计算实例、结构原型等信息。
        
        参数：
            isPersist (default=False):是否持久化，即更新数据库中对应的数据。
        
        返回：
            如果克隆成功，则返回克隆的结构对象。否则，返回 None。
        """
        from copy import deepcopy as dc
        
        raw_structure=self.formatting(dtype='poscar')
        structure=Structure().create(raw_structure, isPersist=isPersist)
        
        return structure # temporal
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
     
    def destroy(self):
        """
        delete a structure from database.
        
        Arguments:
            isPersist (default=False): whether to save to the database.
            
        从数据库中删除一个结构。
        
        参数：
            isPersist (default=False):是否持久化，即更新数据库中对应的数据。
        """
        from django.core.cache import cache
        
        # composition
        composition=self.composition
        structures_of_composition=list(composition.structure_set.all())
        if len(structures_of_composition) == 1 and structures_of_composition[0].id == self.id:
            composition_cache='composition_%s' %composition.formula
            cache.expire(composition_cache, timeout=0)
            composition.delete()
        # atom
        for atom in list(self.atom_set.all()):
            atom.delete()
        # site
        for site in list(self.site_set.all()):
            site.wyckoffSite.delete()
            site.delete()
        # structure
        self.delete()
    
    
    def calculate_volume(self):
        """
        calculate the volume of this structure.
        
        Returns:
           calculated volume (float).
           
        根据结构中的晶胞参数，计算晶胞体积。
        
        返回：
            计算的晶胞体积。
        """
        lattice=self.lattice
        return np.linalg.det(lattice)
    
    @property
    def lattice_parameters(self):
        """
        lattice parameters, its format is [a, b, c, alpha, beta, gamma].
            
        晶胞参数。
        
        返回：
            晶胞参数的格式化数组 [a, b, c, alpha, beta, gamma]
        """
        a=np.linalg.norm(self.lattice[0])
        b=np.linalg.norm(self.lattice[1])
        c=np.linalg.norm(self.lattice[2])
        alpha=np.degrees(np.arccos(np.clip(np.dot(self.lattice[1]/b, self.lattice[2]/c), -1, 1)))
        beta=np.degrees(np.arccos(np.clip(np.dot(self.lattice[0]/a, self.lattice[2]/c), -1, 1)))
        gamma=np.degrees(np.arccos(np.clip(np.dot(self.lattice[0]/a, self.lattice[1]/b), -1, 1)))
        
        return np.array([a, b, c, alpha, beta, gamma])
        
    def niggli_reduce(self, eps=1e-5):
        """
        Niggli reduction.
        
        Arguments:
            eps (default=1e-5): tolerance parameter, but unlike symprec the unit is not a length.
                This is used to check if difference of norms of two basis vectors 
                is close to zero or not and if two basis vectors are orthogonal
                by the value of dot product being close to zero or not. The detail
                is shown at https://atztogo.github.io/niggli/.
        
        Returns:
            Niggli reduction.
        """
        import spglib
        
        cell=self.formatting('cell')
        lattice=cell['lattice']
        niggli_lattice=spglib.niggli_reduce(lattice, eps=eps)
        return niggli_lattice        
        
    def delaunay_reduce(self, eps=1e-5):
        """
        Delaunay reduction.
        
        Arguments:
            eps (default=1e-5): tolerance parameter, see niggliReduce.
        """
        import spglib
        
        cell=self.formatting('cell')
        lattice=cell['lattice']
        delaunay_lattice=spglib.delaunay_reduce(lattice, eps=eps)
        return delaunay_lattice        
      
    def formatting(self, dtype='poscar', **kwargs):
        """
        convert this object to a special formated object. 
        Note that the output structure is a standardized structure when dtypde is 'cif'. Perhaps, the output structure is different from the raw structure. 
        
        Arguments:
            dtype (default='poscar'): expected type. The supported type: cif, poscar, cell.
            
            kwargs:
                for 'poscar' type:
                    coordinate_type:type of atomic coordinate (Direc/Cartesian).
                    isContainedConstraints: whether to contain the constraint information of atomic coordinate. 
                        The type of value is True or False.
                    isContainedVelocities: whether to contain the atomic velocity information (False/True).
                        
                for 'cif' type:
                    symprec (default=1e-5): precision when to find the symmetry.
                    angle_tolerance (default=-1.0): a experimental argument that controls angle tolerance between basis vectors.
                    hall_number (default=0): hall number.
                    
        Returns:
            formated structure (python dictionary).
            
            for 'poscar' type:
                {'comment':comment,
                 'lattice':lattice,
                 'elements':elements,
                 'numbers':numbers,
                 'type':type,
                 'positions':positions,
                 'constraints':constraints(optional)}
                 
            for 'cif' type:
                {'data_':formula,
                 '_cell_length_a':crya,
                 '_cell_length_b':cryb,
                 '_cell_length_c':cryc,
                 '_cell_angle_alpha':alpha,
                 '_cell_angle_beta':beta,
                 '_cell_angle_gamma':gamma,
                 '_cell_volume':cellvolume,
                 '_symmetry_space_group_name_H-M':hmsyb,
                 '_symmetry_Int_Tables_number':itnum,
                 '_symmetry_equiv_pos_as_xyz':symopt,
                 '_atom_site_label':sitelab,
                 '_atom_site_wyckoff_symbol':wyc,
                 '_atom_site_fract_x':sitex,
                 '_atom_site_fract_y':sitey,
                 '_atom_site_fract_z':sitez,
                 '_atom_site_occupancy':occu}
                 
            for 'cell' type:
                {'lattice':lattice,
                 'positions':positions,
                 'numbers':numbers,
                 'magmoms':magmoms(optional)}
                 
        转换结构对象为指定类型的结构的格式化字典数组。注意：当输出结构为cif时，输出的是标准化的结构，有可能跟初始输入结构不同。
        
        参数：
            dtype (default='poscar'):将要转化为的结构类型。目前支持的格式有：cif、poscar、cell。
            
            kwargs:
                for 'poscar' types:
                    coordinate_type:格式化数组中的原子坐标类型：‘Direct’、‘Cartesian’。
                    isContainedConstraints:格式化数组中是否包含原子束缚信息（用于VASP的选择动力学）。
                
                for 'cif' type:
                    symprec (default=1e-5):找结构对称性时，采用的精度。
                    angle_tolerance (default=-1.0):找结构对称性时，控制晶胞基矢之间的角度容差。
                    hall_number (default=0): 该空间群对应的hall数。详细解释请看spglib中get_symmetry_dataset()方法的参数--hall_number的说明。
                        https://atztogo.github.io/spglib/python-spglib.html#get-symmetry-dataset
        返回：
            结构的格式化字典数组。输出的类型如下：
            
            'poscar'类型：
                {'comment':comment,
                 'lattice':lattice,
                 'elements':elements,
                 'numbers':numbers,
                 'type':type,
                 'positions':positions,
                 'constraints':constraints(optional)}
            'cif'类型：
                {'data_':formula,
                 '_cell_length_a':crya,
                 '_cell_length_b':cryb,
                 '_cell_length_c':cryc,
                 '_cell_angle_alpha':alpha,
                 '_cell_angle_beta':beta,
                 '_cell_angle_gamma':gamma,
                 '_cell_volume':cellvolume,
                 '_symmetry_space_group_name_H-M':hmsyb,
                 '_symmetry_Int_Tables_number':itnum,
                 '_symmetry_equiv_pos_as_xyz':symopt,
                 '_atom_site_label':sitelab,
                 '_atom_site_wyckoff_symbol':wyc,
                 '_atom_site_fract_x':sitex,
                 '_atom_site_fract_y':sitey,
                 '_atom_site_fract_z':sitez,
                 '_atom_site_occupancy':occu}
            'cell'类型：
                {'lattice':lattice,
                 'positions':positions,
                 'numbers':numbers,
                 'magmoms':magmoms(optional)}
        """
        from copy import deepcopy
        from jump2.db.iostream.cif import format_symbol
        from jump2.db.iostream.spaceGroupD3 import spacegroups as sgd
        from jump2.db.iostream.hall2hm import hl2hm as hm
        
        if dtype.strip().lower() == 'poscar':
            comment=self.comment
            lattice=deepcopy(self.lattice)
            
            coordinate_type='Direct'
            if 'coordinate_type' in kwargs:
                if kwargs['coordinate_type'].strip().lower().startswith('c'):
                    coordinate_type='Cartesian'
                elif kwargs['coordinate_type'].strip().lower().startswith('d'):
                    coordinate_type='Direct'
                else:
                    raise StructureError("unrecognized type of atomic coordinate (Direct/Cartesian)")
                
            # elements, numbers, position, constrain (optional) and velocities (optional)
            elements=[]
            numbers=[]
            positions=[]
            constraints=[]
            velocities=[]
            for i in xrange(0, len(self.elements)):
                elements.append(self.elements[i].symbol)
                numbers.append(len(self.elements[i].atoms)) # need to check carefully
                for j in xrange(0, numbers[i]):
                    if coordinate_type == 'Direct':
                        positions.append(self.elements[i].atoms[j].position)
                    elif coordinate_type == 'Cartesian':
                        positions.append(any2cartesian(self.lattice, self.elements[i].atoms[j].position))
                        
                    if ('isContainedConstraints' in kwargs) and kwargs['isContainedConstraints']:
                        constraints.append(self.elements[i].atoms[j].contraint)
                    if ('isContainedVelocities' in kwargs) and kwargs['isContainedVelocities']:
                        velocities.append(self.elements[i].atoms[j].velocity)
            elements=np.array(elements)
            numbers=np.array(numbers)
            positions=np.array(positions) 
            constraints=np.array(constraints)
            velocities=np.array(velocities)
     
            poscar={'comment':comment,
                    'lattice':lattice,
                    'elements':elements,
                    'numbers':numbers,
                    'type':coordinate_type,
                    'positions':positions,
                    'constraints':constraints}
            
            if ('isContainedVelocities' in kwargs) and kwargs['isContainedVelocities'] and (velocities != []):
                poscar['velocities']=velocities
                
            return poscar
        
        elif dtype.strip().lower() == 'cif':
            symprec=1e-5
            if 'symprec' in kwargs:
                symprec=kwargs['symprec']
            angle_tolerance=-1.0
            if 'angle_tolerance' in kwargs:
                angle_tolerance=kwargs['angle_tolerance']
            hall_number=0
            if 'hall_nmber' in kwargs:
                hall_number=kwargs['hall_number']
            
            structure=self.minimize_clone(isPersist=False)
            structure.standardize(isPersist=False, symprec=symprec, angle_tolerance=angle_tolerance, hall_number=hall_number)
            
            lattice=structure.lattice
            lattice_parameters=structure.lattice_parameters
            
            # positions, elements, wyckoff and occupancy
            positions=[]
            elements=[]
            wyckoff=[]
            occupancys=[]
            sites=structure.sites
            for site in sites:
                positions.append(site.position)
                wyckoff.append(site.wyckoffSite.symbol)
                elements.append(site.atoms[0].element.symbol)
                occupancys.append(site.atoms[0].occupancy)
                
            # formula
            formula=structure.composition.formula
            
            # spacegroup
            number=str(structure.spacegroup.number)
            equiv=sgd[number]
            hall=structure.spacegroup.hall
            H_M=hm[hall]
            if hall is None:
                equiv=sgd[number]
            else:
                equiv=sgd[format_symbol(hm[hall])]
            # volume
            cellvolume=structure.volume

            elements=np.array(elements)
            wyckoff=np.array(wyckoff)
            positions=np.array(positions)
            occupancys=np.array(occupancys)

            cif={'data_':formula,
                  '_cell_length_a':lattice_parameters[0],
                  '_cell_length_b':lattice_parameters[1],
                  '_cell_length_c':lattice_parameters[2],
                  '_cell_angle_alpha':lattice_parameters[3],
                  '_cell_angle_beta':lattice_parameters[4],
                  '_cell_angle_gamma':lattice_parameters[5],
                  '_cell_volume':cellvolume,
                  '_symmetry_space_group_name_H-M':H_M,
                  '_symmetry_Int_Tables_number':number,
                  '_symmetry_equiv_pos_as_xyz':equiv,
                  '_atom_site_label':elements,
                  '_atom_site_wyckoff_symbol':wyckoff,
                  '_atom_site_fract':positions,
                  '_atom_site_occupancy':occupancys}
            return cif
        
        elif dtype.strip().lower() == 'cell':
            numbers=[]
            positions=[]
            for i in xrange(0, len(self.elements)):
                for j in xrange(0, len(self.elements[i].atoms)):
                    numbers.append(self.elements[i].z)
                    positions.append(self.elements[i].atoms[j].position)
            
            numbers=np.array(numbers)
            positions=np.array(positions)
            
            cell={'lattice':self.lattice,
                  'positions':positions,
                  'numbers':numbers}
            return cell
        
        else:
            raise ValueError("unrecognized type in 'dtype'")
    
    
    def coordinateByIndex(self, symbol_of_element, index_of_atom, direction, removeRepetive=True):
        """
        get the coordinate of given element along special direction.
        
        Arguments:
            symbol_of_element:
            index_of_atom: in order of smallest to largest
            direction: direction of 
        """
        atoms=sorted(self.get_element(symbol_of_element).atoms, key=lambda atom: atom.position[direction])
        distances=[]
        for atom in atoms:
            distances.append(atom.position[direction])
        if removeRepetive:
            distances=sorted(set(distances))
        return distances[index_of_atom]
    
    
    