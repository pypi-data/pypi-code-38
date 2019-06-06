import copy
from inspect import isfunction
import itertools
from math import inf, pi, e

from deepmerge import Merger
from pyramda import *
from json import dumps


@curry
def prop(key, dct_or_obj):
    """
        Implementation of prop (get_item) that also supports object attributes
    :param key:
    :param dct_or_obj:
    :return:
    """
    # Note that hasattr is a builtin and getattr is a ramda function, hence the different arg position
    if isinstance(dict, dct_or_obj):
        if has(key, dct_or_obj):
            return dct_or_obj[key]
        else:
            raise Exception("No key %s found for dict %s" % (key, dct_or_obj))
    elif isinstance(list, dct_or_obj):
        if isint(key):
            return dct_or_obj[key]
        else:
            raise Exception("Key %s not expected for list type: %s" % (key, dct_or_obj))
    elif isinstance(object, dct_or_obj):
        if hasattr(dct_or_obj, key):
            return getattr(key, dct_or_obj)
        else:
            raise Exception("No key %s found for objects %s" % (key, dct_or_obj))
    else:
        raise Exception("%s is neither a dict nor objects" % dct_or_obj)


@curry
def filter_dict(f, dct):
    """
        Filter a dict
    :param f: lambda or function expecting a tuple (key, value)
    :param dict:
    :return: The filtered dict
    """
    return dict(filter(f, dct.items()))


def all_pass_dict(f, dct):
    """
        Returns true if all dct values pass f
    :param f: binary lambda predicate
    :param dct:
    :return: True or false
    """
    return all(map_with_obj_to_values(
        lambda key, value: f(key, value),
        dct
    ))


def compact_dict(dct):
    """
        Compacts a dct by removing pairs with a None value, meaning 0, None, [], {}, False, etc
    :param dct:
    :return: The filtered dict
    """
    return dict(filter(lambda key_value: key_value[1], dct.items()))


def compact_dict_none(dct):
    """
        Compacts a dct by removing pairs with a None value. Other nil values pass
    :param dct:
    :return: The filtered dict
    """
    return dict(filter(lambda key_value: key_value[1] != None, dct.items()))


@curry
def prop_or(default, key, dct_or_obj):
    """
        Ramda propOr implementation. This also resolves object attributes, so key
        can be a dict prop or an attribute of dct_or_obj
    :param default: Value if dct_or_obj doesn't have key_or_prop or the resolved value is null
    :param key:
    :param dct_or_obj:
    :return:
    """
    # Note that hasattr is a builtin and getattr is a ramda function, hence the different arg position
    if isinstance(dict, dct_or_obj):
        value = dct_or_obj[key] if has(key, dct_or_obj) else default
    elif isinstance(object, dct_or_obj):
        value = getattr(key, dct_or_obj) if hasattr(dct_or_obj, key) else default
    else:
        value = default
    # 0 and False are ok, None defaults
    if value == None:
        return default
    return value


@curry
def prop_eq(key, value, dct):
    """
        Ramda propEq implementation
    :param key:
    :param value:
    :param dct:
    :return: True if dct[key] is non null and equal to value
    """
    return prop_eq_or(False, key, value, dct)


@curry
def prop_eq_or(default, key, value, dct):
    """
        Ramda propEq plus propOr implementation
    :param default:
    :param key:
    :param value:
    :param dct:
    :return:
    """
    return dct[key] and dct[key] == value if key in dct else default


@curry
def prop_eq_or_in(key, value, dct):
    """
        Ramda propEq/propIn
    :param key:
    :param value:
    :param dct:
    :return:
    """
    return prop_eq_or_in_or(False, key, value, dct)


@curry
def prop_eq_or_in_or(default, key, value, dct):
    """
        Ramda propEq/propIn plus propOr
    :param default:
    :param key:
    :param value:
    :param dct:
    :return:
    """
    return has(key, dct) and \
           (dct[key] == value if key in dct else (
               dct[key] in value if isinstance((list, tuple), value) and not isinstance(str, value)
               else default
           ))


