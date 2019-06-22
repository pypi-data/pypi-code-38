import logging

import asyncpg
from guillotina import configure
from guillotina.db.interfaces import IPostgresStorage
from guillotina.db.uid import MAX_UID_LENGTH
from guillotina.db.storages.utils import get_table_definition
from guillotina.interfaces import IDatabaseInitializedEvent

logger = logging.getLogger(__name__)


_aliases_schema = {
    'zoid': (
        f'VARCHAR({MAX_UID_LENGTH}) NOT NULL '
        'REFERENCES objects ON DELETE CASCADE'),
    'container_id': (
        f'VARCHAR({MAX_UID_LENGTH}) NOT NULL '
        'REFERENCES objects ON DELETE CASCADE'),
    'path': 'VARCHAR(2000)',
    'moved': 'BOOLEAN NOT NULL'
}

_links_schema = {
    'source_id': (
        f'VARCHAR({MAX_UID_LENGTH}) NOT NULL '
        'REFERENCES objects ON DELETE CASCADE'),
    'target_id': (
        f'VARCHAR({MAX_UID_LENGTH}) NOT NULL '
        'REFERENCES objects ON DELETE CASCADE')
}


_initialize_statements = [
    'CREATE INDEX IF NOT EXISTS alias_zoid ON aliases (zoid);',
    'CREATE INDEX IF NOT EXISTS alias_container_id ON aliases (container_id);',
    'CREATE INDEX IF NOT EXISTS alias_path ON aliases (path);',
    'CREATE INDEX IF NOT EXISTS alias_moved ON aliases (moved);',
    'CREATE INDEX IF NOT EXISTS link_source_id ON links (source_id);',
    'CREATE INDEX IF NOT EXISTS link_target_id ON links (target_id);',
]


@configure.subscriber(for_=IDatabaseInitializedEvent)
async def initialize(event):
    storage = event.database.storage
    if not IPostgresStorage.providedBy(storage):
        logger.error(
            'Link integrity support only available for '
            'postgresql and cockroachdb')
        return

    statements = [
        get_table_definition(
            'aliases', _aliases_schema, primary_keys=('zoid', 'path')),
        get_table_definition(
            'links', _links_schema, primary_keys=('source_id', 'target_id'))
    ]
    statements.extend(_initialize_statements)
    for statement in statements:
        try:
            async with storage.lock:
                await storage.read_conn.execute(statement)
        except asyncpg.exceptions.UniqueViolationError:
            # this is okay on creation, means 2 getting created at same time
            pass
