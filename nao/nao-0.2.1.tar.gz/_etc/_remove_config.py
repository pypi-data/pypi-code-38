# -*- coding: utf-8 -*-
"""

The basic concept is to read all valid YAML and make it
a versatile config object based on additional parsing
rules intruduced by nao.

Nao should be able to load every YAML file and make it
available for investigation. Only warnings should be issued
if the structure seems odd.

Multiple sources could be projected on each other using a recursive
dictionary structure as it is done in the normal multivariate inner
structure of nao. For different options see anyconfig parsing.

Every state of the nao object tree should return objects that are
both primitive and versatile. There should be local and global
options for plain retreival of objects. The strange setup of
creating objects that both inherit from nao and the respective
base types (or types marked up in the YAML file - dynamic class
creation) is necessary to be able to provide the same (familiar)
structure of source files upon saving!

Attribute like access is allowed to support easy use of
configuration objects and to keep the dict lookup syntax
for layer activation.

Default filters and default search locations are provided
to be able to use Nao as:

from nao import config
OR
import nao
config = nao.load()
"""
# Copyright (C) 2015 Szabolcs Blaga, see LICENSE
# use Python init script properly

# __all__ = ['Nao', 'SimpleFilter', 'load', 'update']

__version__ = '0.1-dev'

import _yaml

odict = _yaml.odict





def no_transform(key):
    return key

def simple_transform(key):
    return '_'+key

class Filter(object):
    pass

class SimpleFilter(Filter):
    """
    translate between nao keys and yaml map keys e.g. 
    macro  ->  _macro
    en  ->  en_US  

    should be able to build filters dynamically based on the
    actual yaml the ano object loads
    """
    def __init__(self, *keys):
        self._keys = keys

    def __contains__(self, key):
        """Implements key in filter functionality"""
        return key in self._keys

    def key(self, index):
        """should return key for a given index"""
        return self._keys[index-1]

    def index(self, key):
        """should return index for a given key (non zero!)"""
        return self._keys.index(key) + 1
    

class BabelFilter(Filter):
    pass

class UnderscoreFilter(Filter):
    pass



default_filters = [
    SimpleFilter('en', 'hu'),
    ]

def load(source, filters=default_filters):
    """
    TODO
    """
    x = _yaml.load(source)
    log.debug(x)

    return Nao(x)


def update(base, other, recursive=True):
    """
    TODO override addition for this purpose!
    """
    if dictlike(base):
        if recursive:
            recursive_update(base, other)
        else:
            base.update(other)
    else:
        raise AttributeError('Update dictionary like objects only.')

    
def recursive_update(base, other):
    """
    Recursively upadtes base with other. Both should be
    dictionary-like mapping types. 

    Returns None as modifies base in place

    This is a module level function and can be used for
    any dictionary like objects including dict, odict
    and naodict

    TODO: check __instancecheck__ for naodict metaclass
    """
    for key, value in other.iteritems():
        if key in base and dictlike(base[key], value):
            recursive_update(base[key], value)
        else:
            base[key] = value
        

def dictlike(*candidates):
    """checking"""
    for c in candidates:
        if not isinstance(c, (dict, naodict)): return False
    return True


def listlike(*candidates):
    """checking"""
    for c in candidates:
        if not isinstance(c, (list,)): return False
    return True


_registry = {} # for special classes that inherit both Nao and the YAML type



