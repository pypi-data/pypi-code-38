'''
Created on Nov 23, 2017

@author: Yuhao Fu
'''
from jump2.db.materials.spacegroup import Spacegroup
from django.core.cache import cache
import cPickle

class CachedSpacegroupProvider(object):
    """
    cache of spacegroup (contains its operations' object).
    
    """
    def get(self, number):
        """
        get spacegroup.
        
        Arguments:
            number: number of spacegroup.
        
        Returns:    
            spacegroup's object.
        """
        spacegroup_cache='spacegroup_%s' %number
        spacegroup=None
        if cache.has_key(spacegroup_cache):
            spacegroup=self._get_from_cache(spacegroup_cache)
        elif Spacegroup.objects.filter(number=number).exists():
            spacegroup=self._get_from_db(spacegroup_cache)
            self.put(number, spacegroup)
        else:
            #spacegroup=self.set(number)
            return None
        # initialize
        #spacegroup.wyckoffSites=[]
        
        return spacegroup
    
    def _get_from_cache(self, spacegroup_cache):
        """
        get spacegroup from cache.
        
        Arguments:
            spacegroup_cache: formated number. i.e. spacegroup_1
        """
        return cPickle.loads(cache.get(spacegroup_cache))
    
    def _get_from_db(self, spacegroup_cache):
        """
        get spacegroup from database.
        
        Arguments:
            spacegroup_cache: formated number. i.e. spacegroup_1
        """
        spacegroup=Spacegroup.objects.get(number=spacegroup_cache.split('_')[-1])
        return spacegroup
    
    def put(self, number, spacegroup):
        """
        put spacegroup in cache.
        
        Arguments:
            number: number of spacegroup.
            spacegroup: object of spacegroup.
        """
        spacegroup_cache='spacegroup_%s' %number
        cache.set(spacegroup_cache, cPickle.dumps(spacegroup, protocol=1), 60*30)
        
    def set(self, number, **kwargs):
        """
        Arguments:
            number: number of spacegroup.
            isPersist: if True, save to database. Conversely, only run in memory.
            
            kwargs:
                operations: collection of operation's object.
                #wyckoffSites: collection of wyckoffSite's object.
                #structures: collection of structure's object.
                
                international: international short symbol.
                hm: hall number.
                hall: hall symbol.
                pearson: 
                schoenflies:
                lattice_system:
                centerosymmetric:
        """
        spacegroup=Spacegroup().create(number, isPersist=True)
        if 'international' in kwargs:
            spacegroup.international=kwargs['international']
        if 'hm' in kwargs:
            spacegroup.hm=kwargs['hm']
        if 'hall' in kwargs:
            spacegroup.hall=kwargs['hall']
        if 'pearson' in kwargs:
            spacegroup.pearson=kwargs['pearson']
        if 'schoenflies' in kwargs:
            spacegroup.schoenflies=kwargs['schoenflies']
        if 'lattice_system' in kwargs:
            spacegroup.lattice_system=kwargs['lattice_system']
        if 'centerosymmetric' in kwargs:
            spacegroup.centerosymmetric=kwargs['centerosymmetric']
        
        spacegroup.save()
        self.put(number, spacegroup)
        
        return spacegroup
        
        
        
        
        
        
            
            
            
            
            
            
            
