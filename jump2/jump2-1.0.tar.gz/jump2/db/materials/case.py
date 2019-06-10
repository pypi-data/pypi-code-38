#coding=utf-8
'''
Created on Oct 20, 2017

@author: Yuhao Fu
'''
from __future__ import unicode_literals
from django.db import models

from jump2.db.utils.customField import DictField

class Case(models.Model, object):
    """
    case of calculation.
    
    Relationships:
        case
            |- structure
                
    Attributes:
        case
            |- structure: calculated structure in case.
            |- name: name of case. 
            |- calculated_parameters: calculated parameters in case.
            # ---------- properties ----------
            |- energy: calculated energy of structure in case.
            |- energy_per_formula: calculated energy per formula for the structure in case.
            |- energy_per_atom: calculated energy per atom for the structure in case.
            |- pressure: pressure of output in calculation.
            |- bandgap: calculated bandgap for the structure.
            |- bandgap_img: bandgap image.
            |- electron_mass: effective mass of electron ({'vbm':vbm, 'cbm':cbm}).
            |- hole_mass: effective mass of hole ({'vbm':vbm, 'cbm':cbm}).
            
    计算实例类，保存整个计算过程中的所有信息，包括：计算参数、结构、计算的性质，等。
    
    关系：
        case
            |- structure
            
    属性:
        case
            |- structure:计算的结构。
            |- name:计算实例的名称。
            |- calculated_parameters:计算实例中使用的计算参数。
            # ---------- properties ----------
            |- energy:计算的能量。
            |- energy_per_formula:计算的每分子式能量。
            |- energy_per_atom:计算的每原子能量。
            |- pressure:输出的结构压力。
            |- bandgap:计算的带隙。
            |- bandgap_img:计算的能带图。
            |- electron_mass:电子的有效质量 ({'vbm':vbm, 'cbm':cbm})。
            |- hole_mass:空穴的有效质量 ({'vbm':vbm, 'cbm':cbm})。
    """
    # relationship
    structure=models.ForeignKey('Structure', null=True)
    
    name=models.CharField(primary_key=True, max_length=255) # name of case
    
    calculated_parameters=DictField(blank=True, null=True)
    
    # properties
    energy=models.FloatField(blank=True, null=True)
    energy_per_formula=models.FloatField(blank=True, null=True)
    energy_per_atom=models.FloatField(blank=True, null=True)
    
    pressure=models.FloatField(blank=True, null=True)
    
    # property
    bandgap=models.FloatField(blank=True, null=True)
    bandgap_img=models.ImageField(blank=True, null=True)
    electron_mass=DictField(blank=True, null=True) # {'vbm':vbm, 'cbm':cbm}
    hole_mass=DictField(blank=True, null=True) # {'vbm':vbm, 'cbm':cbm}
    
    class Meta:
        app_label='materials'
        db_table='case'
        default_related_name='case_set'
        
    def __str__(self):
        return self.name
    
    def create(self, name, isPersist, **kwargs):
        """
        create case's object.
        
        Arguments:
            name: name of case.
            isPersist: if True, save to database. Conversely, only run in memory.
            
            kwargs:
                structure: structure's object.
        
        Returns:
            case's object.
        
        创建实例对象。
        
        参数：
            name:实例的名称。
            isPersist:是否持久化，即更新数据库中对应的数据。
            
            kwargs:
                structure:结构对象。
                
        返回：
            实例对象。
        """
        from jump2.db.materials.structure import Structure
        
        self.name=name
        
        if 'structure' in kwargs:
            structure=kwargs['structure']
            if isinstance(structure, Structure):
                self.structure=structure
                
        if isPersist:
            self.save()
                
        return self
    
    
    