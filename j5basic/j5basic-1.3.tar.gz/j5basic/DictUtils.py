#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Implements a case-insensitive (on keys) dictionary and various dictionary functions"""

# Copyright 2002, 2003 St James Software

try:
    from virtualtime import datetime_tz
except ImportError as e:
    datetime_tz = None

import datetime
import six

_DUMMY_ARG_ = object()

def unique_items(list1):
    """generates unique hashable items in list1, in the same order they were given in"""
    seen = set()
    for item in list1:
        if item not in seen:
            seen.add(item)
            yield item

def assert_dicts_equal(dict1,dict2, datetimes_to_naive=False):
    """tests equality of two dicts"""
    k1, k2 = set(dict1.keys()), set(dict2.keys())

    assert k1 == k2
    for key in k1:
        if datetimes_to_naive and isinstance(dict1[key], datetime.datetime) and isinstance(dict2[key], datetime.datetime):
            assert datetime_tz
            assert (datetime_tz.localize(dict1[key]), key) == (datetime_tz.localize(dict2[key]), key)
        else:
            # this assert means we get the key if the assert fails
            assert (dict1[key], key) == (dict2[key], key)

def assert_dicts_not_equal(dict1,dict2):
    """tests two dicts are not equal"""
    k1, k2 = list(dict1.keys()), list(dict2.keys())
    k1.sort()
    k2.sort()

    if k1 == k2:
        for key in k1:
            if (dict1[key], key) != (dict2[key], key):
                return
        assert False, (k1, k2)

def filterdict(origdict, keyset):
    """returns the subset of origdict containing only the keys in keyset and their corresponding values """
    newdict = {}
    # this cunningly works with cidict (case-insensitive dictionary class)
    # since we just check if key in origdict, not the reverse...
    # the keys are those from keyset, not origdict
    for key in keyset:
        if key in origdict:
            newdict[key] = origdict[key]
    return newdict

def subtractdicts(ldict, rdict):
    """returns a dictionary containing those keys&values in ldict that aren't in rdict or differ from rdict"""
    diffdict = {}
    for key in ldict:
        if key in rdict:
            lvalue, rvalue = ldict[key], rdict[key]
            # type mismatch doesn't count if both are str/unicode
            if (type(lvalue) != type(rvalue)) and not (type(lvalue) in (six.text_type, six.binary_type) and type(rvalue) in (six.text_type, six.binary_type)):
                diffdict[key] = lvalue
            elif type(lvalue) != type(rvalue):
                # handle str/unicode mismatch
                if type(lvalue) == six.binary_type: lvaluecmp = lvalue.decode('UTF-8')
                else: lvaluecmp = lvalue
                if type(rvalue) == six.binary_type: rvaluecmp = rvalue.decode('UTF-8')
                else: rvaluecmp = rvalue
                if lvaluecmp != rvaluecmp:
                    diffdict[key] = lvalue
            elif lvalue != rvalue:
                diffdict[key] = lvalue
        else:
            diffdict[key] = ldict[key]
    return diffdict

def merge_dicts(dict1, *dicts):
    """returns a dictionary consisting of all the dicts, overriding key values in the order they're passed in"""
    merged = dict1.copy()
    for d in dicts:
        merged.update(d)
    return merged

def mapdict(thedict, keymap=None, valuemap=None):
    """ returns a dictionary with the keys mapped using keymap, the values using valuemap """
    if keymap is None:
        if valuemap is None:
            return thedict
        else:
            return dict([(key, valuemap(value)) for key, value in thedict.items()])
    else:
        if valuemap is None:
            return dict([(keymap(key), value) for key, value in thedict.items()])
        else:
            return dict([(keymap(key), valuemap(value)) for key, value in thedict.items()])

def generalupper(str):
    """this uses the object's upper method - works with string and unicode"""
    if str is None: return str
    return str.upper()

def upperkeys(thedict):
    return mapdict(thedict, generalupper, None)

class cidict(dict):
    def __init__(self, fromdict = None):
        """constructs the cidict, optionally using another dict to do so"""
        if fromdict is not None:
            self.update(fromdict)

    def __getitem__(self, key):
        if type(key) != str and type(key) != str:
            raise TypeError("cidict can only have str or unicode as key (got %r)" % type(key))
        for akey in self.keys():
            if akey.lower() == key.lower():
                return dict.__getitem__(self, akey)
        raise IndexError

    def __setitem__(self, key, value):
        if type(key) != str and type(key) != str:
            raise TypeError("cidict can only have str or unicode as key (got %r)" % type(key))
        for akey in self.keys():
            if akey.lower() == key.lower():
                return dict.__setitem__(self, akey, value)
        return dict.__setitem__(self, key, value)

    def update(self, _updatedict=_DUMMY_ARG_, **kwargs):
        """D.update(E) -> None.  Update D from E: for k in E.keys(): D[k] = E[k]"""
        if _updatedict == _DUMMY_ARG_:
            pass
        elif hasattr(_updatedict, "keys"):
            for key in list(_updatedict.keys()):
                self[key] = _updatedict[key]
        else:
            for key, value in _updatedict:
                self[key] = value
        for key in kwargs:
            self[key] = kwargs[key]

    def __delitem__(self, key):
        if type(key) != str and type(key) != str:
            raise TypeError("cidict can only have str or unicode as key (got %r)" % type(key))
        for akey in self.keys():
            if akey.lower() == key.lower():
                return dict.__delitem__(self, akey)
        raise IndexError

    def __contains__(self, key):
        if type(key) != str and type(key) != str:
            raise TypeError("cidict can only have str or unicode as key (got %r)" % type(key))
        for akey in self.keys():
            if akey.lower() == key.lower():
                return 1
        return 0

    def has_key(self, key):
        return self.__contains__(key)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

