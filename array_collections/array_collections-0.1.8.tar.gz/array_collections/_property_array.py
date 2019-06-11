# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 03:56:02 2019

@author: yoelr
"""
import numpy as np
from pandas import DataFrame
from ._tuple_array import tuple_array
from free_properties._free_property import inplace_magic_names
import re

__all__ = ('property_array',)

ndarray = np.ndarray
asarray = np.asarray
getitem = ndarray.__getitem__
broadcast = np.broadcast_to

# %% Functions

# def has_property(array):
#     return (0 in array.shape or 
#             hasattr(ndarray.__getitem__(array, (0,)*array.ndim), 'value'))

def make_1d_table(data, with_units, ndim):
    """Create a 1d DataFrame object if all entries have the same type."""
    index = []; cols = []
    # Add index
    for i in data:
        index.append(str(i.name))
    
    # Make sure all items have same type
    i0 = data.item(0)
    if not (np.array([type(i) for i in data]) == type(i0)).all():
        return None
    
    # Add column
    colname = type(i0).__name__
    colname = re.sub(r"\B([A-Z])", r" \1", colname).capitalize()
    units = f' ({i0._units})' if with_units else ''
    cols.append(colname + units)
    
    return DataFrame(data, index=index, columns=cols)
    
def make_2d_table(data, with_units, ndim):
    """Create a 2d DataFrame object if all columns and rows have the same type and name attribute respectively."""
    index = []; cols = []
    for r in data:
        # Add index
        i0 = r.item(0)
        name0 = str(i0.name)
        index.append(name0)
        
        # Make sure the whole row is of same type
        names = np.array([str(i.name) for i in r])
        if not (names == name0).all(): return None
    
    for r in data.transpose():
        # Add column
        Type0 = type(r.item(0))
        colname = Type0.__name__
        colname = re.sub(r"\B([A-Z])", r" \1", colname).capitalize()
        units = f' ({i0._units})' if with_units else ''
        cols.append(colname + units)
        
        # Make sure the whole column is of same type
        Types = np.array([type(i) for i in r])
        if not (Types == Type0).all(): return None    

    return DataFrame(data, index=index, columns=cols)


# %% Property array

class property_array(ndarray):
    """Create an array that allows for array-like manipulation of FreeProperty objects. All entries in a property_array must be instances of FreeProperty. Setting items of a property_array sets values of objects instead.
    
    **Parameters**
    
        **array:** array_like[FreeProperty] Input data, in any form that can be converted to an array. This includes lists, lists of tuples, tuples, tuples of tuples, tuples of lists and ndarrays.
    
        **order:** {'C', 'F'} Whether to use row-major (C-style) or column-major (Fortran-style) memory representation. Defaults to ‘C’.
    
    **Examples**
    
        Use the PropertyFactory to create a Weight property class which calculates weight based on density and volume:
    
        .. code-block:: python
        
            from array_collections import PropertyFactory
           
            >>> @PropertyFactory
            >>> def Weight(self):
            ...    '''Weight (kg) based on volume (m^3).'''
            ...    data = self.data
            ...    rho = data['rho'] # Density (kg/m^3)
            ...    vol = data['vol'] # Volume (m^3)
            ...    return rho * vol
            >>>
            >>> @Weight.setter
            >>> def Weight(self, weight):
            ...    data = self.data
            ...    rho = data['rho'] # Density (kg/m^3)
            ...    data['vol'] = weight / rho
           
        Create dictionaries of data and initialize new properties:
       
        .. code-block:: python
       
           >>> water_data = {'rho': 1000, 'vol': 3}
           >>> ethanol_data = {'rho': 789, 'vol': 3}
           >>> weight_water = Weight('Water', water_data)
           >>> weight_ethanol = Weight('Ethanol', ethanol_data)
           >>> weight_water
           Weight(Water) -> 3000 (kg)
           >>>weight_ethanol
           Weight(Ethanol) -> 2367 (kg)
          
        Create a property_array from data:
           
        .. code-block:: python
       
           >>> prop_arr = property_array([weight_water, weight_water])
           property_array([3000, 2367])
           
        Changing the values of a property_array changes the value of its properties:
           
        .. code-block:: python
       
           >>> # Addition in place
           >>> prop_arr += 3000
           >>> prop_arr
           property_array([6000, 5367])
           >>> # Note how the data also changes
           >>> water_data
           {'rho': 1000, 'vol': 6.0}
           >>> ethanol_data
           {'rho': 789, 'vol': 6.802281368821292}
           >>> # Setting an item changes the property value
           >>> prop_arr[1] = 2367
           >>> ethanol_data
           {'rho': 789, 'vol': 3}
          
        New arrays have no connection to the property_array:
           
        .. code-block:: python
       
           >>> prop_arr - 1000 #  Returns a new array
           array([5000.0, 1367.0], dtype=object)
           >>> water_data #  Data remains unchanged
           {'rho': 1000, 'vol': 6.0}
           
        A representative DataFrame can also be made from the property_array:
           
        .. code-block:: python
       
          >>> prop_arr.table()
                  Weight (kg)
          Water        6000.0
          Ethanol      2367.0
           
        .. Note:: The DataFrame object contains the values of the properties, not the FreeProperty objects as a property_array would.
    
    """
    __slots__ = ()          
    
    def __new__(cls, properties, order='C'):
        return asarray(properties, object, order).view(cls)
    
    def __getitem__(self, key):
        value = getitem(self, key)
        if isinstance(value, property_array): return value
        else: return value.value
    
    def __setitem__(self, key, value):
        items = self.view(ndarray)[key]
        if isinstance(items, ndarray):
            for i, v in zip(items.flatten(), broadcast(value, items.shape).flatten()):
                i.value = v 
        else:
            items.value = value
    
    def __array_wrap__(self, result):
        if self is result: return self
        else: return result.view(ndarray)
    
    def table(self, title='', with_units=True):
        """Create a representative DataFrame object."""
        ndim = self.ndim
        if ndim == 1:
            make_table = make_1d_table
        elif ndim == 2:
            make_table = make_2d_table
        else:
            raise ValueError(f'Dimension of table must be either 1 or 2, not {self.ndim}')
        
        data = self.view(ndarray)
        # First assume all columns and rows have the same type and name respectively
        table = make_table(data, with_units, ndim)
        if table is None:
            # When this fails, assume all rows have same type and columns have same name
            data = data.transpose()
            table = make_table(data, with_units, ndim)
            if table is None:
                raise TypeError('To create a table, at least one dimension must have the same property type and the other dimension the same property name.')
            else:
                table = table.transpose()
        table.title = title
        return table
    
    def __repr__(self):
        if len(self) == 0: return tuple_array.__repr__(self)
        else: return tuple_array.__repr__(self.astype(type(self.item(0).value)))

def wrap_ifunc(iname):
    name = iname[:2] + iname[3:] # Remove 'i'
    if hasattr(property_array, name):
        ifunc = getattr(property_array, iname)
        func = getattr(property_array, name)
        def wrapper(self, *args, **kwargs):
            self[:] = func(self, *args, **kwargs)
            return self
        wrapper.__name__ = iname
        wrapper.__doc__ = ifunc.__name__
        return wrapper

for iname in inplace_magic_names:   
    setattr(property_array, iname, wrap_ifunc(iname))

