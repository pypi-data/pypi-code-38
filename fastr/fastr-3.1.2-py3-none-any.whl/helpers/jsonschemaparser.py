# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The JSON schema parser validates a json data structure and if possible casts
data to the correct type and fills out default values. The result in a valid
document that can be used to construct objects.
"""

import collections
import copy
import json
import os
import re
import urllib.request, urllib.parse, urllib.error
from urllib.parse import urlparse, urlunparse

import jsonschema.validators
from jsonschema._format import FormatChecker
from jsonschema.exceptions import ValidationError
from jsonschema.compat import iteritems

import fastr
from fastr import exceptions


class FastrRefResolver(jsonschema.RefResolver):
    """
    Adapted version of the RefResolver for handling inter-file references
    more to our liking
    """
    def __init__(self, base_uri, referrer, store=(), cache_remote=True, handlers=()):
        """
        Create a new FastrRefResolver

        :param str base_uri: URI of the referring document
        :param referrer: the actual referring document
        :param dict store: a mapping from URIs to documents to cache
        :param bool cache_remote: whether remote refs should be cached after
            first resolution
        :param dict handlers: a mapping from URI schemes to functions that
            should be used to retrieve them
        """

        handlers = dict(handlers)
        base_uri = urlunparse(['file', '', urllib.request.pathname2url(base_uri), '', '', ''])
        default_handlers = {'': FastrRefResolver.readfile,
                            'fastr': FastrRefResolver.readfastrschema}
        default_handlers.update(handlers)
        super(FastrRefResolver, self).__init__(base_uri, referrer, store, cache_remote, default_handlers)

    @classmethod
    def from_schema(cls, schema, *args, **kwargs):
        """
        Instantiate a RefResolver based on a schema
        """
        default_handlers = {'': FastrRefResolver.readfile,
                            'fastr': FastrRefResolver.readfastrschema}
        if 'handlers' in kwargs:
            handlers = dict(kwargs['handlers'])
            default_handlers.update(handlers)
        kwargs['handlers'] = default_handlers

        return cls(schema.get("id", ""), schema, *args, **kwargs)

    @staticmethod
    def readfile(filename):
        """
        Open a json file based on a simple filename

        :param str filename: the path of the file to read
        :return: the resulting json schema data
        """
        with open(filename, 'r') as fin:
            result = json.load(fin)

        return result

    @staticmethod
    def readfastrschema(name):
        """
        Open a json file based on a fastr:// url that points to a file in the
        fastr.schemadir

        :param str name: the url of the file to open
        :return: the resulting json schema data
        """
        path = urlparse(name).path[1:]
        filename = os.path.join(fastr.config.schemadir, path)
        return FastrRefResolver.readfile(filename)


def _str_to_boolean(value):
    """
    Converts a string to boolean

    :param str value: the string to convert
    :return: the result
    :rtype: bool
    """
    if isinstance(value, str):
        return value.lower() in ['1', 'true']
    else:
        raise TypeError('Expected a string to convert to a boolean, got a {}'.format(type(value).__name__))


def _str_to_list(value):
    """
    Converts a str to a list

    :param str value: string to convert
    :return: the resulting list
    :rtype: list
    """
    return [value]


def _default_to_object(value) -> dict:
    """
    Converts anything to a dict (json object)
    :param value: the value to convert
    :return: the result
    :raises FastrValueError: if the value cannot be converted to a dict in a sensible way
    """
    if isinstance(value, (dict, collections.Mapping)):
        result = dict(value)
    elif hasattr(value, '__getstate__'):
        result = value.__getstate__()
    elif hasattr(value, '__dict__'):
        result = value.__dict__
    else:
        try:
            result = dict(value)
        except ValueError:
            raise exceptions.FastrValueError('Cannot cast {} to a dict'.format(type(value).__name__))

    return result


def _ordereddict_to_array(value):
    """
    Specific conversion from the OrderedDict to a list (json array)
    :param OrderedDict value: the value to convert
    :return: the result
    :rtype: list
    """
    return list(value.values())


def _none_to_array(_):
    """
    Convert a None (json null) to a list (json array)

    :param NoneType _: the value (that is ignored)
    :return: an empty list
    :rtype: list
    """
    return []


# Default casts to get to a datatype
_DEFAULT_TYPECASTS = {
    "array": list,
    "boolean": bool,
    "integer": int,
    "number": float,
    "object": _default_to_object,
    "string": str,
}


# Specific casts to get to a datatype, given by ("targettype", "inputtype"): cast_func
_TYPECASTS = {
    ("array", collections.OrderedDict): _ordereddict_to_array,
    ("array", type(None)): _none_to_array,
    ("array", str): _str_to_list,
    ("boolean", str): _str_to_boolean,
}


def _refer(validator, schema):
    """
    Follow a references in the schema

    :param validator: the json schema validator
    :param dict schema: the current json schema
    :return: the new json schema
    :rtype: dict
    """
    ref = schema.get("$ref")
    if ref is None:
        return schema

    with validator.resolver.resolving(ref) as resolved:
        result = resolved

        if '$ref' in result:
            return _refer(validator, result)
        else:
            return result


def _match_type(validator, instance, schema):
    """
    Match the datatype of and instance with a datatype required by the schema.

    :param validator: Validator used
    :param instance: The instance of the data
    :param dict schema: The schema describing the instance
    :return: the instance in the matched type
    """
    desired_type = schema.get('type')
    if not isinstance(desired_type, list):
        desired_type = [desired_type]

    if not any(validator.is_type(instance, dtype) for dtype in desired_type):
        for dtype in desired_type:
            try:
                try:
                    return _TYPECASTS[dtype, type(instance)](instance)
                except KeyError:
                    return _DEFAULT_TYPECASTS[dtype](instance)
            except (ValueError, TypeError):
                # Not coercible, just hope another will success
                pass
    else:
        return instance


def pattern_properties_prevalid(validator, pattern_properties, instance, schema):
    """
    The pre-validation function for patternProperties

    :param validator: the json schema validator
    :param dict pattern_properties: the current patternProperties
    :param dict instance: the current object instance
    :param dict schema: the current json schema
    """
    if not validator.is_type(instance, "object"):
        return

    properties = set(schema.get('properties', {}).keys())
    pattern_properties = _refer(validator, pattern_properties)

    for key, _ in instance.items():
        if key in properties:
            continue

        for pattern, subschema in iteritems(pattern_properties):
            if not re.match(pattern, key):
                continue

            subschema = _refer(validator, subschema)
            instance[key] = _match_type(validator, instance[key], subschema)

            break


def properties_prevalidate(validator, properties, instance, schema):
    """
    The pre-validation function for properties

    :param validator: the json schema validator
    :param dict properties: the current properties
    :param instance: the current object instance
    :param dict schema: the current json schema
    """
    # All arguments must be used because this function is called like this
    # pylint: disable=unused-argument
    if not validator.is_type(instance, "object"):
        return

    properties = _refer(validator, properties)

    for property_name, subschema in iteritems(properties):
        subschema = _refer(validator, subschema)
        if property_name in instance:
            instance[property_name] = _match_type(validator, instance[property_name], subschema)


def items_prevalidate(validator, items, instance, schema):
    """
    The pre-validation function for items

    :param validator: the json schema validator
    :param dict items: the current items
    :param instance: the current object instance
    :param dict schema: the current json schema
    """
    # All arguments must be used because this function is called like this
    # pylint: disable=unused-argument
    if instance is None:
        return

    if isinstance(items, dict):
        subschema = _refer(validator, items)
        for idx, item in enumerate(instance):
            instance[idx] = _match_type(validator, item, subschema)
    elif isinstance(items, list) and len(items) == len(instance):
        for idx, (item, subschema) in enumerate(zip(instance, items)):
            subschema = _refer(validator, subschema)
            instance[idx] = _match_type(validator, item, subschema)
    else:
        raise ValueError('Expected a list or a tuple notation, found neither: [{}] {}, [{}] {}'.format(
            type(schema).__name__,
            schema,
            type(instance).__name__,
            instance
        ))


def properties_postvalidate(validator, properties, instance, schema):
    """
    # All arguments must be used because this function is called like this
    # pylint: disable=unused-argument
    The post-validation function for properties

    :param validator: the json schema validator
    :param dict properties: the current properties
    :param instance: the current object instance
    :param dict schema: the current json schema
    """
    # All arguments must be used because this function is called like this
    # pylint: disable=unused-argument
    for property_name, subschema in iteritems(properties):
        if instance is None:
            print('wtf? {} / {} -> {}'.format(instance, property_name, subschema))
        if property_name not in instance and "default" in subschema:
            instance[property_name] = subschema["default"]


def one_of_draft4(validator, one_of, instance, schema):
    """
    The one_of directory needs to be done stepwise, because a validation
    even if it fails will try to change types / set defaults etc. Therefore
    we first create a copy of the data per subschema and test if they match.
    Once we found a proper match, we only validate that branch on the real data
    so that only the valid piece of schema will effect the data.

    :param validator: the json schema validator
    :param dict one_of: the current one_of
    :param instance: the current object instance
    :param dict schema: the current json schema
    """
    # All arguments must be used because this function is called like this
    # pylint: disable=unused-argument
    subschemas = enumerate(one_of)
    all_errors = []
    first_valid = {}

    for index, subschema in subschemas:
        temp_instance = copy.deepcopy(instance)
        errs = list(validator.descend(temp_instance, subschema, schema_path=index))
        if not errs:
            first_valid = subschema
            break
        all_errors.extend(errs)
    else:
        # Make sure the reference is available later
        yield ValidationError(
            "%r is not valid under any of the given schemas" % (instance,),
            context=all_errors,
            )

    more_valid = []
    for _, subschema in subschemas:
        temp_instance = copy.deepcopy(instance)
        if validator.is_valid(temp_instance, subschema):
            more_valid.append(subschema)

    if more_valid:
        more_valid.append(first_valid)
        reprs = ", ".join(repr(schema) for schema in more_valid)
        yield ValidationError(
            "%r is valid under each of %s" % (instance, reprs)
        )

    validator.validate(instance, first_valid)


def any_of_draft4(validator, any_of, instance, schema):
    """
    The oneOf directory needs to be done stepwise, because a validation
    even if it fails will try to change types / set defaults etc. Therefore
    we first create a copy of the data per subschema and test if they match.
    Then for all the schemas that are valid, we perform the validation on the
    actual data so that only the valid subschemas will effect the data.

    :param validator: the json schema validator
    :param dict any_of: the current oneOf
    :param instance: the current object instance
    :param dict schema: the current json schema
    """
    # All arguments must be used because this function is called like this
    # pylint: disable=unused-argument
    all_errors = []
    valid_subschemas = []
    for index, subschema in enumerate(any_of):
        temp_instance = copy.deepcopy(instance)
        errs = list(validator.descend(temp_instance, subschema, schema_path=index))

        if not errs:
            valid_subschemas.append((index, subschema))
        else:
            all_errors.extend(errs)

    if len(valid_subschemas) == 0:
        yield ValidationError(
            "%r is not valid under any of the given schemas" % (instance,),
            context=all_errors,
            )
    else:
        for index, subschema in valid_subschemas:
            validator.validate(instance, subschema)


def not_draft4(validator, not_schema, instance, schema):
    """
    The not needs to use a temporary copy of the instance, not to change the
    instance with the invalid schema

    :param validator: the json schema validator
    :param dict not_schema: the current oneOf
    :param instance: the current object instance
    :param dict schema: the current json schema
    """
    # All arguments must be used because this function is called like this
    # pylint: disable=unused-argument

    # Make sure not to change instance
    temp_instance = copy.deepcopy(instance)

    if validator.is_valid(temp_instance, not_schema):
        yield ValidationError(
            "%r is not allowed for %r" % (not_schema, instance)
        )


def extend(validator_cls):
    """
