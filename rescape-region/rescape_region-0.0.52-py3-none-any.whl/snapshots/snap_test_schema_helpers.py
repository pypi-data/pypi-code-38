# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['SchemaHelpersTypeCase::test_merge_with_django_properties 1'] = {
    'date_joined': {
        'create': 'deny',
        'type': 'DateTime',
        'update': 'deny'
    },
    'email': {
        'create': [
            'require'
        ],
        'type': 'String'
    },
    'first_name': {
        'create': 'require',
        'type': 'String'
    },
    'id': {
        'create': 'deny',
        'type': 'Int',
        'unique': [
            'primary',
            'unique'
        ],
        'update': [
            'require'
        ]
    },
    'is_active': {
        'type': 'Boolean'
    },
    'is_staff': {
        'type': 'Boolean'
    },
    'is_superuser': {
        'type': 'Boolean'
    },
    'last_name': {
        'create': 'require',
        'type': 'String'
    },
    'password': {
        'create': [
            'require'
        ],
        'read': 'deny',
        'type': 'String'
    },
    'username': {
        'create': [
            'require'
        ],
        'type': 'String',
        'unique': [
            'unique'
        ]
    }
}

snapshots['SchemaHelpersTypeCase::test_merge_with_django_properties 2'] = {
    'created_at': {
        'type': 'DateTime'
    },
    'data': {
        'fields': {
            'example': {
                'type': 'Float'
            },
            'friend': {
                'fields': {
                    'id': {
                        'create': 'require',
                        'type': 'Int',
                        'unique': [
                            'primary',
                            'unique',
                            'primary',
                            'unique',
                            'primary',
                            'unique',
                            'primary',
                            'unique'
                        ]
                    }
                },
                'graphene_type': 'UserType',
                'type': 'UserType'
            }
        },
        'graphene_type': 'FooDataType',
        'type': 'related_input_field_for_crud_type'
    },
    'key': {
        'create': 'require',
        'type': 'String',
        'unique': [
            'unique'
        ]
    },
    'name': {
        'create': 'require',
        'type': 'String'
    },
    'updated_at': {
        'type': 'DateTime'
    },
    'user': {
        'django_type': 'User',
        'fields': {
            'id': {
                'create': 'require',
                'type': 'Int',
                'unique': [
                    'primary',
                    'unique',
                    'primary',
                    'unique',
                    'primary',
                    'unique',
                    'primary',
                    'unique'
                ]
            }
        },
        'graphene_type': 'UserType',
        'type': 'related_input_field_for_crud_type'
    }
}

snapshots['SchemaHelpersTypeCase::test_create_fields 1'] = [
    'username',
    'password',
    'email',
    'is_superuser',
    'first_name',
    'last_name',
    'is_staff',
    'is_active'
]

snapshots['SchemaHelpersTypeCase::test_create_fields 2'] = [
    'key',
    'name',
    'created_at',
    'updated_at',
    'data',
    'user'
]

snapshots['SchemaHelpersTypeCase::test_query_fields 1'] = [
    'id',
    'username',
    'email',
    'is_superuser',
    'first_name',
    'last_name',
    'is_staff',
    'is_active',
    'date_joined'
]

snapshots['SchemaHelpersTypeCase::test_query_fields 2'] = [
    'key',
    'name',
    'created_at',
    'updated_at',
    'data',
    'user'
]

snapshots['SchemaHelpersTypeCase::test_update_fields 1'] = [
    'id',
    'username',
    'password',
    'email',
    'is_superuser',
    'first_name',
    'last_name',
    'is_staff',
    'is_active'
]

snapshots['SchemaHelpersTypeCase::test_update_fields 2'] = [
    'key',
    'name',
    'created_at',
    'updated_at',
    'data',
    'user'
]

snapshots['SchemaHelpersTypeCase::test_update_fields_for_create_or_update 1'] = {
    'defaults': {
        'email': 'dino@barn.farm',
        'first_name': 'T',
        'last_name': 'Rex',
        'password': 'pbkdf2_sha256$100000$not_random$kd71bQn3ng/uGJ/MfuNbDORGyd6XCsWpTCdFOtr+5F0='
    },
    'username': 'dino'
}

snapshots['SchemaHelpersTypeCase::test_update_fields_for_create_or_update 2'] = {
    'defaults': {
        'data': {
            'example': 2.2
        },
        'name': 'Foo Name',
        'user_id': 5
    },
    'key': 'fooKey'
}
