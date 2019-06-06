#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Update Schema from 1.0 to 2.0."""
from playhouse.migrate import SchemaMigrator, migrate
from ..globals import DB


def update_schema():
    """Update schema from 1.0 to 2.0."""
    old_table_data = {
        'atoolproposal': {
            'new_name': 'atoolproject',
            'column_rename': {
                'proposal': 'project'
            }
        },
        'citationproposal': {
            'new_name': 'citationproject',
        },
        'proposalgroup': {
            'new_name': 'projectgroup',
        },
        'proposalinstrument': {
            'new_name': 'projectinstrument',
        },
        'proposalparticipant': {
            'new_name': 'projectparticipant',
        },
        'transsip': {},
        'transsap': {}
    }
    migrator = SchemaMigrator(DB)
    migrate(
        migrator.rename_table('proposals', 'projects'),
        migrator.rename_column('projects', 'proposal_type', 'project_type')
    )
    for old_table_name, old_table_value in old_table_data.items():
        if old_table_value.get('new_name', False):
            migrate(
                migrator.rename_table(
                    old_table_name, old_table_value['new_name'])
            )
        new_table_name = old_table_value.get('new_name', old_table_name)
        migrate(
            migrator.rename_column(
                new_table_name,
                'proposal_id',
                'project_id'
            )
        )
        if old_table_value.get('new_name', False):
            for index_meta in DB.get_indexes(new_table_name):
                new_index_name = '{}{}'.format(new_table_name, index_meta.name[len(old_table_name):])
                DB.execute_sql('alter index {} rename to {}'.format(index_meta.name, new_index_name))
        for fkey_meta in DB.get_foreign_keys(new_table_name):
            if not old_table_value.get('new_name', False) and fkey_meta.dest_table != 'projects':
                continue
            if old_table_value.get('new_name', False):
                old_index_prefix = old_table_name
            else:
                old_index_prefix = new_table_name
            if fkey_meta.dest_table == 'projects':
                old_fkey_name = '_'.join([old_index_prefix, 'proposal_id', 'fkey'])
            else:
                old_fkey_name = '_'.join([old_index_prefix, fkey_meta.column, 'fkey'])
            new_fkey_name = '_'.join([new_table_name, fkey_meta.column, 'fkey'])
            DB.execute_sql('alter table {} rename constraint {} TO {}'.format(
                new_table_name, old_fkey_name, new_fkey_name))