Extend the given :class:`jsonschema.IValidator` with the Seep layer.

"""

    validator_class = jsonschema.validators.extend(
        validator_cls, {
            "anyOf": any_of_draft4,
            "oneOf": one_of_draft4,
            "not": not_draft4
            }
    )

    class Blueprinter(validator_class):
        """
        Class that constructs the data structure based on a JSON schema.
        """
        PREVALIDATORS = collections.OrderedDict()
        POSTVALIDATORS = collections.OrderedDict()

        def __init__(self, uri, schema, types=(), resolver=None, format_checker=None):
            if resolver is None:
                resolver = FastrRefResolver(uri, schema)

            if format_checker is None:
                format_checker = FormatChecker()

            super(Blueprinter, self).__init__(schema=schema,
                                              types=types,
                                              resolver=resolver,
                                              format_checker=format_checker)
            self._stack = []
            self.network = None

        def instantiate(self, data, network=None):
            result = [data]
            self.network = network
            self._stack.append(result)
            self.validate(data)

            if len(result) != 1:
                raise ValueError('Something went wrong!')

            self.network = None
            return result[0]

        def iter_errors(self, instance, _schema=None):
            if _schema is None:
                _schema = self.schema

            with self.resolver.in_scope(_schema.get("id", "")):
                self._stack.append(instance)

                ref = _schema.get("$ref")
                if ref is not None:
                    validators = [("$ref", ref)]
                else:
                    validators = iteritems(_schema)

                # Iterate over PREVALIDATORS so we can control their order
                for k, action in self.PREVALIDATORS.items():
                    if k in _schema:
                        action(self, _schema[k], instance, _schema)

                errors = []
                for k, value in validators:
                    validator = self.VALIDATORS.get(k)
                    if validator is None:
                        continue

                    extra_errors = tuple(validator(self, value, instance, _schema)) or ()

                    for error in extra_errors:
                        # set details if not already set by the called fn
                        error._set(
                            validator=k,
                            validator_value=value,
                            instance=instance,
                            schema=_schema,
                            )
                        if k != "$ref":
                            error.schema_path.appendleft(k)
                        errors.append(error)

                self._stack.pop()

                for error in errors:
                    yield error

                # Iterate over POSTVALIDATORS so we can control their order
                for k, action in self.POSTVALIDATORS.items():
                    if k in _schema:
                        action(self, _schema[k], instance, _schema)

    Blueprinter.PREVALIDATORS['properties'] = properties_prevalidate
    Blueprinter.PREVALIDATORS['patternProperties'] = pattern_properties_prevalid
    Blueprinter.PREVALIDATORS['items'] = items_prevalidate
    Blueprinter.POSTVALIDATORS['properties'] = properties_postvalidate
    return Blueprinter


def getblueprinter(uri, blueprint=None):
    """
Instantiate the given data using the blueprinter.

:argument blueprint: a blueprint (JSON Schema with Seep properties)

"""

    if blueprint is None:
        with open(uri, 'r') as fin:
            try:
                blueprint = json.load(fin)
            except ValueError as exception:
                raise ValueError('{} ({})'.format(exception.args[0], uri))

    validator = jsonschema.validators.validator_for(blueprint)
    blueprinter = extend(validator)(uri, blueprint)
    return blueprinter
