#coding=utf-8
'''
Created on Oct 21, 2017

@author: Yuhao Fu
'''
from __future__ import unicode_literals
from django.db import models


class Prototype(models.Model):
    """
    prototype.
    
    Relationships:
        prototype
            |- structure
            |- composition
                
    Attributes:
        prototype
            |- composition: composition of prototype.
            |- structure_of_prototype: structure of prototype.
            |- name: name of prototype.
            # ---------- database ----------
            |- structure_set: collection of structures belong to the prototype.
            # ---------- build-in ----------
            |- structures: collection of structures belong to the prototype.
            
    结构原型类。
    
    关系：
        prototype
                |- structure
                |- composition
                
    属性:
        prototype
            |- composition:结构原型的化学式。
            |- structure_of_prototype:结构原型对应的结构。
            |- name: 结构原型的名称。
            # ---------- database ----------
            |- structure_set:属于该结构原型的结构对象集合。
            # ---------- build-in ----------
            |- structures:属于该结构原型的结构对象集合。
    """
    # relationships
    composition=models.ForeignKey('Composition', blank=True, null=True)
    structure_of_prototype=models.ForeignKey('Structure', blank=True, null=True, related_name='+')
    #structure_of_prototype=models.ForeignKey('Structure', blank=True, null=True)
    
    name=models.CharField(max_length=80, primary_key=True)
    
    class Meta:
        app_label='materials'
        db_table='prototype'
        #default_related_name='prototype_set'
        
    def __str__(self):
        if not self.composition is None:
            return '%s - %s' %(self.name, self.composition)
        else:
            return self.name
        
    _structures=None
    @property
    def structures(self):
        """
        structures belong to the prototype.
        
        属于该结构原型的结构。
        """
        if self._structures is None:
            if not Prototype.objects.filter(name=self.name).exists():
                self._structures=[]
            else:
                self._structures=list(self.structure_set.all())
        return self._structures
    @structures.setter
    def structures(self, structures):
        """
        assign the value. Note that it will cover the previous value.
        
        Arguments:
            structures: collection of strucutre's object.
            
        Returns:
            True if the assignment is successful. Conversely, False.
            
        ’structures‘属性的set方法。注意：该方法将会清除以前的数据。
        
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
        add a structure to this prototype.
        
        Arguments:
            structure: structure's object.
            
        Returns:
            True if add a atom successfully. Conversely, False.
            
        添加一个结构到结构原型对象的属性数组（structures）中。
        
        参数：
            structure:结构对象。
            
        返回：
            布尔值（True/False）。
        """
        from jump2.db.utils.check import exist
        
        if not exist(structure, self.structures, 'structure'):
            self.structures.append(structure)
            structure.prototype=self
            return True
        else:
            return False
        
    def create(self, name, isPersist=False, **kwargs):
        """
        create prototype's object.
        
        Arguments:
            name: name of prototype.
            isPersist (default=False): whether to save to the database.
            
            kwargs:
                formula_of_composition: composition's formula  of prototype.
                structure_of_prototype: structure of prototype.
                structures: collection of structure's object, which belong to this prototype.
        
        Returns:
            prototype's object.
            
        创建结构原型对象。
        
        参数：
            name:结构原型的名称。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                formula_of_composition:结构原型的化学式。
                structure_of_prototype:结构原型对应的结构。
                structures:属于该结构原型的结构对象集合。
                
        返回：
            结构原型对象。
        """
        from jump2.db.cache.cachedCompositionProvider import CachedCompositionProvider
        from jump2.db.materials.structure import Structure
        
        self.name=name
        
        structure_of_prototype=None
        if 'structure_of_prototype' in kwargs:
            structure_of_prototype=kwargs['structure_of_prototype']
            if isinstance(structure_of_prototype, Structure):
                self.structure_of_prototype=structure_of_prototype
            else:
                raise ValueError("structure_of_prototype is not a structure's object")
        
        formula_of_composition=None
        if 'formula_of_composition' in kwargs:
            formula_of_composition=kwargs['formula_of_composition']
            formula=formula_of_composition
            if not structure_of_prototype is None:
                if structure_of_prototype.composition.formula != formula:
                    raise ValueError("don't consistent between 'structure_of_prototype' and 'formula_of_composition'")
            self.composition=CachedCompositionProvider().get(formula)
        
        if 'structures' in kwargs:
            structures=kwargs['structures']
            for structure in structures:
                if isinstance(structure, Structure):
                    self.add_structure(structure)
        
        if isPersist:
            self.save()
                
        return self
        
        
            
        