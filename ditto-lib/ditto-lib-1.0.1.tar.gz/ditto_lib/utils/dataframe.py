#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  similarity.py
#  Developed in 2019 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements base DataFrame functionality
#

from ordered_set import OrderedSet

class Attribute:

    '''
    Attribute class
    '''

    def __init__(self, name, is_descriptor=True):
        self.is_descriptor = is_descriptor
        self.name = name
        self.hash = hash(name)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def copy(self):
        return Attribute(self.name, self.is_descriptor)

class DataFrame:

    '''
    Basic class for storing raw data
    '''

    def __init__(self):
        self.items = {}
        self.attributes = OrderedSet()

    def raw(self, excluded_attributes=set()):
        '''
        Return a dict. 'values' contains the raw data of 
        each item in an array. 'item_names' contains the names
        of the items in order. 'attribute_names' contains the name of
        the attributes in order.

        Args:
        excluded_attributes(set): A set of attribute names to exclude. Defaults to the empty set
        '''
        data_raw = []
        item_names = []
        attribute_names = []
        adding_attributes = True
        for item_name, item_data in self.items.items():
            descriptor_data = []
            for attribute in self.attributes:
                if attribute.is_descriptor and attribute.name not in excluded_attributes:
                    descriptor_data.append(float(item_data[self.attributes.index(attribute)]))
                    if adding_attributes is True:
                        attribute_names.append(attribute.name)
            adding_attributes = False
            data_raw.append(descriptor_data)
            item_names.append(item_name)
        return {'item_names' : item_names, 'values' : data_raw, 'attribute_names' : attribute_names}

    def item(self, name):
        '''
        Return the values of the given item name
        '''
        if name in self.items:
            return self.items[name]
        else:
            return None

    def copy(self):
        '''
        Retun a copy of this DataFrame
        '''
        dataframe = DataFrame
        dataframe.attributes = OrderedSet([self.attributes[i].copy() for i in range(len(self.attributes))])
        dataframe.items = {key : values.copy() for key, values in self.items.items()}
        return dataframe