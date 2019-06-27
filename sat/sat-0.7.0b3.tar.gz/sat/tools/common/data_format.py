#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" tools common to backend and frontends """
#  FIXME: json may be more appropriate than manual serialising like done here

from sat.core import exceptions
import json


def dict2iter(name, dict_, pop=False):
    """iterate into a list serialised in a dict

    name is the name of the key.
    Serialisation is done with [name] [name#1] [name#2] and so on
    e.g.: if name is 'group', keys are group, group#1, group#2, ...
    iteration stop at first missing increment
    Empty values are possible
    @param name(unicode): name of the key
    @param dict_(dict): dictionary with the serialised list
    @param pop(bool): if True, remove the value from dict
    @return iter: iterate through the deserialised list
    """
    if pop:
        get = lambda d, k: d.pop(k)
    else:
        get = lambda d, k: d[k]

    try:
        yield get(dict_, name)
    except KeyError:
        return
    else:
        idx = 1
        while True:
            try:
                yield get(dict_, u"{}#{}".format(name, idx))
            except KeyError:
                return
            else:
                idx += 1


def dict2iterdict(name, dict_, extra_keys, pop=False):
    """like dict2iter but yield dictionaries

    params are like in [dict2iter], extra_keys is used for extra dict keys.
    e.g. dict2iterdict(comments, mb_data, ('node', 'service')) will yield dicts like:
        {u'comments': u'value1', u'node': u'value2', u'service': u'value3'}
    """
    #  FIXME: this format seem overcomplicated, it may be more appropriate to use json here
    if pop:
        get = lambda d, k: d.pop(k)
    else:
        get = lambda d, k: d[k]
    for idx, main_value in enumerate(dict2iter(name, dict_, pop=pop)):
        ret = {name: main_value}
        for k in extra_keys:
            ret[k] = get(
                dict_, u"{}{}_{}".format(name, (u"#" + unicode(idx)) if idx else u"", k)
            )
        yield ret


def iter2dict(name, iter_, dict_=None, check_conflict=True):
    """Fill a dict with values from an iterable

    name is used to serialise iter_, in the same way as in [dict2iter]
    Build from the tags a dict using the microblog data format.

    @param name(unicode): key to use for serialisation
        e.g. "group" to have keys "group", "group#1", "group#2", ...
    @param iter_(iterable): values to store
    @param dict_(None, dict): dictionary to fill, or None to create one
    @param check_conflict(bool): if True, raise an exception in case of existing key
    @return (dict): filled dict, or newly created one
    @raise exceptions.ConflictError: a needed key already exists
    """
    if dict_ is None:
        dict_ = {}
    for idx, value in enumerate(iter_):
        if idx == 0:
            key = name
        else:
            key = u"{}#{}".format(name, idx)
        if check_conflict and key in dict_:
            raise exceptions.ConflictError
        dict_[key] = value
    return dict


def getSubDict(name, dict_, sep=u"_"):
    """get a sub dictionary from a serialised dictionary

    look for keys starting with name, and create a dict with it
    eg.: if "key" is looked for, {'html': 1, 'key_toto': 2, 'key_titi': 3} will return:
        {None: 1, toto: 2, titi: 3}
    @param name(unicode): name of the key
    @param dict_(dict): dictionary with the serialised list
    @param sep(unicode): separator used between name and subkey
    @return iter: iterate through the deserialised items
    """
    for k, v in dict_.iteritems():
        if k.startswith(name):
            if k == name:
                yield None, v
            else:
                if k[len(name)] != sep:
                    continue
                else:
                    yield k[len(name) + 1 :], v

def serialise(data):
    """Serialise data so it can be sent to bridge

    @return(unicode): serialised data, can be transmitted as string to the bridge
    """
    return json.dumps(data, ensure_ascii=False, default=unicode)

def deserialise(serialised_data, default=None, type_check=dict):
    """Deserialize data from bridge

    @param serialised_data(unicode): data to deserialise
    @default (object): value to use when serialised data is empty string
    @param type_check(type): if not None, the deserialised data must be of this type
    @return(object): deserialised data
    @raise ValueError: serialised_data is of wrong type
    """
    if serialised_data == u"":
        return default
    ret = json.loads(serialised_data)
    if type_check is not None and not isinstance(ret, type_check):
        raise ValueError(u"Bad data type, was expecting {type_check}, got {real_type}"
            .format(type_check=type_check, real_type=type(ret)))
    return ret
