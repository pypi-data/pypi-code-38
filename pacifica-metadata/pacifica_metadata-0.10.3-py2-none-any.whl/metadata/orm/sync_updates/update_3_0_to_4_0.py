#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Update Schema from 2.0 to 3.0."""
from peewee import ForeignKeyField, TextField, CharField
from playhouse.migrate import SchemaMigrator, migrate
from ..relationships import Relationships
from ..globals import DB


def update_schema():
    """Update schema from 3.0 to 4.0."""
    migrator = SchemaMigrator(DB)
    for table_name in ['keys', 'values', 'groups']:
        migrate(
            migrator.add_column(
                table_name, 'display_name',
                CharField(default='', index=True)
            ),
            migrator.add_column(
                table_name, 'description',
                TextField(default='')
            )
        )
    new_rel_list = [{
        'name': 'upload_required',
        'display_name': 'Required for Upload',
        'description': 'This relationship means that the objects are required for upload to be asserted.'
    }, {
        'name': 'search_required',
        'display_name': 'Required for Search',
        'description': 'This relationship means that the objects are required for search to be asserted.'
    }, {
        'name': 'co_principle_investigator',
        'display_name': 'Co-Principle Investigator',
        'description': 'subject is the co-principle investigator of the object'
    }]
    for new_rel in new_rel_list:
        Relationships.get_or_create(**new_rel)
    rel_obj = Relationships.get(name='upload_required')
    migrate(
        migrator.add_column(
            'instrumentkeyvalue', 'relationship_id',
            ForeignKeyField(Relationships, field=Relationships.uuid, default=rel_obj.uuid)
        )
    )
    DB.execute_sql('alter table instrumentkeyvalue drop constraint instrumentkeyvalue_pkey')
    DB.execute_sql('''
        alter table
            instrumentkeyvalue
        add constraint
            instrumentkeyvalue_pkey primary key (instrument_id, key_id, value_id, relationship_id)
    ''')
