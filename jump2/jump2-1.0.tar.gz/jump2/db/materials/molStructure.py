#coding=utf-8
'''
Created on Oct 24, 2017

@author: fu
'''
from __future__ import unicode_literals
from django.db import models

from fractions import gcd
from itertools import groupby
import numpy as np

from jump2.db.materials.molElement import MolElement
from jump2.db.materials.molAtom import MolAtom

class MolStructureError(Exception):
    pass
    
    
class MolStructure(models.Model, object):
    '''
    molecular structure.
    
    Note that:
        coordinate type of atomic positions can only be 'Cartesian' for molecule inside the jump2.
        
    Relationships:
        structure
            |- composition
            |- element
            |- atom
            
    Attributes:
        structure
            |- composition
            |- label
            |- natoms
            |- ntypes
            |- volume
            |- volume_per_atom
            # ---------- database ----------
            |- element_set
            |- atom_set
            # ---------- build-in ----------
            |- elements
            |- atoms
        
    分子结构类。

    关系:
        structure
            |- composition
            |- element
            |- atom
            
    属性:
        structure
            |- composition
            |- label
            |- natoms
            |- ntypes
            |- volume
            |- volume_per_atom
            # ---------- database ----------
            |- element_set
            |- atom_set
            # ---------- build-in ----------
            |- elements
            |- atoms
    '''
    # relationship
    composition=models.ForeignKey('MolComposition', null=True)
    element_set=models.ManyToManyField('MolElement')
    
    label=models.CharField(null=True, blank=True, max_length=80)
    
    natoms=models.IntegerField(blank=True, null=True)
    ntypes=models.IntegerField(blank=True, null=True)
    
    volume=models.FloatField(blank=True, null=True)
    volume_per_atom=models.FloatField(blank=True, null=True)
    
    class Meta:
        app_label='materials'
        db_table='molStructure'
        default_related_name='structure_set'
        
    def __str__(self):
        return self.composition.formula

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
    def del_element(self, index_or_element, isUpdatedInfo=False, isPersist=False):
        """
        delete a element from this structure. Note that it will delete this element's object from other related classes's objects.
        
        Arguments:
            index_or_element: element's index, symbol or object.
            isUpdatedInfo (default=False): whether to update the composition and symmetry information (include the site, operation, wyckoffSite, spacegroup). 
            isPersist (default=False): whether to save to the database.
        
        从结构中删除一个元素。注意：当删除元素时，处于效率的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
        程序默认不会更新结构（更新化学式，等）。
        
        参数：
            index_or_element:其值可以是元素在结构的元素属性数组中的索引（index）、元素符号或元素对象。
            isUpdatedInfo (default=False): 是否更新与结构的数据信息（比如，化学式和对称信息，等）。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
        返回：
            布尔值（True/False）。
        """
        import warnings
        
        element=None
        if isinstance(index_or_element, int):
            index=index_or_element
            if index < 0 or index > self.ntypes:
                warnings.warn('beyond the range of elementary index')
                return False
            element=self.elements[index]
        elif isinstance(index_or_element, basestring):
            symbol=index_or_element
            element=self.get_element(symbol)
            if element is None:
                warnings.warn("can't find out this %s in the structure" % symbol)
                return False
        elif isinstance(index_or_element, MolElement):
            element=index_or_element
            if not element in self.elements:
                warnings.warn("this element isn't in this structure")
                return False
        else:
            warnings.warn('unrecognized index_or_element')
            return False
        
        # delete all atoms of this element
        for atom in list(element.atoms):
            self.del_atom(atom, isUpdatedInfo=isUpdatedInfo, isPersist=isPersist)    
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
    def add_atom(self, atom, isUpdatedInfo=False, isPersist=False):
        """
        add a atom to this structure.
        Arguments:
            atom: atom's object or formated string. you must specify the type. The valid formation: ['Na', 2.3, 1.4, 0.0, 'Cartesian']
            isUpdatedInfo (default=False): whether to update the composition. 
            isPersist (default=False): whether to save to the database.

        Returns:
            True if add a atom successfully. Conversely, False.
            
        添加一个原子到结构对象的属性数组（atoms）中。
        
        参数：
            atom:参数的值可以是原子的格式化数组或原子对象。注意：必须指定原子坐标类型（‘Cartesian’），其合法的格式为: ['Na', 5.234, 0.0, 0.0, 'Cartesian']。
            isUpdatedInfo (default=False): 是否更新结构的其他关联数据信息（如，化学式、不等价位置，等）。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
        
        返回：
            布尔值（True/False）。
        """
        import warnings
        from jump2.db.utils.check import exist, check_formated_atom_only_cartesian
        from jump2.db.cache.cachedMolCompositionProvider import CachedMolCompositionProvider
        from jump2.db.cache.cachedMolElementProvider import CachedMolElementProvider
        
        if not exist(atom, self.atoms, 'atom'):
            if isinstance(atom, MolAtom):
                #if not atom.element in self.elements:
                if self.get_element(atom.element.symbol) is None:
                    self.add_element(atom.element)
                    if isPersist:
                        self.element_set.add(atom.element)
                elif not atom.element in self.elements:
                    warnings.warn("element's object of given atom isn't in this structure, but have the same element's symbol")
                    return False
                self.atoms.append(atom)
                atom.structure=self
            elif check_formated_atom_only_cartesian(atom):
                formated_atom=atom
                if len(formated_atom) == 5 and formated_atom[-1].strip().lower().startswith('c'): # Cartesian
                    formated_atom=formated_atom[:4]
                
                symbol_of_element=formated_atom[0]
                element=self.get_element(symbol_of_element)
                position=formated_atom[1:]
                    
                if element is None:
                    element=CachedMolElementProvider().get(symbol_of_element)
                    atom=MolAtom().create(element, position, isPersist=False, structure=self)
                    self.ntypes=len(self.elements)
                else:
                    atom=MolAtom().create(element, position, isPersist=False, structure=self)
            # atom
            self.natoms=len(self.atoms)
            
        if isPersist:
            self.update(isPersist=isPersist)
        elif isUpdatedInfo and not isPersist:
            self.update(isPersist=False)
                    
            return True
        else:
            return False
    def get_atom(self, formated_atom, **kwargs):
        """
        get a atom by formated atomic list.
        
        Arguments:
            formated_atom: formated atom. Note that type of coordinate is only 'Cartesian',  you must specify the type. The valid formation: ['Na', 2.3, 1.4, 0.0, 'Cartesian']

            kwargs:
                precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                        to determine whether this atom is in collection by comparing its distance from other atoms.
        Returns:
            atom's object if exist. Conversely, return None.
            
        从结构中获得给定的原子对象。
        
        参数：
            formated_atom:原子的格式化数组。注意：必须指定原子坐标类型（‘Cartesian’），其合法的格式为: ['Na', 5.234, 0.0, 0.0, 'Cartesian']。
                
                kwargs：
                    isNormalizingCoordinate (default=True):当给定原子的类型为格式化数组时，默认移除原子坐标上的平移周期性，以保证其值在0.0～1.0之间。
                    precision (default=1e-3):比较原子是否重叠的精度。当“atom”参数为格式化数组时，此参数用于判断给定的原子是否在结构中（比较给定原子坐标与结构中的原子坐标之间的距离）。
        
        返回：
            如果结构中存在该原子，返回原子对象。否则，返回 None。
        """
        from jump2.db.utils.check import check_formated_atom_only_cartesian
        from jump2.db.utils.fetch import get_entity_from_collection4molecule
        
        precision=1e-3
        if 'precision' in kwargs:
            precision=kwargs['precision']
        
        if check_formated_atom_only_cartesian(formated_atom):
            return get_entity_from_collection4molecule(formated_atom, self.atoms, 'atom', precision=precision)
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
                precision (default=1e-3): used to determine whether the two atoms are overlapped. Note that, 
                        to determine whether this atom is in collection by comparing its distance 
                        from other atoms.
            
        Returns:
            True if delete a atom successfully. Conversely, False.
            
        从结构中删除一个原子。注意：当删除原子时，基于程序效率上的考虑（可能会多次对结构进行操作，可以在所有的操作完成后，更新内存中内建的结构关联信息以及同步数据库中的数据），
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
        
        atom=None
        if isinstance(index_or_atom, int):
            index=index_or_atom
            if index < 0 or index > self.natoms:
                warnings.warn('beyond the range of atomic index')
                return False
            atom=self.atoms[index]
        elif isinstance(index_or_atom, MolAtom):
            atom=index_or_atom
            if not atom in self.atoms:
                warnings.warn("atom doesn't belong to this structure")
                return False
        elif check_formated_atom_only_cartesian(index_or_atom):
            formated_atom=index_or_atom
            if len(formated_atom) == 5 and formated_atom[-1].strip().lower().startswith('c'): # Cartesian
                formated_atom=formated_atom[:4]
                
            symbol_of_element=formated_atom[0]
            position=np.array(formated_atom[1:])
                
            precision=1e-3
            if 'precision' in kwargs:
                precision=kwargs['precision']
            for atom0 in self.atoms:
                if (atom0.element.symbol == symbol_of_element) and (np.linalg.norm(atom0.position-position) <= precision):
                    atom=atom0
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
            
        # element
        element=atom.element
        element.atoms.remove(atom)
        if element.atoms == []:
            # structure
            structure.elements.remove(element)
                
        if isPersist:
            self.update(isPersist=isPersist)
        elif isUpdatedInfo and not isPersist:
            self.update(isPersist=False)        
        return True
  
    def _update_composition_info(self):
        """
        update the information related composition. Note that the method need access to element and atom information.
        
        更新化学式相关信息。注意：该方法需要访问结构中的元素和原子信息，来更新数据。
        """
        from jump2.db.cache.cachedMolCompositionProvider import CachedMolCompositionProvider
        
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
        self.composition=CachedMolCompositionProvider().get(formula)
        self.composition.add_strucutre(self)
        self.composition.elements=self.elements
        self.multiple=multi
        self.ntypes=len(self.elements)
    
    def update(self, isPersist=False):
        """
        update structure by build-in atoms of structure in memory.
        
        Arguments:
            isPersist (default=False): whether to save to the database.
        
        根据结构中的原子（内建关系），更新结构信息。
        
        参数：
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
        """
        # composition-related information
        self._update_composition_info()
        if isPersist:
            self._persist()
    
    def _persist(self):
        """
        save to database. If data between build-in relation and database is not consistent. It will replace the database's data by build-in memory.
        
        将内存中的结构保存到数据库中。注意：在保存前，会对比该结构在内存和数据库中的数据，依据内存中的结构信息，更新数据库中的数据。
        """
        from jump2.db.utils.check import compare_with_db
        
        # structure
        self.save()
            
        # atom
        for atom in self.atoms:
            atom.save()
        result=compare_with_db(self.atoms, self, 'atom')
        #aims=result['memory']
        aibs=result['db']
        if not aibs is None: 
            for atom in aibs:
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

        # atom
        for atom in self.atoms:
            self.atom_set.add(atom)
 
                    
    def create(self, raw_structure, isPersist=False, **kwargs):
        """
        create a structure's object.
        Note that the type of atomic coordinate is Cartesian for molecule inside the jump2.
        
        Arguments:
            raw_structure: formated structure from Read method's returned dictionary.
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                # ---------- composition ----------
                generic:
                
        Returns:
            structure's object.
            
        创建一个分子结构对象。注意：在Jump2内部，分子结构中的原子坐标必须时‘Cartesian’类型。
        
        参数：
            raw_structure:Read方法返回的结构的格式化字典数组。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                # ---------- composition ----------
                generic:
        
        返回：
            结构对象。
        """
        from jump2.db.cache.cachedMolCompositionProvider import CachedMolCompositionProvider
        
        if isPersist:
            self.save()
            
        element_symbols=raw_structure['elements']
        numbers=raw_structure['numbers'] # atomic number of each element
        if len(element_symbols) != len(numbers):
            raise MolStructureError('inconsistent between elements and numbers')
        
        # 1. composition
        
        formula=''
        generic=None
        if 'generic' in kwargs:
            generic=kwargs[generic]
        
        # 1. composition
        for i in xrange(0, len(element_symbols)):
            formula += element_symbols[i]+str(numbers[i])
        composition=CachedMolCompositionProvider().get(formula)
        self.composition=composition
        
        # 2. elements
        for element in composition.elements:
            element.atoms=[]
            self.add_element(element)
            if isPersist:
                self.element_set.add(element)

        if not generic:
            composition.generic=generic
        composition.add_strucutre(self) # bidirectional add
        
            
        # label
        if 'label' in kwargs:
            self.label=kwargs['label']
            
        self.ntypes=len(element_symbols)
        self.natoms=np.sum(numbers)
        
        # volume & volume_per_atom
        #self.volume=None
        #self.volume_per_atom=self.volume/self.natoms
        
        # 4. atom
        atom_index=0 # index of atom    
        for i in xrange(0, len(element_symbols)): # element
            for j in xrange(0, numbers[i]): # number of element
                position=raw_structure['positions'][atom_index]
                atom=MolAtom().create(self.get_element(element_symbols[i]), position, isPersist=False, structure=self)
                
                if isPersist:
                    atom.save()
                           
                atom_index += 1

        # ox
        # magmom
        
        if isPersist:
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
    

    
    