def Nao(object):
    """
    It provides an attribute-like access for iteritems
    and a dict like syntay to activate filters.

    naodict
        items accessed by .item_name
            attribute names shield normal dict methods
            normal methods aliased as _name
        filters activated by [*filter_names]
            this shields normal dict access
        for x in naodict iterates through (k,v) pairs
            it uses dict.iteritems

    naolist
        items accessed by [number]
        filters activated by [*filter_names]
        for x in naolist iterates through values

    naostr
        make it python3 only?

    cascading filter?



    """
    def __init__(self, data,
            filters=default_filters,
            mapping_type=naodict):
        self._mapping_type = mapping_type
        self._filters = filters # should be iterable
        self._data = self._parse(data)

    def __getitem__(self, key):
        """
        Should return self with the proper filters 
        activated. Copying would be very perfomance
        intensive.

        >>> config['en'] 
        # returns the particular tree

        """
        # check key as tuple or slice
        for index, filter in enumerate(self._filters):
            if key in filter:
                self._current = list(self._current)[index] = key


    def update(self, other, recursive=True):
        """
        Updates the whole multilayer structure layer by layer
        """
        dat = self._parse(other)
        recursive_update(self._data, dat, recursive=recursive)

    def load(self, stream):
        self._data = self._parse(_yaml.load(stream))

    def _parse(self, data):
        """
        This is the core of the whole fuss
        """
        base = {} # empty on load

        # walk through od recursively and separate it by filters
        # only listlike or dictlike walked others are considered leaves
        index = tuple([0] * len(self._filters))
        base[index] = self._recursive(base, data, data, index)

        return base


    def _recursive(self, base, initial, current, index):
        """ """
        if dictlike(current):
            dres = self._mapping_type()
            keys = self._getkeys(index)
            for k, v in current.iteritems():
                # decide if it is part of the filter structure
                if self._haskey(k):
                    # check is the given key current search index
                    key = k # TODO transform
                    if key in keys:
                        # let the recursion flow in and SKIP! current level
                        return self._recursive(base, initial, v, index)
                        # SHOULD ISSUE warning if a key passed more than once
                    # new key
                    else:
                        new_index = self._addkey(index, key)
                        # if key is contradictory to the current
                        if new_index is None:
                            log.warning('Contradictory key: %s, after %s' % (key, keys))

                        # new_key is already in self._data
                        elif new_index in self._data:
                            log.warning('Multiple data for: %s' % keys)

                        # else start building form the beginning with new_key
                        else:
                            base[new_index] = self._recursive(base, initial, initial, new_index)

                # continue building the tree
                else:
                    dres[k] = self._recursive(base, initial, v, index)
            return dres

        elif listlike(current):
            return [self._recurse(base, initial, item, index) for item in current]

        else:
            return current


    def _getkeys(self, index):
        return tuple([self._filters[f].key(i) for f, i in enumerate(index)])

    def _haskey(self, key):
        for filter in self._filters:
            if key in filter: return True
        return False

    def _addkey(self, index, key):
        position = None
        for i, filter in enumerate(self._filters):
            if key in filter:
                position = i
                break

        if position is None:
            raise KeyError("Cannot add key : %s" % key)

        # only the default could be modified -> contradictory path
        if index[position] != 0:
            return None

        value = self._filters[position].index(key)
        new_index = list(index)
        new_index[position] = value

        return tuple(new_index)

    def save(self):
        """
        To be implemented
        """
        pass

    def __repr__(self):
        """YAML-like reprezentation """


        


