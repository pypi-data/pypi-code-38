#coding=utf-8
'''
Created on Oct 24, 2017

@author: fu
'''
from __future__ import unicode_literals
from django.db import models

from jump2.db.utils.customField import NumpyArrayField

class MolAtomError(Exception):
    pass

class MolAtom(models.Model):
    """
    Molecular Atom.
    
    Relationships:
        atom
            |- structure
            |- element
            
    Attributes:
        atom
            |- structure
            |- element
            |- position
            |- magmom
            |- charge
            |- volume
            |- ox
            
    分子的原子类。
    
    关系:
        atom
            |- structure
            |- element
            
    属性:
        atom
            |- structure
            |- element
            |- position
            |- magmom
            |- charge
            |- volume
            |- ox
    """
    # relationship
    structure=models.ForeignKey('MolStructure', null=True)
    element=models.ForeignKey('MolElement', null=True)
    
    position=NumpyArrayField(blank=True, null=True)
    
    magmom=models.FloatField(blank=True, null=True)
    charge=models.FloatField(blank=True, null=True) # effective charge
    volume=models.FloatField(blank=True, null=True) # atomic volume
    
    ox=models.IntegerField(blank=True, null=True) # oxidation state
    
    class Meta:
        app_label='materials'
        db_table='molAtom'
        default_related_name='atom_set'
    
    def __str__(self):
        if self.position is None:
            return '%s: [None, None, None]' %self.element.symbol
        else:
            return '%s [%f, %f, %f]' %(self.element.symbol, self.position[0], self.position[1], self.position[2])
    
    def create(self, element, position, isPersist, **kwargs):
        """
        create a atom object.
        
        Arguments:
            element: element's symbol of this atom. i.e. Na
            position: atomic position.
            isPersit: if True, save to database. Conversely, only run in memory.
            
            kwargs:
                structure:
                
                ox:
                magmom:
                charge:
                volume:
                
        Returns:
            atom's object.
            
        创建一个原子对象。
        
        参数：
            element:原子的元素符号。如，Na。
            position:原子位置。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                structure:原子所属的结构对象。
                
                ox:原子的氧化态。
                magmom:原子的磁矩。
                charge:原子所带电荷。
                volume:原子体积。
                
        返回：
            原子对象。
        """
        from jump2.db.cache.cachedMolElementProvider import CachedMolElementProvider
        from jump2.db.materials.molStructure import MolStructure
        from jump2.db.materials.molElement import MolElement
        
        if isPersist:
            self.save()
        
        if isinstance(element, basestring):
            symbol=element
            element=CachedMolElementProvider().get(symbol)
        elif not isinstance(element, MolElement):
            raise  ValueError('unrecognized element')
        element.add_atom(self)
        self.position=position
        
        if 'ox' in kwargs:
            ox=kwargs['ox']
            self.ox=ox        
        if 'magmom' in kwargs:
            magmom=kwargs['magmom']
            self.magmom=magmom
        if 'charge' in kwargs:
            charge=kwargs['charge']
            self.charge=charge
        if 'volume' in kwargs:
            volume=kwargs['volume']
            self.volume=volume
            
        if 'structure' in kwargs:
            structure=kwargs['structure']
            if not isinstance(structure, MolStructure):
                raise ValueError('unrecognized structure')
            structure.add_atom(self, isPersist=isPersist)
            
        if isPersist:
            self.save()
                
        return self
    