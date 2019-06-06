#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Update Schema from 2.0 to 2.1."""
from playhouse.migrate import SchemaMigrator, migrate
from ..globals import DB


def update_schema():
    """Update schema from 2.0 to 2.1."""
    DB.execute_sql('alter table projects rename constraint proposals_pkey to projects_pkey')
    rename_indexes = {
        'atoolproject_proposal_id': 'atoolproject_project_id',
        'citationproject_proposal_id': 'citationproject_project_id',
        'projectgroup_proposal_id': 'projectgroup_project_id',
        'projectinstrument_proposal_id': 'projectinstrument_project_id',
        'projectparticipant_proposal_id': 'projectparticipant_project_id',
        'proposals_accepted_date': 'projects_accepted_date',
        'proposals_actual_end_date': 'projects_actual_end_date',
        'proposals_actual_start_date': 'projects_actual_start_date',
        'proposals_closed_date': 'projects_closed_date',
        'proposals_created': 'projects_created',
        'proposals_deleted': 'projects_deleted',
        'proposals_short_name': 'projects_short_name',
        'proposals_submitted_date': 'projects_submitted_date',
        'proposals_suspense_date': 'projects_suspense_date',
        'proposals_title': 'projects_title',
        'proposals_updated': 'projects_updated',
        'transsap_proposal_id': 'transsap_project_id',
        'transsip_proposal_id': 'transsip_project_id'
    }
    for old_index, new_index in rename_indexes.items():
        DB.execute_sql('alter index {} rename to {}'.format(old_index, new_index))
    migrator = SchemaMigrator(DB)
    for table_name in ['transsip', 'transsap']:
        for col_name in ['created', 'deleted', 'updated']:
            migrate(migrator.add_index(table_name, (col_name,), False))
