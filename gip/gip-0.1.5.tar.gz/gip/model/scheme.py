import cerberus
from gip import exceptions

models = {
    'locks': {
        'dict': {
            'type': 'dict',
            'keyschema': {
                'type': 'string',
                'regex': '^[0-9a-z-_]+$'  # Regex must match requirements.name
            },
            'valueschema': {
                'type': 'string',
                'regex': '^[0-9a-z]+$'
            },
            'allow_unknown': True
        }
    },
    'requirements': {
        'dict': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type': 'string',
                        'regex': '^[0-9a-z-_]+$',
                        'required': True
                    },
                    'repo': {
                        'type': 'string',
                        'required': True
                    },
                    'type': {
                        'type': 'string',
                        'required': True,
                        'allowed': [
                            'gitlab',
                            'github'
                        ]
                    },
                    'version': {
                        'type': 'string'
                    },
                    'dest': {
                        'type': 'string'
                    }
                }
            }
        }
    }
}


def validate(type, data):
    """
    Validate types against scheme

    :param type: one of the keys in the models dict
    :param data: data to validate against the scheme
    :raise exceptions.ValidationError: if data not valid
    """
    try:
        validator = cerberus.Validator(models[type])
    except KeyError:
        raise exceptions.ValidationError(errors={
            'No matching type found for validation'
        })

    # Add data to dict, Cerberus only works with dicts, not lists
    if validator.validate({'dict': data}):
        return True  # Valid data according to scheme
    else:
        raise exceptions.ValidationError(errors=validator.errors)
