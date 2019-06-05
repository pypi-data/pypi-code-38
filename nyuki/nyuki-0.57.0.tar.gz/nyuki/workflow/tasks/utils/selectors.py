def generate_factory_schema(schema=None, **rules):
    """
    Append custom object properties to the base selector schema.
    """
    if schema is None:
        schema = {'type': 'object'}
    schema['required'] = schema.get('required', []) + ['rules']
    schema['properties'] = {
        **schema.get('properties', {}),
        'rules': {'$ref': '#/definitions/rules'}
    }
    schema['definitions'] = {
        **schema.get('definitions', {}),
        **rules,
        'rules': {
            'type': 'array',
            'items': {
                'oneOf': [{'$ref': '#/definitions/condition-block'}] + [
                    {'$ref': '#/definitions/{}'.format(dtype)}
                    for dtype in rules.keys()
                ]
            }
        },
        'condition-block': {
            'type': 'object',
            'required': ['type', 'conditions'],
            'properties': {
                'type': {'type': 'string', 'enum': ['condition-block']},
                'conditions': {
                    'type': 'array',
                    'items': {
                        'oneOf': [
                            {'$ref': '#/definitions/condition-if'},
                            {'$ref': '#/definitions/condition-else'}
                        ]
                    }
                }
            }
        },
        'condition-if': {
            'type': 'object',
            'required': ['type', 'condition', 'rules'],
            'properties': {
                'type': {'type': 'string', 'enum': ['if', 'elif']},
                'condition': {'type': 'string', 'minLength': 1},
                'rules': {'$ref': '#/definitions/rules'}
            }
        },
        'condition-else': {
            'type': 'object',
            'required': ['type', 'rules'],
            'properties': {
                'type': {'type': 'string', 'enum': ['else']},
                'rules': {'$ref': '#/definitions/rules'}
            }
        }
    }
    return schema
