# Basic Flattening Utility
# Author: Spencer Hanson, for Swimlane

from types import *
import re

"""
Flattener file to provide utilites for dealing with messy JSON
"""


class Flattener(object):
    """
    Flattener class to easily flatten JSON
    """

    BASIC_TYPES = (NoneType, TypeType, BooleanType, IntType, LongType, FloatType, ComplexType, FunctionType, LambdaType,
                   GeneratorType, CodeType, ClassType, InstanceType, MethodType, UnboundMethodType, ModuleType,
                   FileType, XRangeType, SliceType, EllipsisType, TracebackType, FrameType, BufferType, DictProxyType,
                   NotImplementedType, GetSetDescriptorType, MemberDescriptorType, StringTypes)

    LIST_TYPES = (TupleType, ListType, set, frozenset)

    DICT_TYPES = DictType

    def combine_list(self, data, key):
        """
        Combine a list or listdict into a dict entry to be flattened.
        combine_list([1,2,3], "a") -> {"a": "1,2,3"}
        combine_list(["A","B"], "test") -> {"test": "A,B"}

        :param data:
        :param key:
        :return:
        """
        if not isinstance(data, list):
            raise Exception("Can't combine non-list!")
        if len(data) > 0 and isinstance(data[0], dict):
            return self.combine_listdict(data)
        else:
            return {key: data}

    def combine_listdict(self, data):
        """
        Combine a listdict into a single dictionary, NOT flattening
        Ex:
        [{"e": f_0, "g": h_0, ..}, {"e": f_1, "g": h_1, ..}] ->
                      c["e"] =  [f0, f1, ...]
                      c["g"] =  [h0, h1, ...]

        :param data: Listdict to combine into a single dictionary
        :return: Combined dictionary
        """
        if not isinstance(data, list) or (len(data) > 0 and not isinstance(data[0], dict)):
            return data  # Can't combine non-listdict, so return base list

        result = {}
        for el in data:
            for k, v in el.iteritems():
                if k in result:
                    if isinstance(v, list):
                        """
                        Special case when:
                        {
                        "a_id": val,
                        "a": {
                            "id": val,
                            "other": [list val]
                        }
                        Collision of sub-listdict and and reformatted superkey lead to two keys being mapped to 'a_id'.
                        One option is to combine like [val1, val2] but can lead to [val, []] which isn't flattened
                        Other option is to extend like [val1].extend([val2]) but those "a_id" and "a": "id" might not be
                         related.
                        Current solution is to take the inner key ("a": "id") and turn it into "a_id_" appending '_'
                        until no collision
                        
                        The "other": [] is required, since the flattening treats "a" like as a dict-list, therefore "id"
                        is turned into a list (until flattening of subdict "a" is complete) which causes this error
                        
                        """
                        is_collision = True
                        new_key = k + "_"
                        while is_collision:
                            if new_key in result:
                                new_key += "_"
                            else:
                                result[new_key] = v
                                is_collision = False
                    else:
                        result[k].append(v)
                else:
                    if isinstance(v, list):
                        result[k] = v
                    else:
                        result[k] = [v]
        return result

    def flatten(self, data, prefix=None, stringify_lists=True, shallow_flatten=False):
        """
        General flattening function
        Method to flatten a dict like or listdict
        Makes the keys lowercase, removes .'s and replaces spaces with underscores

        a["b C.D"] = {"e": f} -> a["b_cd_e"] = f


        All values are basic types of string or integer
        Lists will be flattened into CSV strings
        Works recursively on list-dicts and inner dicts

        :param data: List of dictionaries or dictionary to flatten
        :param prefix: Prefix to add to the data after flattening
        :param stringify_lists: Should we turn lists with basic types into CVSs? Defaults to True
        :param shallow_flatten: Should we ignore the first level of nesting, and only flatten each element within it?
         Used for lists of dictionaries
        :return: Single level dictionary/List of single level dictionaries
        """

        if shallow_flatten:
            return [self.flatten(item, prefix=prefix, stringify_lists=stringify_lists, shallow_flatten=False) for item in data]

        result = None
        is_basictype = False
        if isinstance(data, Flattener.DICT_TYPES):
            result = self.flatten_dict(data, prefix)  # Dict types
        elif isinstance(data, Flattener.LIST_TYPES):

            # Complex list-like types
            result = self.combine_listdict([self.flatten(item, prefix) for item in list(data)])

        elif isinstance(data, Flattener.BASIC_TYPES):
            result = data  # Basic types
            is_basictype = True
        else:
            raise Exception("Don't know how to flatten {}".format(data.__class__))  # Unknown type

        if stringify_lists and not is_basictype:
            if hasattr(result, "iteritems"):
                for k, v in result.iteritems():
                    if isinstance(result[k], list):
                        result[k] = ",".join(unicode(vi) for vi in v)
            else:
                new_result = []
                basictype_list = True  # Is our list something like [1, 2] or ["a", "b"] not [{"a": 1}, "b"]
                for item in iter(result):
                    if not isinstance(item, Flattener.BASIC_TYPES):
                        basictype_list = False

                    if isinstance(item, list):
                        new_result.append(",".join(unicode(vi) for vi in item))
                    else:
                        new_result.append(item)

                if basictype_list:
                    new_result = ",".join([str(el) for el in new_result])

                result = new_result

        return result

    def flatten_dict(self, data, prefix=None):
        flat_dict = {}
        for k, v in data.iteritems():
            k = k.replace('.', '').replace(' ', '_')  # Reformat the key
            k = prefix + "_" + k if prefix else k

            if isinstance(v, dict):  # Dict within dict
                sub_dict = self.flatten_dict(v, prefix=k)
                flat_dict = self.combine_listdict(
                    [flat_dict, sub_dict])  # Combine the flat_dict with the flattened sub_dict

            elif isinstance(v, list):
                flat_els = []
                for el in v:
                    flat_els.append(self.flatten(el, prefix=k))
                flat_dict = self.combine_listdict([flat_dict, self.combine_list(flat_els, k)])
            else:  # Base case, unflattenable value
                flat_dict[k] = v
        return flat_dict


