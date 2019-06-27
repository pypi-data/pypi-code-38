from cc_core.commons.schemas.common import PATTERN_KEY


_files_schema = {
    'type': 'object',
    'patternProperties': {
        PATTERN_KEY: {
            'type': 'object',
            'properties': {
                'isOptional': {'type': 'boolean'},
                'isArray': {'type': 'boolean'},
                'files': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'path': {'type': 'string'},
                            'size': {'type': 'number'},
                            'debugInfo': {'type': 'string'}
                        },
                        'additionalProperties': False,
                        'required': ['path', 'size', 'debugInfo']
                    }
                }
            },
            'additionalProperties': False,
            'required': ['isOptional', 'isArray', 'files']
        }
    },
    'additionalProperties': False
}

# TODO: Incomplete
callback_schema = {
    'type': 'object',
    'properties': {
        'state': {'enum': ['succeeded', 'failed']}
    },
    'additionalProperties': True,
    'required': ['state']
}
