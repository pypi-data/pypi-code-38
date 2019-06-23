#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# cluster.py
# Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
# Implements a Cluster object 
#

from ditto_lib.utils.logging import logger
from ditto_lib.utils.dataframe import DataFrame
from ditto_lib.itemcollection import ItemCollection

from ordered_set import OrderedSet

class Cluster():

    def __init__(self, name=None):
        self._name = name
        self._items = {}

    def __repr__(self):
        return "Cluster {}".format(self.name)

    def __len__(self):
        '''
        Returns the amount of items in this cluster
        '''
        return len(self._items)

    @property
    def name(self):
        '''
        Name of the item
        '''
        return self._name

    @name.setter
    def name(self, name):
        logger.log('debug', "{} name set to {}".format(self._name, name))
        self._name = name

    @property
    def items(self):
        '''
        Return all the items stored by this cluster
        '''
        return self._items

    def copy(self, name):
        '''
        Returns a deep copy of this cluster
        '''
        new_cluster = Cluster(name)
        new_cluster._items = self._items.copy()
        return new_cluster

    def add_item(self, name, values):
        self._items[name] = values
        logger.log('debug', "Added item {} from cluster {}".format(name, self.name))

    def remove_item(self, name):
        '''
        Remove the item from the items list
        '''
        del self._items[name]
        logger.log('debug', "Removed item {} from cluster {}".format(name, self.name))

    def contains(self, name):
        '''
        Returns whether this cluster contains the item given.
        Accepts the item name
        '''
        return name in self._items

    def as_itemcollection(self, attributes, copy=False):
        '''
        Return this cluster as an item collection.

        Args:
        attributes(OrderedSet/Set): Attributes of the new ItemCollection
        copy(bool): If copy is set to True, then the returned ItemCollection will be a 
            deep copy of this cluster. Useful if you need to modify the resulting collection
            but do not want to affect this cluster. Will work slower than a shallow copy 
        '''
        attribute_dict = OrderedSet()
        item_dict = {}
        dataframe = DataFrame()
        if copy:
            item_dict = {name : values.copy for name, values in self._items.items()}
            attribute_dict = OrderedSet([attribute.copy for attribute in attributes])
        else:
            item_dict = self._items
            attribute_dict = attributes
        item_collection = ItemCollection(self.name)
        dataframe.items = item_dict
        dataframe.attributes = attribute_dict
        self._df = dataframe
        return item_collection