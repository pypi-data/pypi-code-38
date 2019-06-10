'''
Created on Oct 23, 2017

@author: Yuhao Fu
'''
from jump2.db.materials.element import Element
from django.core.cache import cache
import cPickle
from jump2.db.utils.initialization.init_elements import InitializeElement

class CachedElementProvider(object):
    """
    cache of element.
    
    likely cache asid. the algorithm is:
        1. if 
    """
    def get(self, symbol):
        """
        get element.
        
        Arguments:
            symbol: element's symbol. i.e. H
            
        Returns:
            element's object.
        """
        symbol_cache='element_%s' %symbol
        element=None
        if cache.has_key(symbol_cache):
            element=self._get_from_cache(symbol_cache)
        elif Element.objects.filter(symbol=symbol).exists():
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
            symbol_cache: formated symbol of element. i.e. element_H
        """
        return cPickle.loads(cache.get(symbol_cache))
    
    def _get_from_db(self, symbol_cache):
        """
        get element from database.
        
        Arguments:
            symbol_cache: formated symbol of element. i.e. element_H
        """
        return Element.objects.get(symbol=symbol_cache)
        
    def put(self, symbol, element):
        """
        put element in cache.
        
        Arguments:
            symbol_cache: formated symbol of element. i.e. element_H
            element: object of element.
        """
        symbol_cache='element_%s' %symbol
        cache.set(symbol_cache, cPickle.dumps(element, protocol=1), 60*30) # 30 minutes
    
    def set(self, symbol):
        """
        add new element to database and update the cache.
        
        Arguments:
            symbol: element's symbol. i.e. H
        """
        InitializeElement(symbol)
        element=self._get_from_db(symbol)
        self.put(symbol, element)
        return element
        
class CompressedCachedElementProvider(object):
    """
    address cache of element in a compressed format (bz2 by default).
    
    """
    def get(self, symbol):
        """
        get element.
        
        Arguments:
            symbol: element's symbol. i.e. H
        """
        symbol_cache='compressed_element_%s' %symbol
        if cache.has_key(symbol_cache):
            return self._get_from_cache(symbol_cache)
        elif Element.objects.filter(symbol=symbol).exists():
            element=self._get_from_db(symbol)
            self.put(symbol, element)
            return element
        else:
            element=self.set(symbol)
            return element
        
    def _get_from_cache(self, symbol_cache):
        """
        get element from cache.
        
        Arguments:
            symbol_cache: formated symbol of element. i.e. compressed_element_H
        """
        return cPickle.loads(cache.get(symbol_cache).decode('base64').decode('bz2'))
    
    def _get_from_db(self, symbol_cache):
        """
        get element from database.
        
        Arguments:
            symbol_cache: formated symbol of element. i.e. compressed_element_H
        """
        return Element.objects.get(symbol=symbol_cache.split('_')[-1])
        
    def put(self, symbol, element):
        """
        put element in cache.
        
        Arguments:
            symbol: element's symbol.
            element: object of element.
        """
        symbol_cache='compressed_element_%s' %symbol
        cache.set(symbol_cache, cPickle.dumps(element, protocol=1).encode('bz2').encode('base64'), 60*30) # 30 minutes
    
    def set(self, symbol):
        """
        add new element to database and update the cache.
        
        Arguments:
            symbol: element's symbol. i.e. H
        """
        InitializeElement(symbol)
        element=self._get_from_db(symbol)
        self.put(symbol, element)
        return element
            
        