def hoist_key(key, from_list):
    """
    Hoist out a specific key within a given listdict
    Ex: hoist_key("a", [{"a": 1, "b": 4},{"a": 2}, ..]) -> [1,2,3]
    :param key: Key to grab from each dict within the list of dictionaries
    :param from_list: listdict to source from
    :return: list of hoisted values
    """
    hoisted = []
    for element in from_list:
        if key not in element:
            raise Exception("Key {} not found in dict {}".format(key, element))
        hoisted.append(element[key])
    return hoisted


def hoist_keys(key_list, from_list):
    """
    Hoist out a specific keys within a given listdict
    Ex: hoist_keys(["a", "b"], [{"a": 1, "b": 4},{"a": 2, "b": 2, "c": 3}, ..]) ->
    [[all a keys], [all b keys]] -> [[1,2],[4,2]]
    :param key_list: List of keys to hoist from the list of dictionaries
    :param from_list:
    :return: List of the list of hoisted keys
    """
    hoisted = []
    for key in key_list:
        hoisted.append(hoist_key(key, from_list))
    return hoisted


def replace_dict_prefix(prefix, replace_val, from_dict):
    """
    Change a similar prefix on keys within a dict to something else, say 'annoying_stuff_' -> 'a_'
    Ex {"annoying_stuff_important_stuff": "data", "annoying_stuff_asdf": "data2"} ->
    {"a_important_stuff": "data", "a_asdf": "data2"}

    :param prefix: Prefix to replace
    :param replace_val: Prefix to replace with
    :param from_dict: Dictionary to replace prefix on
    :return: Changed from_dict
    """
    for k in from_dict.keys():
        if k.startswith(prefix):
            newk = k.replace(prefix, replace_val, 1)
            if newk in from_dict:
                raise Exception("Can't remove prefix, results in namespace collision!")
            from_dict[newk] = from_dict.pop(k)
    return from_dict


def merge_listdict(data, subdict_data):
    """
    Helper method for flatten_data, used to help flatten recursive list-dicts
    Takes the data of the dict to store the flattened output like {"a": "val1", "b": ...}
    And the value of the subdict with similar keys, like {"a": "val2"}
    Merges the two into a list {"a": ["val1", "val2"], "b": ...}

    :param data: Original data dict
    :param subdict_data: subdict to add to the outer dictionary
    :return: modified data dict
    """
    data_keys = data.keys()
    sub_keys = subdict_data.keys()
    for key in set(data_keys).intersection(sub_keys):  # Keys that they share
        if isinstance(data[key], list):  # Already a list of this object
            data[key].append(subdict_data[key])
        else:  # It isn't a list, so to merge it we must make it into one
            data[key] = [data[key], subdict_data[key]]

    for key in set(sub_keys).difference(data_keys):  # Keys that are in the subdict to preserve data
        data[key] = subdict_data[key]

    return data


def clean_xmltodict_result(data):
    """
    Helper method to clean the output of an xmltodict with messy '#' and '@' trailing
    :param data: dict
    :return: dict
    """
    keys_to_delete = []
    pairs_to_add = []

    for k, v in data.iteritems():
        match = re.match(".*_([@#].*$)", k)  # Ends with _#text or _@property
        if match:
            # Remove the '#' or '@' ie  asdf_@property -> asdf_property
            pairs_to_add.append((k.replace(match.groups()[0], match.groups()[0][1:]), v))
            keys_to_delete.append(k)

    for k in keys_to_delete:
        data.pop(k)

    for k, v in pairs_to_add:
        if k in data:
            raise Exception("Cannot clean {}, results in namespace collision".format(k))
        data[k] = v

    return data
