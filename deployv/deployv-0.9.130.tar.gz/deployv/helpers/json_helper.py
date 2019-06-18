# -*- coding: utf-8 -*-

"""This module provides different methods to easily verify messages to be sure
they are valid json strings and they comply with the json schema.
"""

import os
import logging
import simplejson
import jsonschema
from six import string_types, binary_type


_logger = logging.getLogger(__name__)


def _get_schema_path(name='base.json'):
    """Builds and returns the json schema file used to validate messages.

    Returns false if the file doesn't exist.

    :param name: The name of the json schema, by default is "base.json".
    :type name: str

    :returns: The json schema file name.
    :rtype: str
    """
    schema_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'json_schemas', name)
    if os.path.isfile(schema_file):
        return schema_file
    return False


def build_schema(model=None):
    """Loads the base schema and it extends it with the specified model schema.

    If there is no specified model, or it doesn't have an associated schema,
    it will return the base schema.

    :param model: The model schema name, for example 'deploy.deploy' or 'deploy_deploy'.
    :type model: str or None

    :returns: The model json schema.
    :rtype: dict
    """
    schema = load_json(_get_schema_path())
    model_name = '{model}.json'.format(model=(model or '').replace('.', '_'))
    model_schema_path = _get_schema_path(model_name)
    if model_schema_path:
        model_schema = load_json(model_schema_path)
        schema.get('properties').update(model_schema.get('properties') or {})
        schema.setdefault('definitions', {}).update(model_schema.get('definitions') or {})
    return schema


def load_json(json, logger=True):
    """Loads a valid json string or file into a dictionary, returning the dict
    object.

    :param json: json string to convert.
    :type json: string or dict
    :param logger: when is False, it does not print the error logger. Default True
    :type logger: bool

    :returns: Returns the loaded dict or False if an error ocurred.
    :rtype: dict or bool

    :Example:

    .. code-block:: python

        json_dict = load_json(json_str)
        if isinstance(json_dict, dict):
            _logger.info("Everything OK")
        else:
            _logger.error("Something wrong")

    :Note: Don't check only using ``if json_dict: ...`` because ``"{}"`` is a
        valid json string and will return a valid object, but an empty object
        is considered `falsy` and the check will fail (unless that is what you
        want).
    """
    if isinstance(json, binary_type):
        json = json.decode()
    if isinstance(json, string_types):
        if os.path.isfile(json):
            return load_json_file(json, logger)
        return load_json_string(json, logger)
    if isinstance(json, dict):
        return json
    if logger:
        error_message = "Invalid type ({type})".format(type=type(json))
        _logger.error("Error loading json: %s", error_message)
    return False


def load_json_string(json, logger=True):
    """Loads a valid json string into a dictionary, returning the dict object.

    :param json: json string to convert.
    :type json: string
    :param logger: when is False, it does not print the error logger. Default True
    :type logger: bool

    :returns: Returns the loaded dict or False if an error ocurred.
    :rtype: dict or bool

    :Example:

    .. code-block:: python

        json_dict = load_json_string(json_str)
        if isinstance(json_dict, dict):
            _logger.info("Everything OK")
        else:
            _logger.error("Something wrong")

    :Note: Don't check only using ``if json_dict: ...`` because ``"{}"`` is a
        valid json string and will return a valid object, but an empty object
        is considered `falsy` and the check will fail (unless that is what you
        want).
    """
    _logger.debug(json)
    try:
        return simplejson.loads(json)
    except ValueError as error:
        if logger:
            _logger.error("Error loading json string: %s", str(error))
        return False


def load_json_file(json, logger=True):
    """Loads a valid json file into a dictionary, returning the dict object.

    :param json: json file to load.
    :type json: string
    :param logger: when is False, it does not print the error logger. Default True
    :type logger: bool

    :returns: Returns the loaded dict or False if an error ocurred.
    :rtype: dict or bool

    :Example:

    .. code-block:: python

        json_dict = load_json_file(json_file_name)
        if isinstance(json_dict, dict):
            _logger.info("Everything OK")
        else:
            _logger.error("Something wrong")

    :Note: Don't check only using ``if json_dict: ...`` because ``"{}"`` is a
        valid json string and will return a valid object, but an empty object
        is considered `falsy` and the check will fail (unless that is what you
        want).
    """
    try:
        with open(json) as json_file:
            return load_json_string(json_file.read(), logger)
    except IOError as error:
        if logger:
            _logger.error("Error loading json file %s: %s", json, str(error))
        return False


def validate_schema(json, schema=None):
    """Validates a json against the valid schema, returning if the validation
    went OK and an error message if any errors occurred.

    Documentation for json schema in https://pypi.python.org/pypi/jsonschema

    :param json: json to validate
    :param schema: the schema to apply to the json. If None is passed it will
        get the default schema defined in this module.
    :type json: str or dict
    :type schema: str or dict or None

    :returns: A dict with "result" (a boolean value if the validation was OK) and
        "error" (a string with the error message if an error occurred).
    :rtype: dict

    :Example:

    .. code-block:: python

        validation = json_helper.validate_schema(json)
        if validation.get("error"):
            _logger.error("Something wrong")
        else:
            _logger.info("Everything OK")
    """
    json = load_json(json)
    schema = build_schema() if schema is None else load_json(schema)
    if not isinstance(json, dict) or not isinstance(schema, dict):
        bad_json = "schema" if not isinstance(schema, dict) else "target object"
        return {"error": "Invalid json in {bad}".format(bad=bad_json)}
    try:
        jsonschema.validate(json, schema)
    except jsonschema.ValidationError as error:
        msg_path = " > ".join(str(item) for item in list(error.absolute_path))
        schema_path = " > ".join(str(item) for item in list(error.absolute_schema_path))
        msg = "Error validating the json: {error} (in: {path}) (schema: {schema})".format(
                   error=error.message, path=msg_path, schema=schema_path)
        _logger.error(msg)
        return {"error": msg}
    return {"result": True}


def save_json(info, filename):
    """Save info into Json file.

    :param info: Object to be saved
    :param filename: Name of Json file

    :returns: Absolute path of Json file
    :rtype: str
    """
    try:
        with open(filename, 'w') as fout:
            _logger.debug("Opening file %s", filename)
            simplejson.dump(info, fout, sort_keys=True, indent=4,
                            ensure_ascii=False, separators=(',', ':'))
            if not os.path.isabs(filename):
                filename = os.path.abspath(filename)
            _logger.debug("File saved")
    except IOError as error:
        _logger.error(error)
        return False
    return filename
