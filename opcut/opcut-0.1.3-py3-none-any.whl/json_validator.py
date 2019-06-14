# pylint: skip-file
import jsonschema


_schemas = {'opcut://logging.yaml#': {'$schema': 'http://json-schema.org/schema#', 'id': 'opcut://logging.yaml#', 'title': 'Logging', 'description': 'Logging configuration', 'type': 'object', 'required': ['version'], 'properties': {'version': {'title': 'Version', 'type': 'integer', 'default': 1}, 'formatters': {'title': 'Formatters', 'type': 'object', 'patternProperties': {'(.)+': {'title': 'Formatter', 'type': 'object', 'properties': {'format': {'title': 'Format', 'type': 'string', 'default': None}, 'datefmt': {'title': 'Date format', 'type': 'string', 'default': None}}}}}, 'filters': {'title': 'Filters', 'type': 'object', 'patternProperties': {'(.)+': {'title': 'Filter', 'type': 'object', 'properties': {'name': {'title': 'Logger name', 'type': 'string', 'default': ''}}}}}, 'handlers': {'title': 'Handlers', 'type': 'object', 'patternProperties': {'(.)+': {'title': 'Handler', 'type': 'object', 'description': 'Additional properties are passed as keyword arguments to\nconstructor\n', 'required': ['class'], 'properties': {'class': {'title': 'Class', 'type': 'string'}, 'level': {'title': 'Level', 'type': 'string'}, 'formatter': {'title': 'Formatter', 'type': 'string'}, 'filters': {'title': 'Filters', 'type': 'array', 'items': {'title': 'Filter id', 'type': 'string'}}}}}}, 'loggers': {'title': 'Loggers', 'type': 'object', 'patternProperties': {'(.)+': {'title': 'Logger', 'type': 'object', 'properties': {'level': {'title': 'Level', 'type': 'string'}, 'propagate': {'title': 'Propagate', 'type': 'boolean'}, 'filters': {'title': 'Filters', 'type': 'array', 'items': {'title': 'Filter id', 'type': 'string'}}, 'handlers': {'title': 'Handlers', 'type': 'array', 'items': {'title': 'Handler id', 'type': 'string'}}}}}}, 'root': {'title': 'Root logger', 'type': 'object', 'properties': {'level': {'title': 'Level', 'type': 'string'}, 'filters': {'title': 'Filters', 'type': 'array', 'items': {'title': 'Filter id', 'type': 'string'}}, 'handlers': {'title': 'Handlers', 'type': 'array', 'items': {'title': 'Handler id', 'type': 'string'}}}}, 'incremental': {'title': 'Incremental configuration', 'type': 'boolean', 'default': False}, 'disable_existing_loggers': {'title': 'Disable existing loggers', 'type': 'boolean', 'default': True}}}, 'opcut://params.yaml#': {'$schema': 'http://json-schema.org/schema#', 'id': 'opcut://params.yaml#', 'type': 'object', 'required': ['cut_width', 'panels', 'items'], 'properties': {'cut_width': {'type': 'number'}, 'panels': {'type': 'object', 'patternProperties': {'(.)+': {'$ref': 'opcut://params.yaml#/definitions/panel'}}}, 'items': {'type': 'object', 'patternProperties': {'(.)+': {'$ref': 'opcut://params.yaml#/definitions/item'}}}}, 'definitions': {'panel': {'type': 'object', 'required': ['width', 'height'], 'properties': {'width': {'type': 'number'}, 'height': {'type': 'number'}}}, 'item': {'type': 'object', 'required': ['width', 'height', 'can_rotate'], 'properties': {'width': {'type': 'number'}, 'height': {'type': 'number'}, 'can_rotate': {'type': 'boolean'}}}}}, 'opcut://result.yaml#': {'$schema': 'http://json-schema.org/schema#', 'id': 'opcut://result.yaml#', 'type': 'object', 'required': ['params', 'used', 'unused'], 'properties': {'params': {'$ref': 'opcut://params.yaml#'}, 'used': {'type': 'array', 'items': {'$ref': 'opcut://result.yaml#/definitions/used'}}, 'unused': {'type': 'array', 'items': {'$ref': 'opcut://result.yaml#/definitions/unused'}}}, 'definitions': {'used': {'type': 'object', 'required': ['panel', 'item', 'x', 'y', 'rotate'], 'properties': {'panel': {'type': 'string'}, 'item': {'type': 'string'}, 'x': {'type': 'number'}, 'y': {'type': 'number'}, 'rotate': {'type': 'boolean'}}}, 'unused': {'type': 'object', 'required': ['panel', 'width', 'height', 'x', 'y'], 'properties': {'panel': {'type': 'string'}, 'width': {'type': 'number'}, 'height': {'type': 'number'}, 'x': {'type': 'number'}, 'y': {'type': 'number'}}}}}, 'opcut://messages.yaml#': {'$schema': 'http://json-schema.org/schema#', 'id': 'opcut://messages.yaml#', 'oneOf': [{'$ref': 'opcut://messages.yaml#/definitions/calculate/request'}, {'$ref': 'opcut://messages.yaml#/definitions/calculate/response'}, {'$ref': 'opcut://messages.yaml#/definitions/generate_output/request'}, {'$ref': 'opcut://messages.yaml#/definitions/generate_output/response'}], 'definitions': {'calculate': {'request': {'type': 'object', 'required': ['params', 'method'], 'properties': {'params': {'$ref': 'opcut://params.yaml#'}, 'method': {'enum': ['GREEDY', 'FORWARD_GREEDY']}}}, 'response': {'type': 'object', 'required': ['result'], 'properties': {'result': {'oneOf': [{'type': 'null'}, {'$ref': 'opcut://result.yaml#'}]}}}}, 'generate_output': {'request': {'type': 'object', 'required': ['result', 'output_type', 'panel'], 'properties': {'result': {'$ref': 'opcut://result.yaml#'}, 'output_type': {'enum': ['PDF', 'SVG']}, 'panel': {'type': ['null', 'string']}}}, 'response': {'type': 'object', 'required': ['data'], 'properties': {'result': {'type': ['string', 'null']}}}}}}}  # NOQA


def validate(data, schema_id):
    """ Validate data with JSON schema

    Args:
       data: validated data
       schema_id (str): JSON schema identificator

    Raises:
       Exception: validation fails

    """
    base_uri = schema_id.split("#")[0] + "#"
    resolver = jsonschema.RefResolver(
        base_uri=base_uri,
        referrer=_schemas[base_uri],
        store=_schemas,
        cache_remote=False)
    jsonschema.validate(
        instance=data,
        schema=resolver.resolve(schema_id)[1],
        resolver=resolver)