@curry
def default_to(default, value):
    """
    Ramda implementation of default_to
    :param default:
    :param value:
    :return:
    """
    return value or default


@curry
def item_path_or(default, keys, dict_or_obj):
    """
    Optional version of item_path with a default value. keys can be dict keys or object attributes, or a combination
    :param default:
    :param keys: List of keys or dot-separated string
    :param dict_or_obj: A dict or obj
    :return:
    """
    if not keys:
        raise ValueError("Expected at least one key, got {0}".format(keys))
    resolved_keys = keys.split('.') if isinstance(str, keys) else keys
    current_value = dict_or_obj
    for key in resolved_keys:
        current_value = prop_or(default, key, default_to({}, current_value))
    return current_value


def isint(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


@curry
def item_path(keys, dict):
    """
        Upgrade pyramda item_path to deal with objects
    :param keys: List of keys into the dict or obj
    :param dict: A dict or obj with attributes containing deep dicts and/or objs
    :return:
    """
    if not keys:
        raise ValueError("Expected at least one key, got {0}".format(keys))
    current_value = dict
    for key in keys:
        current_value = prop(key, current_value)
    return current_value


@curry
def item_str_path(keys, dct):
    """
        Given a string of path segments separated by ., splits them into an array. Int strings are converted
        to numbers to serve as an array index
    :param keys: e.g. 'foo.bar.1.goo'
    :param dct: e.g. dict(foo=dict(bar=[dict(goo='a'), dict(goo='b')])
    :return: The resolved value or an error. E.g. for above the result would be b
    """
    return item_path(map(lambda segment: int(segment) if isint(segment) else segment, keys.split('.')), dct)


@curry
def item_str_path_or(default, keys, dct):
    """
        Given a string of path segments separated by ., splits them into an array. Int strings are converted
        to numbers to serve as an array index
    :param default: Value if any part yields None or undefined
    :param keys: e.g. 'foo.bar.1.goo'
    :param dct: e.g. dict(foo=dict(bar=[dict(goo='a'), dict(goo='b')])
    :return: The resolved value or an error. E.g. for above the result would be b
    """
    return item_path_or(default, map(lambda segment: int(segment) if isint(segment) else segment, keys.split('.')), dct)


@curry
def has(prop, object_or_dct):
    """
    Implementation of ramda has
    :param prop:
    :param object_or_dct:
    :return:
    """
    return prop in object_or_dct if isinstance(dict, object_or_dct) else hasattr(object_or_dct, prop)


@curry
def omit(omit_props, dct):
    """
    Implementation of omit
    :param omit_props:
    :param dct:
    :return:
    """
    return filter_dict(lambda key_value: key_value[0] not in omit_props, dct)


@curry
def omit_deep(omit_props, dct):
    """
    Implementation of omit that recurses. This tests the same keys at every level of dict and in lists
    :param omit_props:
    :param dct:
    :return:
    """

    omit_partial = omit_deep(omit_props)

    if isinstance(dict, dct):
        # Filter out keys and then recurse on each value that wasn't filtered out
        return map_dict(omit_partial, compact_dict(omit(omit_props, dct)))
    if isinstance((list, tuple), dct):
        # run omit_deep on each value
        return map(omit_partial, dct)
    # scalar
    return dct


@curry
def pick_deep(pick_dct, dct):
    """
    Implementation of pick that recurses. This tests the same keys at every level of dict and in lists
    :param pick_dct: Deep dict matching some portion of dct.
    :param dct: Dct to filter. Any key matching pick_dct pass through. It doesn't matter what the pick_dct value
    is as long as the key exists. Arrays also pass through if the have matching values in pick_dct
    :return:
    """

    if isinstance(dict, dct):
        # Filter out keys and then recurse on each value that wasn't filtered out
        return map_with_obj(
            lambda k, v: pick_deep(prop(k, pick_dct), v),
            pick(keys(pick_dct), dct)
        )
    if isinstance((list, tuple), dct):
        # run pick_deep on each value
        return map(
            lambda tup: pick_deep(*tup),
            list(zip(pick_dct or [], dct))
        )
    # scalar
    return dct


@curry
def map_with_obj_deep(f, dct):
    """
    Implementation of map that recurses. This tests the same keys at every level of dict and in lists
    :param f: 2-ary function expecting a key and value and returns a modified value
    :param dct: Dict for deep processing
    :return: Modified dct with matching props mapped
    """
    return _map_deep(lambda k, v: [k, f(k, v)], dct)


@curry
def map_keys_deep(f, dct):
    """
    Implementation of map that recurses. This tests the same keys at every level of dict and in lists
    :param f: 2-ary function expecting a key and value and returns a modified key
    :param dct: Dict for deep processing
    :return: Modified dct with matching props mapped
    """
    return _map_deep(lambda k, v: [f(k, v), v], dct)


def _map_deep(f, dct):
    """
    Used by map_deep and map_keys_deep
    :param map_props:
    :param f: Expects a key and value and returns a pair
    :param dct:
    :return:
    """

    if isinstance(dict, dct):
        return map_key_values(lambda k, v: f(k, _map_deep(f, v)), dct)
    elif isinstance((list, tuple), dct):
        # Call each value with the index as the key. Since f returns a key value discard the key that it returns
        # Even if this is called with map_keys_deep we can't manipulate index values here
        return map(lambda iv: f(iv[0], _map_deep(f, iv[1]))[1], enumerate(dct))
    # scalar
    return dct


@curry
def dict_matches_params_deep(params_dct, dct):
    """
    Filters deeply by comparing dct to filter_dct's value at each depth. Whenever a mismatch occurs the whole
    thing returns false
    :param params_dct: dict matching any portion of dct. E.g. filter_dct = {foo: {bar: 1}} would allow
    {foo: {bar: 1, car: 2}} to pass, {foo: {bar: 2}} would fail, {goo: ...} would fail
    :param dct: Dict for deep processing
    :return: True if all pass else false
    """

    def recurse_if_param_exists(params, key, value):
        """
            If a param[key] exists, recurse. Otherwise return True since there is no param to contest value
        :param params:
        :param key:
        :param value:
        :return:
        """
        return dict_matches_params_deep(
            prop(key, params),
            value
        ) if has(key, params) else True

    def recurse_if_array_param_exists(params, index, value):
        """
            If a param[key] exists, recurse. Otherwise return True since there is no param to contest value
        :param params:
        :param index:
        :param value:
        :return:
        """
        return dict_matches_params_deep(
            params[index],
            value
        ) if isinstance((list, tuple), params_dct) and index < length(params_dct) else True

    if isinstance(dict, dct):
        # Filter out keys and then recurse on each value
        return all_pass_dict(
            # Recurse on each value if there is a corresponding filter_dct[key]. If not we pass
            lambda key, value: recurse_if_param_exists(params_dct, key, value),
            # We shallow merge, giving dct priority with (hopefully) unmatchable values
            merge(map_with_obj(lambda k, v: 1 / (-e * pi), params_dct), dct)
        )

    if isinstance((list, tuple), dct):
        if isinstance((list, tuple), params_dct) and length(dct) < length(params_dct):
            # if there are more param items then dct items fail
            return False
        # run map_deep on each value
        return all(map(
            lambda ivalue: recurse_if_array_param_exists(params_dct, *ivalue),
            enumerate(dct)
        ))
    # scalar. Not that anything not truthy, False, None, 0, are considered equal
    return params_dct == dct


@curry
def join(strin, items):
    """
        Ramda implementation of join
    :param strin:
    :param items:
    :return:
    """
    return strin.join(map(lambda item: str(item), items))


def dump_json(json):
    """
        Returns pretty-printed json
    :param json
    :return:
    """
    return dumps(json, sort_keys=True, indent=4, separators=(',', ': '))


def head(lst):
    """
        Implementation of Ramda's head
    :param lst:
    :return:
    """
    return lst[0] if length(lst) else None


def last(lst):
    """
        Implementation of Ramda's last
    :param lst:
    :return:
    """
    return lst[-1] if length(lst) else None


def tail(lst):
    """
        Implementation of Ramda's tail
    :param lst:
    :return:
    """
    return lst[1:] if length(lst) else []


def init(lst):
    """
        Implementation of Ramda's init, which returns all but the last element of a lit
    :param lst:
    :return:
    """
    return lst[0: -1] if length(lst) else []


@curry
def map_with_obj(f, dct):
    """
        Implementation of Ramda's mapObjIndexed without the final argument.
        This returns the original key with the mapped value. Use map_key_values to modify the keys too
    :param f: Called with a key and value
    :param dct:
    :return {dict}: Keyed by the original key, valued by the mapped value
    """
    f_dict = {}
    for k, v in dct.items():
        f_dict[k] = f(k, v)
    return f_dict


@curry
def map_with_obj_to_values(f, dct):
    """
        Like map_with_obj but just returns the mapped values an array and disgards the keys
    :param f: Called with a key and value
    :param dct:
    :return {list}: values are the mapped value
    """
    return list(values(map_with_obj(f, dct)))


@curry
def map_key_values(f, dct):
    """
        Like map_with_obj but expects a key value pair returned from f and uses it to form a new dict
    :param f: Called with a key and value
    :param dct:
    :return:
    """
    return from_pairs(values(map_with_obj(f, dct)))


@curry
def map_keys(f, dct):
    """
        Calls f with each key of dct, possibly returning a modified key. Values are unchanged
    :param f: Called with each key and returns the same key or a modified key
    :param dct:
    :return: A dct with keys possibly modifed but values unchanged
    """
    f_dict = {}
    for k, v in dct.items():
        f_dict[f(k)] = v
    return f_dict


@curry
def map_keys_with_obj(f, dct):
    """
        Calls f with each key and value of dct, possibly returning a modified key. Values are unchanged
    :param f: Called with each key and value and returns the same key or a modified key
    :param dct:
    :return: A dct with keys possibly modifed but values unchanged
    """
    f_dict = {}
    for k, v in dct.items():
        f_dict[f(k, v)] = v
    return f_dict


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def merge_deep(dct1, dct2, merger=None):
    """
        Deep merge by this spec below
    :param dct1:
    :param dct2:
    :param merger Optional merger
    :return:
    """
    my_merger = merger or Merger(
        # pass in a list of tuples,with the
        # strategies you are looking to apply
        # to each type.
        [
            (list, ["append"]),
            (dict, ["merge"])
        ],
        # next, choose the fallback strategies,
        # applied to all other types:
        ["override"],
        # finally, choose the strategies in
        # the case where the types conflict:
        ["override"]
    )
    return my_merger.merge(dct1, dct2)


def merge_all(dcts):
    """
        Shallow merge all the dcts
    :param dcts:
    :return:
    """
    return reduce(
        lambda accum, dct: merge(accum, dct),
        dict(),
        dcts
    )


def merge_deep_all(dcts):
    """
        Merge deep all dicts using merge_deep
    :param dcts: 
    :return: 
    """""

    return reduce(
        lambda accum, dct: merge_deep(accum, dct),
        dict(),
        dcts
    )


@curry
def merge(dct1, dct2):
    """
        Ramda implmentation of merge
    :param dct1:
    :param dct2:
    :return:
    """
    return merge_dicts(dct1, dct2)


def compact(lst):
    """
        Ramda implmentation of compact. Removes Nones from lst (not 0, etc)
    :param lst:
    :return:
    """
    return filter(lambda x: x is not None, lst)


def compact_empty(lst):
    """
        Ramda implmentation of compact. Removes empty strings
    :param lst:
    :return:
    """
    return filter(lambda x: x != '', lst)


def from_pairs(pairs):
    """
        Implementation of ramda from_pairs Converts a list of pairs or tuples of pairs to a dict
    :param pairs:
    :return:
    """
    return {k: v for k, v in pairs}


def to_pairs(dct):
    """
        Implementation of ramda to_pairs Converts a dict to a list of pairs
    :param dct:
    :return:
    """
    return dct.items()


def flatten(lst):
    """
        Impemenation of ramda flatten
    :param lst:
    :return:
    """
    return list(itertools.chain.from_iterable(lst))


@curry
def concat(lst1, lst2):
    """
        Implmentation of ramda cancat
    :param lst1:
    :param lst2:
    :return:
    """
    return lst1 + lst2


def from_pairs_to_array_values(pairs):
    """
        Like from pairs but combines duplicate key values into arrays
    :param pairs:
    :return:
    """
    result = {}
    for pair in pairs:
        result[pair[0]] = concat(prop_or([], pair[0], result), [pair[1]])
    return result


def fullname(o):
    """
    https://stackoverflow.com/questions/2020014/get-fully-qualified-class-name-of-an-object-in-python
    Return the full name of a class
    :param o:
    :return:
    """
    return o.__module__ + "." + o.__class__.__name__


def length(lst):
    """
    Implementation of Ramda length
    :param lst:
    :return:
    """
    return len(lst)


def isalambda(v):
    """
    Detects if something is a lambda
    :param v:
    :return:
    """
    return isfunction(v) and v.__name__ == '<lambda>'


def map_prop_value_as_index(prp, lst):
    """
        Returns the given prop of each item in the list
    :param prp:
    :param lst:
    :return:
    """
    return from_pairs(map(lambda item: (prop(prp, item), item), lst))


def to_dict_deep(obj, classkey=None):
    """
        Converts an object to a dict deeply
    :param obj:
    :param classkey:
    :return:
    """
    if isinstance(dict, obj):
        data = {}
        for (k, v) in obj.items():
            data[k] = to_dict_deep(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return to_dict_deep(obj._ast())
    elif hasattr(obj, "__iter__") and not isinstance(str, obj):
        return [to_dict_deep(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, to_dict_deep(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj


def flatten_dct_until(obj, until_func, separator):
    """
    Flattens an objects so deep keys and array indices become concatinated strings
    E.g. {a: {b: [1, 3]}} => {'a.b.0': 1, 'a.b.1': 2}
    @param {Object} obj The object to flattened
    @param {Function} until_func stop flattening a line if the this function returns false for the current key
    @param {Object} separator Key segment separator, probably either '.' or '__'
    @returns {Object} The 1-D version of the object
    :param obj:
    :return:
    """
    return from_pairs(_flatten_dct(obj, until_func, separator))


def flatten_dct(obj, separator):
    """
    Flattens an objects so deep keys and array indices become concatinated strings
    E.g. {a: {b: [1, 3]}} => {'a.b.0': 1, 'a.b.1': 2}
    @param {Object} obj The object to flattened
    @param {Object} separator Key segment separator, probably either '.' or '__'
    @returns {Object} The 1-D version of the object
    :param obj:
    :return:
    """
    return from_pairs(_flatten_dct(obj, always(True), separator))


def _flatten_dct(obj, until_func, separator, recurse_keys=[]):
    """

    :param obj:
    :param until_func: Stops recursion on a certain line if the function returns false and the remaining
    value is returned with the key
    :param recurse_keys:
    :return:
    """
    return if_else(
        # If we have something iterable besides a string that is truty
        both(isinstance((dict, list, tuple)), identity),
        # Then recurse on each object or array value. If o is not truthy, meaning {} or [], return
        # a single item dict with the keys and o as the value
        lambda o: compose(
            flatten,
            map_with_obj_to_values(
                lambda k, oo: _flatten_dct(oo, until_func, separator, concat(recurse_keys, [k])) if
                until_func(k) else
                [[join(separator, concat(recurse_keys, [k])), oo]]
            ),
            # Convert lists and tuples to dict where indexes become keys
            if_else(isinstance(dict), identity, list_to_dict)
        )(o),
        # If not an object return a single pair
        lambda o: [[join(separator, recurse_keys), o]]
    )(obj)


def key_string_to_lens_path(key_string):
    """
     Converts a key string like 'foo.bar.0.wopper' to ['foo', 'bar', 0, 'wopper']
 :param {String} keyString The dot-separated key string
 :return {[String]} The lens array containing string or integers
    """
    return map(
        if_else(
            isinstance(int),
            # convert to int
            lambda s: int(s),
            # Leave the string alone
            identity
        ),
        key_string.split('.')
    )


@curry
def fake_lens_path_view(lens_path, obj):
    """
    Simulates R.view with a lens_path since we don't have lens functions
    :param lens_path: Array of string paths
    :param obj: Object containing the given path
    :return: The value at the path or None
    """
    if equals(0, length(lens_path)):
        return obj

    segment = head(lens_path)
    return if_else(
        both(lambda _: identity(segment), has(segment)),
        # Recurse on the rest of the path
        compose(fake_lens_path_view(tail(lens_path)), getitem(segment)),
        # Give up
        lambda _: None
    )(obj)


@curry
def fake_lens_path_set(lens_path, value, obj):
    """
    Simulates R.set with a lens_path since we don't have lens functions
    :param lens_path: Array of string paths
    :param value: The value to set at the lens path
    :param obj: Object containing the given path
    :return: The value at the path or None
    """
    segment = head(lens_path)
    obj_copy = copy.copy(obj)

    def set_array_index(i, v, l):
        # Fill the array with None up to the given index and set the index to v
        try:
            l[i] = v
        except IndexError:
            for _ in range(i - len(l) + 1):
                l.append(None)
            l[i] = v

    if not (length(lens_path) - 1):
        # Done
        new_value = value
    else:
        # Find the value at the path or create a {} or [] at obj[segment]
        found_or_created = item_path_or(
            if_else(
                lambda segment: segment.isnumeric(),
                always([]),
                always({})
            )(head(tail(lens_path))),
            segment,
            obj
        )
        # Recurse on the rest of the path
        new_value = fake_lens_path_set(tail(lens_path), value, found_or_created)

    # Set or replace
    if segment.isnumeric():
        set_array_index(int(segment), new_value, obj_copy)
    else:
        obj_copy[segment] = new_value
    return obj_copy


def unflatten_dct(obj):
    """
    Undoes the work of flatten_dict
    @param {Object} obj 1-D object in the form returned by flattenObj
    @returns {Object} The original 
    :param obj: 
    :return: 
    """

    def reduce_func(accum, key_string_and_value):
        key_string = key_string_and_value[0]
        value = key_string_and_value[1]
        item_key_path = key_string_to_lens_path(key_string)
        # All but the last segment gives us the item container len
        container_key_path = init(item_key_path)
        container = unless(
            # If the path has any length (not []) and the value is set, don't do anything
            both(always(length(container_key_path)), fake_lens_path_view(container_key_path)),
            # Else we are at the top level, so use the existing accum or create a [] or {}
            # depending on if our item key is a number or not
            lambda x: default_to(
                if_else(
                    lambda segment: segment.isnumeric(),
                    always([]),
                    always({})
                )(head(item_key_path))
            )(x)
        )(accum)
        # Finally set the container at the itemLensPath
        return fake_lens_path_set(
            item_key_path,
            value,
            container
        )

    return compose(
        reduce(
            reduce_func,
            # null initial value
            None
        ),
        to_pairs
    )(obj)


def list_to_dict(lst):
    return dict(zip(range(len(lst)), lst))


@curry
def when(if_pred, when_true, obj):
    """
        Ramda when implementation
    :param if_pred:
    :param when_true:
    :param obj:
    :return:
    """
    return if_else(if_pred, when_true, identity, obj)


@curry
def unless(unless_pred, when_not_true, obj):
    """
        Ramda unless implementation
    :param unless_pred:
    :param when_not_true:
    :param obj:
    :return:
    """
    return if_else(unless_pred, identity, when_not_true, obj)
