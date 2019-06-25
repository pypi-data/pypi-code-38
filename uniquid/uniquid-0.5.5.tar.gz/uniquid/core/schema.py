# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

"""JSON Schema definitions."""

NEW_CONTRACT_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'provider': {'type': 'string'},
            'user': {'type': 'string'},
            'functions': {'type': 'array',
                          'items': {'type': 'number'}}
        },
        'required': ['provider', 'user']
    },
    'minItems': 1
}

DELETE_CONTRACT_SCHEMA = {
    'type': 'array',
    'items': {'type': 'string'},
    'minItems': 1
}

NEW_SHARE_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'orgId': {'type': 'string'},
            'xpub': {'type': 'string'}
        },
        'required': ['orgId', 'xpub']
    },
    'minItems': 1
}

DELETE_SHARES_SCHEMA = {
    'type': 'array',
    'items': {'type': 'string'},
    'minItems': 1
}
