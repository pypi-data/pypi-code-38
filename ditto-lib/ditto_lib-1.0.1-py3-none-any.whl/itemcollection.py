#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  itemcollection.py
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  Implements the a container to store Item objects.
#

import csv
import os.path
from ordered_set import OrderedSet

from ditto_lib.utils.logging import logger
from ditto_lib.utils.checker import check_package
from ditto_lib.utils.error import error, percent_error
from ditto_lib.utils.similarity import similarity
from ditto_lib.utils.scalar import scale, weighted
from ditto_lib.utils.dataframe import DataFrame, Attribute
from ditto_lib.tasks.pca import pca

from math import sqrt

try:
    from sklearn.ensemble import RandomForestRegressor
except:
    RandomForestClassifier = None

class ItemCollection:

    '''
    Basic class to store items. Takes the name of the collection.
    '''

    def __init__(self, name: str):
        self._preamble = []
        self._df = DataFrame()
        self._name = name
    
    def __eq__(self, other: ItemCollection):
        if self._df.attributes != other._df.attributes:
            logger.log('debug', "Attributes for {} and {} are not the same".format(self.name, other.name))
            return False
        for name, values in self._df.items.items():
            if not other.contains_item(name):
                logger.log('debug', "Item {} in {} but not in {}".format(name, self.name, other.name))
                return False
            for our_value, other_value in zip(values, other._df.items[name]):
                if our_value != other_value:
                    logger.log('debug', "Item {} does not contain same value for {} and {}".format(name, self.name, other.name))
                    return False
        for name, values in other._df.items.items():
            if not self.contains_item(name):
                logger.log('debug', "Item {} in {} but not in {}".format(name, other.name, self.name))
                return False
            for other_value, our_value in zip(values, self.items[name]):
                if other_value != our_value:
                    logger.log('debug', "Item {} does not contain same value for {} and {}".format(name, self.name, other.name))
                    return False
        return True

    @property
    def dataframe(self):
        return self._df
        
    @property
    def name(self):
        '''
        Name of the collection
        '''
        return self._name

    @name.setter
    def name(self, name: str):
        logger.log('debug', "{} name set to {}".format(self._name, name))
        self._name = name

    def __len__(self):
        '''
        Return how many items this collection is 
        storing
        ''' 
        return len(self._df.items)

    @property
    def attributes(self):
        '''
        Set of attribute names pertaining to this collection
        '''
        return self._df.attributes

    @property
    def items(self):
        '''
        Return all the dictionary of item name to items associated with this collection
        '''
        return self._df.items

    @property
    def iter(self):
        '''
        Return the iterable key, value pair for all items in the collection, this enables 
        the user to call for name, values in collection.iter without having to call the more
        verbose collection.items.items()
        '''
        return self._df.items.items()

    @property
    def preamble(self):
        return self._preamble

    @preamble.setter
    def preamble(self, preamble: list):
        self._preamble = preamble

    def get_item(self, name: str):
        '''
        Return the item values associated with the given item name.
        '''
        item = self._df.item(name)
        if item is not None:
            return item
        else:
            logger.log('error', "Could not get item {} from collection {}".format(name, self.name))
            raise ValueError("Could not get item {} from collection {}".format(name, self.name))

    def item_names(self):
        '''
        Return all the item names that are held by this 
        collection
        '''
        return self._df.items.keys()

    def strip(self, threshold=None):
        '''
        Remove any noisy attributes. Accepts a threshold, a number between 1 and 0. If 
        the percent of different values for a single attribute amongst all items is less
        than or equal to the threshold, remove it. Defaults to None, which will delete 
        an attribute only if all items's share the same value for that attribute. Returns 
        the name of the attributes that were stripped
        '''
        if threshold is None:
            threshold = 1/len(self._df.items)
            logger.log('debug', "Stripping items from {} that all share same value".format(self.name))           
        elif threshold <= 0 or threshold >= 1:
            logger.log('error', "Threshold must be a number between 1 and 0")
            raise ValueError("Threshold must be a number between 1 and 0")
        else:
            logger.log('debug', "Stripping items from {} with a threshold of {}".format(self.name, threshold))
        if len(self.items) > 0:
            to_strip = []
            for attribute in self._df.attributes:
                if attribute.is_descriptor:
                    unique_scores = set()
                    for item in self.items.values():
                        unique_scores.add(item[self.attributes.index(attribute)])
                    if len(unique_scores) / len(self._df.items) <= threshold:
                        to_strip.append(attribute.name)
            for attribute_name in to_strip:
                self.remove_attribute(attribute_name)
                logger.log('debug', "Stripped {} from {}".format(attribute_name, self.name))
        logger.log('info', "Stripped {} amount of attributes from {}".format(len(to_strip), self.name))
        return to_strip

    def attribute(self, attribute_name: str):
        '''
        Returns the attribute with the given name, 
        raises a ValueError is the attribute is not stored
        in the collection
        '''
        attribute = Attribute(attribute_name)
        if attribute not in self._df.attributes:
            logger.log('error', "Tried to get attribute {} in {}, not found".format(attribute_name, self.name))
            raise ValueError("Tried to get attribute {} in {}, not found".format(attribute_name, self.name))
        return self._df.attributes[self._df.attributes.index(attribute)]

    def add_attribute(self, attribute: Attribute):
        '''
        Adds an attribute to the ItemCollection. Adds this 
        attribute to all the items within the collection as well
        '''
        if attribute not in self._df.attributes:
            self._df.attributes.add(attribute)
            for item in self._df.items.values():
                item.append(None)
        logger.log('debug', "Added attribute {} to ItemCollection: {}".format(attribute.name, self._name))

    def remove_attribute(self, attribute_name: str):
        '''
        Remove the attribute from this collection and all items 
        stored in this collection as well. Takes an attribute name
        '''
        attribute = Attribute(attribute_name)
        if attribute not in self.attributes:
            logger.log('error', "Could not remove {} because it doesn't exist in {}".format(attribute_name, self.name))
        else:
            index = self._df.attributes.index(attribute)
            for item in self.items.values():
                del item[index]
            self._df.attributes.remove(attribute)
            logger.log('debug', "Removed attribute {} from {}".format(attribute_name, self.name))

    def prune_attributes(self, to_keep=set(), remove_ndescriptors=False):
        '''
        Remove all attributes

        Args:
        to_keep(set): The set of attribute names to keep. Defaults to empty set
        remove_ndescriptors(bool): True if you want to remove non descriptors, False if you want 
            to keep them. Defaults to False
        '''
        logger.log('debug', "Pruning attributes with to_keep {} and remove_descriptors {}".format(to_keep, remove_ndescriptors))
        to_remove = []
        for attribute in self._df.attributes:
            if attribute.is_descriptor is True or remove_ndescriptors is True:
                if attribute.name not in to_keep:
                    to_remove.append(attribute.name)
        for name in to_remove:
            self.remove_attribute(name)
        logger.log('debug', "Remaining attributes after pruning: {}".format([attribute.name for attribute in self._df.attributes]))

    def prune_preamble(self, length=None):
        '''
        Prune the preamble to the length given. If None, will only
        keep the preamble in columns with data in it, IE, the length 
        of the attributes
        '''
        if length is None:
            for idx, row in enumerate(self._preamble):
                self._preamble[idx] = row[:len(self._df.attributes) + 1]
        else:
            if length >= len(self._df.attributes):
                logger.log('error', "Length given to prune preamble is greater preamble, keeping as is")
            elif length == 0:
                self._preamble = []
            else:
                for idx, row in enumerate(self._preamble):
                    self._preamble[idx] = row[:length]

    def set_item_attribute(self, item_name: str, value: str, attribute_name: str, is_descriptor=True):
        '''
        Set the item's attribute to the given value. Adds this attribute if 
        the item doesn't contain it

        Args:
        item_name(str): The name of the item whose attribute is being modified/added
        attribute_name(str): The attribute being modified/added
        is_descriptor(bool): Boolean whether the attribute is a descriptor, defaults to True
        '''
        attribute = Attribute(attribute_name, is_descriptor)
        if attribute not in self._df.attributes:
            logger.log('debug', "Could not find {} in {}, adding".format(attribute.name, self.name))
            self.add_attribute(attribute)
        if attribute.is_descriptor is True:
            self._df.items[item_name][self.attributes.index(attribute)] = float(value)
        else:
            self._df.items[item_name][self.attributes.index(attribute)] = value
        logger.log('debug', "Added attribute {} to item {}".format(attribute.name, item_name))

    def set_descriptor(self, attribute_name: str, is_descriptor: bool):
        '''
        Set an item's is_descriptor boolean value

        Args:
        attribute_name(str): The name of the attribute
        is_descriptor(bool): Boolean is_descriptor value
        '''
        attribute = Attribute(attribute_name)
        if attribute not in self._df.attributes:
            logger.log('error', "Could not find {} in {}".format(attribute.name, self.name))
            raise ValueError("Could not find {} in {}".format(attribute.name, self.name))
        else:
            self._df.attributes[self._df.attributes.index(attribute)].is_descriptor = is_descriptor

    def item_attribute(self, item_name: str, attribute_name: str):
        '''
        Get the item's attribute

        Args:
        item_name(str): The name of the item whose attribute is being retrieved
        attribute_name(str): The name of the attribute being retrieved
        '''
        attribute = Attribute(attribute_name)
        if attribute in self.attributes:
            attribute = self._df.attributes[self.attributes.index(attribute)]
            if attribute.is_descriptor:
                return float(self.get_item(item_name)[self.attributes.index(Attribute(attribute_name))])
            else:
                return self.get_item(item_name)[self.attributes.index(Attribute(attribute_name))]
        else:
            logger.log('error', "Could not find attribute {} in {}".format(attribute_name, self.name))
            raise ValueError("Could not find attribute {} in {}".format(attribute_name, self.name))

    def attribute_values(self, attribute_name: str):
        '''
        Get the attribue value of all items for the 
        attribute name given. Returns these values in a 
        list of tuples. The first item in the tuple contains
        the item name, the second item contains the attribute value
        '''
        attribute = Attribute(attribute_name)
        if attribute not in self.attributes:
            logger.log('error', "Could not find attribute {} in {}".format(attribute_name, self.name))
            raise ValueError("Could not find attribute {} in {}".format(attribute_name, self.name))
        else:
            index = self.attributes.index(attribute)
            values = []
            for item_name, item in self.items.items():
                if self._df.attributes[index].is_descriptor:
                    values.append((item_name, float(item[index])))
                else:
                    values.append((item_name, item[index]))
            return values

    def attribute_index(self, attribute_name:str ):
        '''
        Returns the index of the attribute name given. This
        can then be used to index items manually
        '''
        attribute = Attribute(attribute_name)
        if attribute not in self.attributes:
            logger.log('error', "Could not find attribute {} in {}".format(attribute_name, self.name))
            raise ValueError("Could not find attribute {} in {}".format(attribute_name, self.name))
        else:
            return self.attributes.index(attribute)
            
    def add_item(self, item_name: str, values: list, attributes=None):
        '''
        Adds a item to the collection. Will mantain collection attribute 
        consistency amongst all items
        
        Args:
        item_name(str): Name of the item being added
        values(list): Values of the item being added
        attributes(OrdereSet): The set of Attributes of the item being added
        '''
        if attributes is None or attributes == self.attributes:
            logger.log('debug', "Item {} has the same attributes as {}".format(item_name, self.name))
            self._df.items[item_name] = values
        else:
            logger.log('debug', "Item {} does not have the same attributes as {}, consolidating attributes".format(item_name, self.name))
            new_values = []
            used = set()
            for i in range(len(self.attributes)):
                if self.attributes[i] not in attributes:
                    new_values.append(None)
                else:
                    new_values.append(values[attributes.index(self.attributes[i])])
                    used.add(attributes.index(self.attributes[i]))
            for index, attribute in enumerate(attributes):
                if index not in used:
                    new_values.append(values[index])
                    self.add_attribute(attribute)
            self._df.items[item_name] = new_values
            logger.log('debug', "Added item {} with values {}".format(item_name, self._df.items[item_name]))

    def remove_item(self, item_name: str):
        '''
        Removes the item with the given name if it exists
        '''
        if self.contains_item(item_name):
            del self.items[item_name]

    def contains_item(self, item_name: str):
        '''
        Returns true if collection contains an item
        with the name given
        '''
        return item_name in self._df.items

    def contains_attribute(self, attribute_name: str):
        '''
        Returns true if the collection contains an
        attribute with the name give
        '''
        return Attribute(attribute_name) in self._df.attributes

    def sorted(self, attribute_name: str, descending=False):
        '''
        Return a list of tuples sorted by the given attribute name. 
        The first item in the tuple is the item name, the second item
        is the list of its features. Frames that don't have this attribute
        defined are sent to the back of the list
        '''
        attribute = Attribute(attribute_name)
        if attribute in self._df.attributes:
            attribute = self._df.attributes[self.attributes.index(attribute)]
            if attribute.is_descriptor:
                index = self._df.attributes.index(attribute)
                for item in self._df.items.values():
                    item[index] = float(item[index])
            sort = sorted(self._df.items.keys(), key=lambda item : (self._df.items[item][self.attributes.index(attribute)] is None,
                self._df.items[item][self.attributes.index(attribute)]), reverse=descending)
            for index, item in enumerate(sort):
                sort[index] = (item, self._df.items[item][self.attributes.index(attribute)])
            return sort
        else:
            logger.log('error', "Tried to sort by {} which does not exist in container {}".format(attribute_name, self._name))
            raise ValueError("Tried to sort by {} which does not exist in container {}".format(attribute_name, self._name))

    def merge(self, collection, new_name: str, preamble_option='merge'):
        '''
        Return a collection that is the result of merging this
        collection and the one that is given. Merge attributes 
        and Items

        Args:
        collection(ItemCollection): The other collection to be merged with this one
        new_name(str): The name of the new collection\
        preamble_option(None, 'merge', 'self', 'other'): Choose which collection's preamble to keep. 
            None for neither, self for current collection, other for collection being passed as an 
            argument, and merge for both.
        '''
        new_collection = ItemCollection(new_name)
        new_attributes = OrderedSet([self.attributes[i].copy() for i in range(len(self.attributes))])
        for i in range(len(collection.attributes)):
            new_attributes.add(collection.attributes[i].copy())
        logger.log('debug', "Attribute list {} generated".format([new_attributes[i].name for i in range(len(new_attributes))]))
        new_preamble = self._merge_preambles(collection, preamble_option)
        new_items = {}

        for name, values in self.items.items():
            new_values = values.copy()
            for index, attribute in enumerate(collection.attributes):
                if attribute not in self.attributes:
                    if collection.contains_item(name):
                        new_values.append(collection.items[name][index])
                    else:
                        new_values.append(None)
            new_items[name] = new_values

        for name, values in collection.items.items():
            if not self.contains_item(name):
                used = set()
                new_values = []
                for index, attribute in enumerate(self.attributes):
                    if attribute not in collection.attributes:
                        new_values.append(None)
                    else:
                        new_values.append(collection.items[name][collection.attributes.index(attribute)])
                        used.add(collection.attributes.index(attribute))
                for index, attribute in enumerate(collection.attributes):
                    if index not in used:
                        new_values.append(collection.items[name][index])
                new_items[name] = new_values
                
        new_collection._df.items = new_items
        new_collection._df.attributes = new_attributes
        new_collection._preamble = new_preamble
        return new_collection

    def intersect(self, collection: ItemCollection, new_name: str, preamble_option='merge'):
        '''
        Intersects this collection's with the given collection's items.
        If the same item is contained in both collections, then the item 
        attributes are merged in this collection. Returns a new collection 
        a result

        Args:
        collection(ItemCollection): The other collection to be merged with this one
        new_name(str): The name of the new collection
        preamble_option(None, 'merge', 'self', 'other'): Choose which collection's preamble 
            to keep. None for neither, self for current collection, other for collection being 
            passed as an argument, and merge for both.
        '''
        new_collection = ItemCollection(new_name)
        new_items = dict()
        new_attributes = OrderedSet([self.attributes[i].copy() for i in range(len(self.attributes))])
        new_preamble = self._merge_preambles(collection, preamble_option)
        for attributes in collection.attributes:
            new_attributes.add(attributes.copy())
        # Select items that are contained in both collections
        for name, values in self.items.items():
            if collection.contains_item(name):
                new_items[name] = values.copy()
        # Merge attributes
        used_indexes = set()
        for i in range(len(self.attributes)):
            attribute = self.attributes[i]
            if attribute in collection.attributes:
                used_indexes.add(collection.attributes.index(attribute))
                for name, values in self.items.items():
                    if values[i] == None:
                        values[i] = collection.items[name][collection.index(attribute)]
        for i in range(len(collection.attributes)):
            if i not in used_indexes:
                for name, values in new_items.items():
                    values.append(collection.items[name][i])
        new_collection._df.attributes = new_attributes
        new_collection._df.items = new_items
        new_collection._preamble = new_preamble
        return new_collection

    def copy(self, name: str):
        '''
        Return a deep copy of this collection with the name
        that is passed
        '''
        new_collection = ItemCollection(name)
        new_collection._df.attributes = OrderedSet([self._df.attributes[i].copy() for i in range(len(self.attributes))])
        for item_name, item in self.items.items():
            new_collection._df.items[item_name] = item.copy()
        logger.log('debug', "{} copied to {}".format(self.name, new_collection.name))
        return new_collection

    def wipe(self):
        '''
        Wipe the current ItemCollection. Resetting its ItemCollections and
        attributes. Will keep the same name
        '''
        self._df.items = {}
        self._df.attributes = OrderedSet()
        self._preamble = []

    def from_csv(self, filename: str, start_row=0, start_column=1, non_descriptors=set(), encoding='utf-8-sig', preamble_indexes=None):
        '''
        Remove any data from this ItemCollection and import
        the data from a csv file

        Args:
        filename(str): The name of the csv file
        start_row(int): The start_row containing the name of the attributes. Defaults
            to 0. Anything under this will be assumed to be the items pertaining to 
            the current ItemCollection.
        start_column(int): The start_column containing the start of where the attribute values 
            will be located. Defaults to 0. If give a string, will look for that start_column name 
            and start importing values from that point. This method also assumes that the first 
            start_column of every csv file contains the item names
        non_descriptors(set): The set of names of any attributes that will not be descriptors in the 
            ItemCollection. Defaults to an empty set
        encoding(str): Defaults to 'utf-8-sig'
        preamble_indexes(tuple): A tuple, with the start row of the preamble, and the end row of the preamble. If
            there is no preamble, set to None. Defaults to None
        '''
        self.wipe()
        if '.csv' not in filename: 
            filename += '.csv'
        try:
            with open(filename, newline='') as file:
                data_raw = list(csv.reader(file))
        except FileNotFoundError:
            logger.log('error', "Could not find file {}".format(filename))
            raise FileNotFoundError("Couldn't find file {}".format(filename))
        if preamble_indexes is not None:
            self._import_preamble(data_raw, preamble_indexes, start_row)

        # Check whether the start_column is a string, and find the correct value
        if isinstance(start_column, str):
            counter = 0
            for column in data_raw[start_row]:
                if start_column != column:
                    logger.log('debug', "Read start_column {}, moving to next one".format(start_column))
                    counter += 1
                else:
                    start_column = counter
                    logger.log('debug', "start_column set to {}".format(start_column))
                    break
            if not isinstance(start_column, int):
                logger.log('error', "Could not find start_column {}".format(start_column))
                raise ValueError("Could not find start_column {}".format(start_column))

        for name in data_raw[start_row][start_column:]:
            self._df.attributes.add(Attribute(name, name not in non_descriptors))
        logger.log('debug', "Attributes {} generated".format([self.attributes[i].name for i in range(len(self.attributes))]))
        for arr in data_raw[start_row + 1:]:
            self._df.items[arr[0]] = [item for item in arr[start_column:]]
        logger.log('info', "Imported {} from {}".format(self.name, filename))

    def to_csv(self, filename: str, prune_preamble=True, identifier='Name'):
        '''
        Write to csv file

        Args:
        filename(str): The file to write to
        prune_preamble(bool): If True, trim the preamble to only go to the
            last column containing an attribute. If False, leave as is. Defaults
            to True
        identifier(str): What the header label for the Item names should be called, defaults
            to 'Name'
        '''
        if '.csv' not in filename:
            filename += '.csv'
        if prune_preamble is True and len(self._preamble) > 0:
            self.prune_preamble()
        with open(filename, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for preamble_row in self._preamble:
                csv_writer.writerow([thing for thing in preamble_row])
            csv_writer.writerow([identifier] + [self._df.attributes[i].name for i in range(len(self._df.attributes))])
            for item_name, item in self.items.items():
                csv_writer.writerow([item_name] + 
                [attribute for attribute in item])
            logger.log('info', "{} written to {}".format(self.name, filename))

    def raw(self, excluded_attributes=set(), scale_method=None, weights=None):
        '''
        Return a dict. 'values' contains the raw data of 
        each item in an array. 'item_names' contains the names
        of the items in order. 'attribute_names' contains the name of
        the attributes in order.

        Args:
        excluded_attributes(set): A set of attribute names to exclude. Defaults to the empty set
        scale_method(None, 'robus', 'min_max', 'standard', 'max_abs'): A method to scale the data before it 
            is returned. Defaults to None
        weights(None, 'auto', list): The list of weights if you want to scale the data using weights.
            If 'auto' is selected, generates the data weights for automatically. Defaults to None
        '''
        data = self._df.raw(excluded_attributes=excluded_attributes)
        logger.log('debug', "Raw dict generate {}".format(data))
        if scale_method is not None:  
            data['values'] = scale(scale_method, data['values'])
        if weights is not None:
            if weights == 'auto':
                weights = [pair[1] for pair in pca(self._df, excluded_attributes=excluded_attributes)]
            data['values'] = weighted(data['values'], weights)
        return data

    def descriptive_attributes(self):
        '''
        Return all attributes that are considered desciptors
        '''
        attributes = []
        for attribute in self.attributes:
            if attribute.is_descriptor:
                attributes.append(attribute.name)
        return attributes

    def rename(self, item_name: str, new_name: str):
        '''
        Rename an item

        Args:
        item_name(str): The item that will be renamed
        new_name(str): The new name of the item
        '''
        if new_name in self._df.items:
            logger.log('warn', "Item {} is already stored in Collection {} and will be overwritten".format(new_name, self.name))
        elif item_name not in self._df.items:
            logger.log('error', "Item {} not found in Collection {}, renaming failed".format(item_name, self.name))
        else:
            self._df.items[new_name] = self._df.items.pop(item_name)

    def _import_preamble(self, data_raw, preamble_indexes, start_row):
        if start_row >= preamble_indexes[0] and start_row <= preamble_indexes[1]:
            logger.log('error', "Could not load preamble because indexes given coincided with the start row")
        else:
            for idx in range(preamble_indexes[1] - preamble_indexes[0] + 1):
                preamble_row = []
                for thing in data_raw[idx]:
                    preamble_row.append(thing)
                    logger.log('debug', "Adding {} to {}'s preamble".format(thing, self.name))
                self._preamble.append(preamble_row)

    def _merge_preambles(self, other: ItemCollection, option: str):      
        if option == 'self':
            logger.log('debug', "New preamble will be current preamble")
            return [row.copy() for row in self._preamble]
        elif option == 'other':
            logger.log('debug', "New preamble will other's preamble")
            return [row.copy() for row in other._preamble]
        elif option is None:
            logger.log('debug', "New preamble will be empty")
            return []
        elif option is 'merge':
            logger.log('debug', "New preamble will be merged")
            new_preamble = [row.copy() for row in self._preamble]
            for other_row in other._preamble:
                for self_row in self._preamble:
                    if self_row != other_row:
                        new_preamble.append([thing.copy() for thing in other_row])
            return new_preamble
        else:
            logger.log('error', "Invalid preamble merge option given")
            return []

def load_collection(name, filename: str, **kwargs):
    '''
    Directly load an ItemCollection from a 
    csv file without having to instantiate one

    Args:
    name(str): The name of the collection
    filename(str): The name of the file
    **kwargs: Any arguments that could be passed into 
        the ItemCollection's from_csv() method
    '''
    collection = ItemCollection(name)
    collection.from_csv(filename, **kwargs)
    return collection
