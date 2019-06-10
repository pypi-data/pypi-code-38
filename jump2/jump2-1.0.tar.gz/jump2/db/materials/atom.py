#coding=utf-8
'''
Created on Oct 21, 2017

@author: Yuhao Fu
'''
from __future__ import unicode_literals
from django.db import models

from jump2.db.utils.customField import NumpyArrayField


class Atom(models.Model, object):
    """
    atom.
    
    Relationships:
        atom
            |- structure
            |- element
            |- species
            |- site
            |- wyckoffSite
            
    Attributes:
        atom
            |- structure
            |- site
            |- element
            |- species
            |- ox
            |- position
            |- force
            |- velocity
            |- constraint
            |- magmom
            |- charge
            |- volume
            |- occupancy
            |- wyckoffSite
    
    原子类。
    
    关系:
        atom
            |- structure
            |- element
            |- species
            |- site
            |- wyckoffSite
            
    属性:
        atom
            |- structure
            |- site
            |- element
            |- species
            |- ox
            |- position
            |- force
            |- velocity (Angstrom/fs)
            |- constraint
            |- magmom
            |- charge
            |- volume
            |- occupancy
            |- wyckoffSite        
    """
    
    structure=models.ForeignKey('Structure', null=True)
    site=models.ForeignKey('Site', null=True)
    element=models.ForeignKey('Element', null=True)
    species=models.ForeignKey('Species', null=True)
    
    ox=models.IntegerField(blank=True, null=True)
    
    position=NumpyArrayField(blank=True, null=True) # [3, 3] (float)
    force=NumpyArrayField(blank=True, null=True) # [3, 3] (float)
    velocity=NumpyArrayField(blank=True, null=True) # [3, 3] (float)
    
    constraint=NumpyArrayField(blank=True, null=True) # [3, 3] (boolean)
    
    magmom=models.FloatField(blank=True, null=True)
    charge=models.FloatField(blank=True, null=True) # effective charge
    volume=models.FloatField(blank=True, null=True) # atomic volume
    
    # symmetry
    occupancy=models.FloatField(default=1) # value is from 0 to 1.
    wyckoffSite=models.ForeignKey('WyckoffSite', blank=True, null=True)
    
    class Meta:
        app_label='materials'
        db_table='atom'
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
                site:
                
                species: species's name. i.e. Fe2+
                ox:
                velocity:
                force:
                constraint:
                magmom:
                charge:
                volume:
                occupancy:
                wyckoffSite:
                
        Returns:
            atom's object.
                
        创建一个原子对象。
        
        参数：
            element:原子的元素符号。如，Na。
            position:原子位置。
            isPersist (default=False):是否持久化，即将结构保存到数据库中。
            
            kwargs:
                structure:原子所属的结构对象。
                site:原子所属的不等价位置。
                
                species: 原子的元素种类名称。如，Fe2+。
                ox:原子的氧化态。
                force:原子受力。
                constraint:选择动力学中，原子的束缚信息。
                magmom:原子的磁矩。
                charge:原子所带电荷。
                volume:原子体积。
                occupancy:原子在晶体结构中的所在位点的百分比。
                wyckoffSite:原子的wyckoff位置。
                
        返回：
            原子对象。
        """
        from jump2.db.cache.cachedElementProvider import CachedElementProvider
        from jump2.db.cache.cachedSpeciesProvider import CachedSpeciesProvider
        from jump2.db.materials.structure import Structure
        from jump2.db.materials.element import Element
        from jump2.db.materials.species import Species
        from jump2.db.materials.site import Site
        
        if isPersist:
            self.save()
        
        if isinstance(element, basestring):
            symbol=element
            element=CachedElementProvider().get(symbol)
        elif not isinstance(element, Element):
            raise  ValueError('unrecognized element')
        element.add_atom(self)
        self.position=position
        
        if 'ox' in kwargs:
            ox=kwargs['ox']
            self.ox=ox
        if 'velocity' in kwargs:
            velocity=kwargs['velocity']
            self.velocity=velocity        
        if 'force' in kwargs:
            force=kwargs['force']
            self.force=force
        if 'constraint' in kwargs:
            constraint=kwargs['constraint']
            self.constraint=constraint
        if 'magmom' in kwargs:
            magmom=kwargs['magmom']
            self.magmom=magmom
        if 'charge' in kwargs:
            charge=kwargs['charge']
            self.charge=charge
        if 'volume' in kwargs:
            volume=kwargs['volume']
            self.volume=volume
        if 'occupancy' in kwargs:
            occupancy=kwargs['occupancy']
            self.occupancy=occupancy
        if 'wyckoffSit' in kwargs:
            wyckoffSite=kwargs['wyckoffSite']
            self.wyckoffSite=wyckoffSite
            
        if 'structure' in kwargs:
            structure=kwargs['structure']
            if not isinstance(structure, Structure):
                raise ValueError('unrecognized structure')
            structure.add_atom(self, isPersist=isPersist)
        if 'site' in kwargs:
            site=kwargs['site']
            if not isinstance(site, Site):
                raise ValueError('unrecognized site')
            site.add_atom(self)
        if 'species' in kwargs:
            species=kwargs['species']
            if isinstance(species, basestring):
                name_of_species=species
                species=CachedSpeciesProvider().get(name_of_species)
            elif not isinstance(species, Species):
                raise ValueError('unrecognized species')
            species.add_atom(self)
            
        if isPersist:
            self.save()
                
        return self
    
    def to_formated(self, dtype='Direct'):
        """
        convert to formated-type. i.e. ['Na', 0.1, 0.0, 0.0, 'Direct'], ['Na', 5.234, 0.0, 0.0, 'Cartesian']
        """
        from jump2.db.utils.convert import direct2cartesian
        
        if dtype.strip().lower() == 'direct':
            return [self.element.symbol, self.position[0], self.position[1], self.position[2], 'Direct']
        elif dtype.strip().lower() == 'cartesian':
            position=direct2cartesian(self.structure.lattice, self.position)
            return [self.element.symbol, position[0], position[1], position[2], 'Cartesian']
        else:
            raise ValueError('unknown dtype')
    
    def nearest_neighbors(self, cutoff=3.0, **kwargs):        
        """
        find out the nearest neighbors of a atom. Note that actually searching radius is cutoff*1.2. 
        
        Arguments:
            cutoff (default=3.0): cutoff radius when calculating the nearest neighbors.
            
        Returns:
            the nearest neighbors of atom.
            
        找出原子的最近临。注意：在寻找过程中，实际找的范围是设置的阶段半径的1.2倍，防止漏掉一些原子。但是，输出的原子还是截断半径以内的原子。
        
        参数：
            cutoff (default=3.0):找最近临所用的截断半径。
            
        返回：
            最近临原子。
        """
        
        rdf=self.rdf(cutoff*1.2)
        for k in sorted(rdf.keys()):
            if k > cutoff:
                rdf.pop(k)
        nearest_neighbors=rdf
        return nearest_neighbors
    
    def rdf(self, max_r=10.0, dr=0.1):
        """
        radius distribution function for atom.
        
        Arguments:
            max_r (default=10.0): max radius (unit: Angstrom).
            dr (default=0.1): delta radius (unit: Angstrom).
            
        Returns:
            {r:{symbol:positions}}
            
        原子的径向分布函数。
        
        参数：
            max_r (default=10.0):计算的最大距离（单位：埃）。
            dr (default=0.1):距离的步长（单位：埃）。
            
        返回：
            径向分布函数字典 {r:{symbol:positions}}。
        """
        import math
        import numpy as np
        from jump2.db.utils.convert import any2cartesian
        
        lattice_parameters=self.structure.lattice_parameters
        a_l=int(math.floor(self.position[0]-max_r/lattice_parameters[0])) # left of a in lattice for supercell
        a_r=int(math.ceil(self.position[0]+max_r/lattice_parameters[0])) # right of a in lattice for supercell
        b_l=int(math.floor(self.position[1]-max_r/lattice_parameters[1])) # left of b in lattice for supercell
        b_r=int(math.ceil(self.position[1]+max_r/lattice_parameters[1])) # right of b in lattice for supercell
        c_l=int(math.floor(self.position[2]-max_r/lattice_parameters[2])) # left of c in lattice for supercell
        c_r=int(math.ceil(self.position[2]+max_r/lattice_parameters[2])) # right of c in lattice for supercell
        dim=[[a_l, a_r], [b_l, b_r], [c_l, c_r]] # range of suercell's size
        
        rdf={}
        for atom in self.structure.atoms:
            symbol=atom.element.symbol
            position=atom.position
            for i in xrange(dim[0][0], dim[0][1]): # x
                for j in xrange(dim[1][0], dim[1][1]): # y
                    for k in xrange(dim[2][0], dim[2][1]): # z
                        x=position[0]+i
                        y=position[1]+j
                        z=position[2]+k
                        
                        r=np.linalg.norm(any2cartesian(self.structure.lattice, np.array([x,y,z])-self.position))
                        r=math.floor(r/dr)*dr
                        
                        atom={symbol:[[x, y, z]]}
                        if rdf == {}:
                            rdf[r]=atom
                        elif r in rdf:
                            value=rdf[r] # {symbol: positions}
                            if symbol in value.keys():
                                v=value[symbol]
                                v.append([x, y, z])
                                value[symbol]=v
                            else:
                                value[symbol]=atom[symbol]
                            rdf[r]=value
                        else: 
                            rdf[r]=atom
        rdf.pop(0.0) # remove self       
        
        return rdf
        
        
        
    
    
    