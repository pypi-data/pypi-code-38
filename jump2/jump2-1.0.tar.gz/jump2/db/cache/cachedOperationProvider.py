'''
Created on Dec 7, 2017

@author: Yuhao Fu
'''
from jump2.db.materials.spacegroup import Operation
from django.core.cache import cache
import cPickle
from jump2.db.utils.fetch import get_operation_from_db

class CachedOperationProvider(object):
    """
    cache of operation
    """
    def get(self, operation):
        """
        get operation.
        
        Arguments:
            operation: {'translation': np.ndarray ([3] (float)), 'rotation': np.ndarray ([3,3] (int))}
            
        Returns:
            operation's object.
        """
        
        operation_cache=self._dict2string(operation)
        operation_obj=None # operation's object
        if cache.has_key(operation_cache):
            operation_obj=self._get_from_cache(operation_cache)
        elif not get_operation_from_db(operation) is None:
            operation_obj=self._get_from_db(operation_cache)
            self.put(operation, operation_obj)
        else:
            operation_obj=self.set(operation)
            
        return operation_obj
    
    def _get_from_cache(self, operation_cache):
        """
        get operation from cache.
        
        Arguments:
            operation_cache: formated operation. i.e. operation_[0.00000000-0.00000000-0.00000000]-[[1-0-0]-[0-1-0]-[0-0-1]]
        """
        return cPickle.loads(cache.get(operation_cache))
    
    def _get_from_db(self, operation_cache):
        """
        get operation from database.
        
        Arguments:
            operation_cache: formated operation. i.e. operation_[0.00000000-0.00000000-0.00000000]-[[1-0-0]-[0-1-0]-[0-0-1]]
        """
        operation=self._string2dirct(operation_cache)
        operation_obj=get_operation_from_db(operation)
        return operation_obj
    
    def put(self, operation, operation_obj):
        """
        put operation in cache.
        
        Arguments:
            operation: {'translation': np.ndarray ([3] (float)), 'rotation': np.ndarray ([3,3] (int))}
            operation_obj: object of operation.
        """
        operation_cache=self._dict2string(operation)
        cache.set(operation_cache, cPickle.dumps(operation_obj, protocol=1), 60*30)
    
    def set(self, operation):
        """
        Arguments:
            operation: {'translation': np.ndarray ([3] (float)), 'rotation': np.ndarray ([3,3] (int))}
        """
        operation_obj=Operation().create(operation, isPersist=True)
        self.put(operation, operation_obj)
        
        return operation_obj
        
        
    def _dict2string(self, operation):
        """
        operation convert to operation_cache.
        
        Arguments:
            operation: {'translation': np.ndarray ([3] (float)), 'rotation': np.ndarray ([3,3] (int))}
            
        Returns:
            operation_cache. i.e. operation_[/0.00000000/0.00000000/0.00000000]-[[/1/0/0]-[/0/1/0]-[/0/0/1]]
        """
        operation_cache='operation_[/%.8f/%.8f/%.8f/]-[[/%d/%d/%d/]-[/%d/%d/%d/]-[/%d/%d/%d/]]' \
            %(operation['translation'][0],operation['translation'][1],operation['translation'][2], \
              operation['rotation'][0][0],operation['rotation'][0][1],operation['rotation'][0][2], \
              operation['rotation'][1][0],operation['rotation'][1][1],operation['rotation'][1][2], \
              operation['rotation'][2][0],operation['rotation'][2][1],operation['rotation'][2][2],)
        return operation_cache
    
    def _string2dirct(self, operation_cache):
        """
        operation_cache convert to operation.
        
        Arguments:
            operation_cache: formated operation. i.e. operation_[0.00000000-0.00000000-0.00000000]-[[1-0-0]-[0-1-0]-[0-0-1]]
            
        Returns:
            operation ({'translation': np.ndarray ([3] (float)), 'rotation': np.ndarray ([3,3] (int))}).
        """
        import numpy as np
        
        tmp=operation_cache.split('/')
        translation=np.array([float(s0) for s0 in tmp[1:4]])
        rotation=np.array([[int(s0) for s0 in tmp[5:8]],
                  [int(s0) for s0 in tmp[9:12]],
                  [int(s0) for s0 in tmp[13:16]]])
        operation={'translation':translation, 'rotation':rotation}
        return operation
            