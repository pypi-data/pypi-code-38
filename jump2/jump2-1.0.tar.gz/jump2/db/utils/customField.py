'''
Created on Oct 20, 2017

@author: Yuhao Fu
'''
import numpy as np
import cPickle
from django.db import models

class ListField(models.TextField):
    description='Stores a python list'
 
    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return []
        
        return cPickle.loads(str(value))
    
    def to_python(self, value):
        if value is None:
            return []
 
        if isinstance(value, list):
            return value
 
        return cPickle.loads(str(value))
    
    def get_prep_value(self, value):
        if value is None:
            return value
        elif isinstance(value, list):
            return cPickle.dumps(value, protocol=0)
        elif isinstance(value, np.ndarray):
            return cPickle.dumps(value.tolist(), protocol=0)
        else:
            raise TypeError('%s is not a list or numpy array' %value)
 
    def value_to_string(self, obj):
        value=self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
        
class NumpyArrayField(models.TextField):
    description='Stores a numpy ndarray'

    def __init__(self, *args, **kwargs):
        super(NumpyArrayField, self).__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return np.array([])   
        return np.array(cPickle.loads(str(value)))
    
    def to_python(self, value):
        if value is None:
            return np.array([])
            
        if isinstance(value, list):
            value=np.array(value)
        if isinstance(value, np.ndarray):
            return value
        
        return np.array(cPickle.loads(str(value)))
    
    def get_prep_value(self, value):
        if value is None:
            return value
        elif isinstance(value, list):
            return cPickle.dumps(value, protocol=0)
        elif isinstance(value, np.ndarray):
            return cPickle.dumps(value.tolist(), protocol=0)
        else:
            raise TypeError('%s is not a list or numpy array' %value)
    
    def value_to_string(self, obj):
        value=self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
        
class DictField(models.TextField):
    description='Stores a python dictionary'
    
    def __init__(self, *args, **kwargs):
        super(DictField, self).__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return {}
        return cPickle.loads(str(value))
    
    def to_python(self, value):
        if value is None:
            return {}
            
        if isinstance(value, dict):
            return value
        
        return cPickle.loads(str(value))
    
    def get_prep_value(self, value):
        if value is None:
            return value
        elif isinstance(value, dict):
            return cPickle.dumps(value, protocol=0)
        else:
            raise TypeError('%s is not a python dictionary' %value)
    
    def value_to_string(self, obj):
        value=self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
    
class CompressedTextField(models.TextField):
    description='Stores a string text in a compressed format (bz2 by default)'
    
    def __init__(self, *args, **kwargs):
        super(CompressedTextField, self).__init__(*args, **kwargs)
        
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return ''
        
        return cPickle.loads(str(value.decode('base64').decode('bz2').decode('utf-8')))
    
    def to_python(self, value):
        if value is None:
            return ''
        
        if isinstance(value, str):
            return value
        
        return cPickle.loads(str(value.decode('base64').decode('bz2').decode('utf-8')))
    
    def get_prep_value(self, value):
        if value is None:
            return value
        elif isinstance(value, str):
            return cPickle.dumps(value, protocol=1).encode('utf-8').encode('bz2').encode('base64')
        else:
            raise TypeError('%s is not a string text' %value)

class CompressedListField(models.TextField):
    description='Stores a python list in a compressed format (bz2 by default)'
 
    def __init__(self, *args, **kwargs):
        super(CompressedListField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return []
        
        return cPickle.loads(str(value.decode('base64').decode('bz2').decode('utf-8')))
    
    def to_python(self, value):
        if value is None:
            return []
 
        if isinstance(value, list):
            return value
 
        return cPickle.loads(str(value.decode('base64').decode('bz2').decode('utf-8')))
    
    def get_prep_value(self, value):
        if value is None:
            return value
        elif isinstance(value, list):
            #string=cPickle.dumps(value, protocol=1)
            #return string.encode('utf-8').encode('bz2').encode('base64')
            return cPickle.dumps(value, protocol=1).encode('utf-8').encode('bz2').encode('base64')
        elif isinstance(value, np.ndarray):
            #string=cPickle.dumps(value.tolist(), protocol=1)
            #return string.encode('utf-8').encode('bz2').encode('base64')
            return cPickle.dumps(value.tolist(), protocol=1).encode('utf-8').encode('bz2').encode('base64')
        else:
            raise TypeError('%s is not a list or numpy array' %value)
 
    def value_to_string(self, obj):
        value=self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class CompressedNumpyArrayField(models.TextField):
    description='Stores a numpy ndarray in a compressed format (bz2 by default)'

    def __init__(self, *args, **kwargs):
        super(CompressedNumpyArrayField, self).__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return np.array([])   
        return np.array(cPickle.loads(str(value.decode('base64').decode('bz2').decode('utf-8'))))
    
    def to_python(self, value):
        if value is None:
            return np.array([])
            
        if isinstance(value, list):
            value=np.array(value)
        if isinstance(value, np.ndarray):
            return value
        
        return np.array(cPickle.loads(str(value.decode('base64').decode('bz2').decode('utf-8'))))
    
    def get_prep_value(self, value):
        if value is None:
            return value
        elif isinstance(value, list):
            return cPickle.dumps(value, protocol=1).encode('utf-8').encode('bz2').encode('base64')
        elif isinstance(value, np.ndarray):
            return cPickle.dumps(value.tolist(), protocol=1).encode('utf-8').encode('bz2').encode('base64')
        else:
            raise TypeError('%s is not a list or numpy array' %value)
    
    def value_to_string(self, obj):
        value=self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class CompressedDictField(models.TextField):
    description='Stores a python dictionary in a compressed format (bz2 by default)'
    
    def __init__(self, *args, **kwargs):
        super(CompressedDictField, self).__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return {}
        return cPickle.loads(str(value.decode('base64').decode('bz2').decode('utf-8')))
    
    def to_python(self, value):
        if value is None:
            return {}
            
        if isinstance(value, dict):
            return value
        
        return cPickle.loads(str(value.decode('base64').decode('bz2').decode('utf-8')))
    
    def get_prep_value(self, value):
        if value is None:
            return value
        elif isinstance(value, dict):
            return cPickle.dumps(value, protocol=1).encode('utf-8').encode('bz2').encode('base64')
        else:
            raise TypeError('%s is not a python dictionary' %value)
    
    def value_to_string(self, obj):
        value=self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

