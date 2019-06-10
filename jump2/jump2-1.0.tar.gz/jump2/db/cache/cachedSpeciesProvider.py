'''
Created on Oct 30, 2017

@author: Yuhao Fu
'''
from jump2.db.materials.species import Species
from django.core.cache import cache
import cPickle

class CachedSpeciesProvider(object):
    """
    cache of species.
    
    """
    def get(self, name):
        """
        get species.
        
        Arguments:
            name: speices's name. i.e. Fe2+
            
        Returns:
            species's object.
        """
        name_cache='species_%s' %name
        species=None
        if cache.has_key(name_cache):
            species=self._get_from_cache(name_cache)
        elif Species.objects.filter(name=name).exists():
            species=self._get_from_db(name)
            self.put(name, species)
        else:
            species=self.set(name)

        # initialize
        species.structures=[]
        species.atoms=[]
        
        return species
        
    def _get_from_cache(self, name_cache):
        """
        get species from cache.
        
        Arguments:
            name_cache: formated species's name. i.e. species_Fe2+
        """
        return cPickle.loads(cache.get(name_cache))
    
    def _get_from_db(self, name_cache):
        """
        get species from database.
        
        Arguments:
            name_cache: formated species's name. i.e. species_Fe2+
        """
        return Species.objects.get(name=name_cache)
        
    def put(self, name, species):
        """
        put species in cache.
        
        Arguments:
            name_cache: formated species's name. i.e. species_Fe2+
            species: object of species.
        """
        name_cache='species_%s' %name
        cache.set(name_cache, cPickle.dumps(species, protocol=1), 60*30) # 30 minutes
    
    def set(self, name):
        """
        add new species to database and update the cache.
        
        Arguments:
            name: species's name. i.e. Fe2+
        """
        species=Species().create(name, isPersist=True)
        self.put(name, species)
        return species
    
    