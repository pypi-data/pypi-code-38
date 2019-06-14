#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

from collections import defaultdict

from .types import TypedValue


class Dictionary(object):
    D_TYPE_VERTEX = "vertex"
    D_TYPE_TIMESERIES = "timeseries"
    D_TYPE_ALGORITHM = "algorithm"

    D_BASED_VERTEX_TYPE = "vertex_type"
    D_BASED_VERTEX_KEY = "vertex_key"

    # Maintain a static version of the dictionary (so we don't keep on sending updates)
    dictionary = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))
    dictionary_changed = False

    @classmethod
    def reset_dictionary(cls):
        cls.dictionary = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))
        cls.dictionary_changed = False

    @classmethod
    def update_and_strip(cls, dictionary_type, vertex_key, attribute, value):
        """
        Updates the dictionary repository with new meta data, then return a simple value (instead of TypedValue object)

        :param str dictionary_type: Dictionary item type. Either "vertex" or "timeseries"
        :param str vertex_key: Key identifying the vertex owning this attribute (utf-8 encoded)
        :param str attribute: Name of attribute (utf-8 encoded)
        :param value: Value of attribute (if TypedValue, this will be used to extract meta-data)

        :return: The plain value (stripped off TypedValue)
        """
        if isinstance(value, TypedValue):
            cls.update_data_type(dictionary_type=dictionary_type,
                                 vertex_key=vertex_key,
                                 attribute=attribute,
                                 data_type=value.data_type)

            value = value.value

        return value

    @classmethod
    def update_data_type(cls, dictionary_type, attribute, data_type, vertex_type=None, vertex_key=None):
        """
        Updates the dictionary repository with new meta data
        :param str dictionary_type: Dictionary item type. Either "vertex" or "timeseries"
        :param str vertex_type: Vertex type (utf-8 encoded) (preferred over vertex_key)
        :param str vertex_key: Key of vertex owning this attribute (utf-8 encoded) (alternative to vertex_type)
        :param str attribute: Name of attribute (utf-8 encoded)
        :param DataType data_type: data type to set
        """

        meta_data = data_type.meta_data

        if vertex_type:
            # Vertex type is preferred
            current_meta_data = cls.dictionary[cls.D_BASED_VERTEX_TYPE][vertex_type][dictionary_type][attribute]
        else:
            assert vertex_key is not None, "Either vertex_type or vertex_key have to be provided"
            # If vertex_type was not provided, we can register the attribute using vertex key. This will later be
            # converted to vertex type when written to the dictionary
            current_meta_data = cls.dictionary[cls.D_BASED_VERTEX_KEY][vertex_key][dictionary_type][attribute]

        if current_meta_data != meta_data:
            current_meta_data.update(meta_data)
            cls.dictionary_changed = True

    @classmethod
    def update_algorithm(cls, vertex_type, name, meta_data):
        """
        Updates the dictionary repository with new algorithm meta data
        :param str vertex_type: the type of the the vertex
        :param str name: Name of the algorithm
        :param dict meta_data : data type to set
        """

        current_meta_data = cls.dictionary[cls.D_BASED_VERTEX_TYPE][vertex_type]["algorithm"][name]

        if current_meta_data != meta_data:
            current_meta_data.update(meta_data)
            cls.dictionary_changed = True

    @classmethod
    def lookup_algorithm_meta_data(cls, vertex_type, name):
        """
        :return the algorithm meta_data if exist else None

        :param str vertex_type: the type of the the vertex
        :param str name: Name of the algorithm
        :rtype: dict | None
        """

        return cls.dictionary[cls.D_BASED_VERTEX_TYPE].get(vertex_type, {}).get("algorithm", {}).get(name)

    @classmethod
    def flush(cls):
        if cls.dictionary_changed:
            local_dictionary, cls.dictionary = \
                (cls.dictionary, defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))))

            cls.dictionary_changed = False

            return local_dictionary

        else:
            return None