class ordereddict(dict):
    """a dictionary which remembers its keys in the order in which they were given"""
    def __init__(self, *args):
        if len(args) == 0:
            super(ordereddict, self).__init__()
            self.order = []
        elif len(args) > 1:
            raise TypeError("ordereddict() takes at most 1 argument (%d given)" % len(args))
        else:
            initarg = args[0]
            super(ordereddict, self).__init__(*args)
            if hasattr(initarg, "keys"):
                self.order = list(initarg.keys())
            else:
                # danger: could have duplicate keys...
                self.order = []
                checkduplicates = {}
                for key, value in initarg:
                    if not key in checkduplicates:
                        self.order.append(key)
                        checkduplicates[key] = None

    def __setitem__(self, key, value):
        alreadypresent = key in self
        result = dict.__setitem__(self, key, value)
        if not alreadypresent: self.order.append(key)
        return result

    def setdefault(self, key, default):
        """D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D"""
        if key in self:
            return self[key]
        else:
            self[key] = default
            return self[key]

    def update(self, _updatedict=_DUMMY_ARG_, **kwargs):
        """D.update(E) -> None.  Update D from E: for k in E.keys(): D[k] = E[k]"""
        if _updatedict == _DUMMY_ARG_:
            pass
        elif hasattr(_updatedict, "keys"):
            for key in list(_updatedict.keys()):
                self[key] = _updatedict[key]
        else:
            for key, value in _updatedict:
                self[key] = value
        for key in kwargs:
            self[key] = kwargs[key]

    def __delitem__(self, key):
        alreadypresent = key in self
        result = dict.__delitem__(self, key)
        if alreadypresent: self.order.remove(key)
        return result

    def copy(self):
        """D.copy() -> a shallow copy of D"""
        thecopy = ordereddict(super(ordereddict, self).copy())
        thecopy.order = self.order[:]
        return thecopy

    def items(self):
        """D.items() -> list of D's (key, value) pairs, as 2-tuples"""
        return [(key, self[key]) for key in self.order]

    def iteritems(self):
        """D.iteritems() -> an iterator over the (key, value) items of D"""
        for key in self.order:
            yield (key, self[key])

    def iterkeys(self):
        """D.iterkeys() -> an iterator over the keys of D"""
        for key in self.order:
            yield key

    __iter__ = iterkeys

    def itervalues(self):
        """D.itervalues() -> an iterator over the values of D"""
        for key in self.order:
            yield self[key]

    def keys(self):
        """D.keys() -> list of D's keys"""
        return self.order[:]

    def values(self):
        """D.values() -> lif of D's values (in the same order as D.keys())"""
        return [self[key] for key in self.order]

    def popitem(self):
        """D.popitem() -> (k, v), remove and return some (key, value) pair as a 2-tuple; but raise KeyError if D is empty"""
        if len(self.order) == 0:
            raise KeyError("popitem(): ordered dictionary is empty")
        k = self.order[-1]
        v = self[k]
        del self[k]
        return (k,v)

    def pop(self, k, v=_DUMMY_ARG_):
        if v == _DUMMY_ARG_:
            v = dict.pop(self, k)
        else:
            v = dict.pop(self, k, v)
        if k in self.order:
            self.order.remove(k)
        return v

    def clear(self):
        dict.clear(self)
        self.order = []

class attrdict(dict):
    """Dictionary that also allows access to keys using attributes"""
    def set_default_value(self, default_value):
        """sets a default value that will be returned for missing attributes"""
        self.__dict__["__default__"] = default_value

    def __getattr__(self, attr):
        """Looks up attributes in the dictionary keys, returning the default only if set"""
        if attr in self:
            return self[attr]
        elif "__default__" in self.__dict__:
            return self.__dict__["__default__"]
        else:
            raise AttributeError("Attribute %s not found" % attr)

class setattrdict(attrdict):
    def __setattr__(self, attr, value):
        """Sets the attribute by setting the value in the dictionary"""
        self[attr] = value

_non_attribifyable_classes = set()
def do_not_attribify(clazz):
    global _non_attribifyable_classes
    _non_attribifyable_classes.add(clazz)

def _can_attribify(o):
    global _non_attribifyable_classes
    for c in _non_attribifyable_classes:
        if isinstance(o, c):
            return False
    return True

def attribify(context, modifiable=False):
    """takes a set of nested dictionaries and converts them into attrdicts. Also searches through lists"""
    # We shouldn't convert Config nodes
    if isinstance(context, dict) and not isinstance(context, attrdict) and _can_attribify(context):
        newcontext = (attrdict if not modifiable else setattrdict)(context)
        for key, value in list(newcontext.items()):
            if isinstance(value, (dict, list)):
                newcontext[key] = attribify(value)
        return newcontext
    elif isinstance(context, list):
        for n, item in enumerate(context):
            if isinstance(item, (dict, list)):
                context[n] = attribify(item)
        return context
    else:
        return context

