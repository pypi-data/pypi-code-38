'''
Created on Nov 28, 2017

@author: Yuhao Fu
'''
from django.core.cache import cache
import cPickle
from jump2.db.utils.initialization.init_elements import InitializeMolElement
from jump2.db.materials.molElement import MolElement

class CachedMolElementProvider(object):
    """
    cache of element.
    
    """
    def get(self, symbol):
        """
        get element.
        
        Arguments:
            symbol: element's symbol. i.e. H
            
        Returns:
            element's object.
        """
        symbol_cache='molElement_%s' %symbol
        element=None
        if cache.has_key(symbol_cache):
            element=self._get_from_cache(symbol_cache)
        elif MolElement.objects.filter(symbol=symbol).exists():
            element=self._get_from_db(symbol)
            self.put(symbol, element)
        else:
            element=self.set(symbol)
        
        # initialize
        element.structures=[]
        element.compositions=[]
        element.species=[]
        element.atoms=[]
        
        return element
        
        
    def _get_from_cache(self, symbol_cache):
        """
        get element from cache.
        
        Arguments:
            symbol_cache: formated symbol of element. i.e. molElement_H
        """
        return cPickle.loads(cache.get(symbol_cache))
    
    def _get_from_db(self, symbol_cache):
        """
        get element from database.
        
        Arguments:
            symbol_cache: formated symbol of element. i.e. molElement_H
        """
        return MolElement.objects.get(symbol=symbol_cache)
        
    def put(self, symbol, element):
        """
        put element in cache.
        
        Arguments:
            symbol_cache: formated symbol of element. i.e. molElement_H
            element: object of element.
        """
        symbol_cache='molElement_%s' %symbol
        cache.set(symbol_cache, cPickle.dumps(element, protocol=1), 60*30) # 30 minutes
    
    def set(self, symbol):
        """
        add new element to database and update the cache.
        
        Arguments:
            symbol: element's symbol. i.e. H
        """
        InitializeMolElement(symbol)
        element=self._get_from_db(symbol)
        self.put(symbol, element)
        return element
        