'''
# class storage
_class_registry = {}

def get_class(cls):

    # creating nao capable dynamic classes
    if cls not in _class_registry:
        _class_registry[cls] = type('Nao'+cls.__name__, (Nao, cls), {})

    return _class_registry[cls]


class Nao(object):
    """
    This represents a versatile object

    Multilingual support through BabelFilter

    Representation has both YAML and various database backends

    Nao creates different types on the fly. These classes has some
    extra properties starting with `_nao_`. So ideally as a main rule
    classes with attributes starting with `_nao_` could mess up nao other
    classes are OK.

    Every node could have a value (its original class) and many
    subnodes based on the Nao object. Subnodes exposed through attributes
    unless they hide functionality in that case a warning is issued. This
    makes it more readable e.g. in template usage.

    Active filters could be set through the __getitem__ functionality, so
    nao objects are hiding original __getitem__ functionality by default
    for string keys as the filter names should always be strings.
    """

    def __init__(self, filters=default_filters, allow_attributes=True):
        """
        allow_attributes
            If True string dictionary keys restricted to the non-unicode naming
            conventions of Python variables are exposed as attributes. This has
            a beutifying effect of using Nao objects in certain contexts, e.g.
            templating languages.

        Layers of data organized by filters are stored in _nao_dict with
        a key constructed as a tuple of the index of the keys in each
        filter.

        Filters should have unique keys!
        """
        self._nao_config = {}
        # self._nao_filters = FilterContainer(filters) # share by reference
        self._nao_odict = odict() # copy on filter
        super(Nao, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        """
        Hiding functionality by default for keys that are exist in any filters
        for the object.
        """
        if (
            self._nao_config.getdefault('filters_prevail', True) and
            self._nao_filters.has_key(key)
            ):
            # should replace itself if immutable so need to return a
            # reference to the value (or a copy)
            return self._nao_filter(key) # propagate false?
        else:
            super(Nao, self).__getitem__(self, key)

    def __getattr__(self, key):
        """
        Based on nao settings expose functionality if it is not hiding
        something else. Otherwise nao functionality is only accessible via
        the `_nao_*` names.
        """
        if (
            self._nao_config.getdefault('allow_attributes', True) and
            key in self._nao_odict[self._nao_active]
            ):
            return self._nao_odict[self._nao_active][key]
        else:
            super(Nao, self).__getattr__(self, key)

    def __setattr__(self, key, value):
        """
        Dangerous for two reasons
            could render nao useless
            autosave is very resource intensive
        Need to replace mutable objects
        """
        super(Nao, self).__setattr__(key, value)



    def _nao_filter(self, key, propagate=True):
        """
        Usually called as filter('name') and it propagates through
        the whole tree and sets every object to the corresponding
        value. This means that the immutable nodes should be recreated
        with the Nao object copied over.
        """
        pass

    def _nao_load(self, input):
        """
        read input as YAML and update self
        """
        self.update()

        cls = self.__class__






def dump():
    # dynmically dump if the data changes
    # thread-safety?


def default_language_test_callback(string):
    """decide weather a given string is considered a locale"""


def default_source_list():
    """
    The list of sources that nao implementation tries by default
    to load Nao objects

    `nao.yaml` at the current directory and that file could have
    more information regarding autoload behaviour through
    `_nao` configuration options

    all yaml files stored in the `config` subdirectory
    """


def load(source=default_source_list):
    """
    Create an empty Nao object and call load on import
    """
    return Nao().load(source=source)


class FilterDescriptor(object):
    """
    """
    def __init__(self, names, transform):
        self._names = names
        self._transform = transform

    @property
    def names(self):
        """return those name identifier that are part of this filter"""
        return self._names

    def transform(self, name):
        """
        Mapping betwwen exposed filter names and effective names

        E.g.    names: startswith('_')
            transform: name[1:]
        """
        return self._transform(name)



class BabelFilter(FilterDescriptor):
    """Need to have connection with the Babel package or directly with the CLDR"""
    pass

class SimpleFilter(FilterDescriptor):
    pass


default_filters = {
    #'lang': BabelFilter(),
    # 'flag': SimpleFilter(name_prefix='_')
}





class RecursiveDictionary(dict):
    """RecursiveDictionary provides the methods rec_update and iter_rec_update
    that can be used to update member dictionaries rather than overwriting
    them.

    Created 2009-05-20 by Jannis Andrija Schnitzer (jannis@itisme.org)
    https://gist.github.com/114831
    Modified 2012-12-01 by Szabolcs Blaga (szabolcs@syrus.hu)
    """
    def recurse(self, other, **third):
        """Recursively update the dictionary with the contents of other and
        third like dict.update() does - but don't overwrite sub-dictionaries.

        Example:
        >>> d = RecursiveDictionary({'foo': {'bar': 42}})
        >>> d.rec_update({'foo': {'baz': 36}})
        >>> d
        {'foo': {'baz': 36, 'bar': 42}}
        """
        try:
            iterator = other.iteritems()
        except AttributeError:
            iterator = other
        self.iter_recurse(iterator)
        self.iter_recurse(third.iteritems())

    def iter_recurse(self, iterator):
        for (key, value) in iterator:
            if key in self and isinstance(self[key], dict) and isinstance(value, dict):
                self[key] = RecursiveDictionary(self[key])
                self[key].recurse(value)
                self[key] = dict(self[key]) # avoid using multi-level recursive dictionaries
            else:
                self[key] = value

    def __repr__(self):
        return super(self.__class__, self).__repr__()

"""
config = RecursiveDictionary()
for f in [path(n+'.yaml') for n in ('global', 'local')]:
    if os.path.isfile(f):
        c = yaml.safe_load(codecs.open(f, 'r'))
        if c is not None: config.recurse(c)

config = dict(config)
"""

# this is the default config object and the modul level
# functions are working on this e.g. load, etc.
# nao = Nao(autoload=default_source_list)
# setting modul default based on nao.yaml/nao.yml
# from nao import nao




'''

