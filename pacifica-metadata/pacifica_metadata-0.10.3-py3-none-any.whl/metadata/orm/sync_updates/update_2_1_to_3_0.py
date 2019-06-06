#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Update Schema from 2.0 to 3.0."""
import uuid
from peewee import ForeignKeyField, UUIDField, Model, CompositeKey, DateTimeField
from playhouse.migrate import SchemaMigrator, migrate
from ..relationships import Relationships
from ..instruments import Instruments
from ..keys import Keys
from ..values import Values
from ..transaction_user import TransactionUser
from ..data_sources import DataSources
from ..instrument_data_source import InstrumentDataSource
from ..globals import DB


def _rename_columns():
    column_rename = {
        'contributors': {'person_id': 'user_id'},
        'institutionuser': {'person_id': 'user_id'},
        'instrumentuser': {'custodian_id': 'user_id'},
        'projectuser': {'person_id': 'user_id'},
        'transactionuser': {'authorized_person_id': 'user_id'}
    }
    migrator = SchemaMigrator(DB)
    for table_name, column_tre in column_rename.items():
        for old_name, new_name in column_tre.items():
            migrate(migrator.rename_column(table_name, old_name, new_name))
            old_fkey_name = '_'.join([table_name, old_name, 'fkey'])
            new_fkey_name = '_'.join([table_name, new_name, 'fkey'])
            DB.execute_sql('alter table {} rename constraint {} TO {}'.format(table_name, old_fkey_name, new_fkey_name))
            old_index_name = '_'.join([table_name, old_name])
            new_index_name = '_'.join([table_name, new_name])
            DB.execute_sql('alter index {} rename to {}'.format(old_index_name, new_index_name))


def _rename_tables():
    table_rename = {
        'institutionperson': 'institutionuser',
        'instrumentcustodian': 'instrumentuser',
        'projectparticipant': 'projectuser',
        'transactionrelease': 'transactionuser'
    }
    migrator = SchemaMigrator(DB)
    for old_table, new_table in table_rename.items():
        migrate(migrator.rename_table(old_table, new_table))
        for index_meta in DB.get_indexes(new_table):
            new_index_name = '{}{}'.format(new_table, index_meta.name[len(old_table):])
            DB.execute_sql('alter index {} rename to {}'.format(index_meta.name, new_index_name))
        for fkey_meta in DB.get_foreign_keys(new_table):
            old_name = '_'.join([old_table, fkey_meta.column, 'fkey'])
            new_name = '_'.join([new_table, fkey_meta.column, 'fkey'])
            DB.execute_sql('alter table {} rename constraint {} TO {}'.format(new_table, old_name, new_name))


def _create_tables():
    class OldInstKeyValue(Model):
        """This is the original Instrument Key Value object."""

        instrument = ForeignKeyField(Instruments)
        key = ForeignKeyField(Keys)
        value = ForeignKeyField(Values)
        created = DateTimeField(index=True)
        updated = DateTimeField(index=True)
        deleted = DateTimeField(index=True, null=True)

        # pylint: disable=too-few-public-methods
        class Meta(object):
            """PeeWee meta class contains the database and the primary key."""

            database = DB
            primary_key = CompositeKey('instrument', 'key', 'value')
            table_name = 'instrumentkeyvalue'
            legacy_table_names = False
    Relationships.create_table()
    DataSources.create_table()
    InstrumentDataSource.create_table()
    OldInstKeyValue.create_table()


# pylint: disable=too-many-locals
def _add_relationship_columns():
    table_rel = {
        'institutionuser': ('member_of', 'institution_user', ('institution_id', 'user_id')),
        'instrumentuser': ('custodian', 'instrument_user', ('instrument_id', 'user_id')),
        'projectuser': ('member_of', 'project_user', ('project_id', 'user_id')),
        'projectinstrument': ('member_of', 'project_instrument', ('instrument_id', 'project_id')),
        'transactionuser': ('authorized_releaser', 'transaction_user', ('transaction_id', 'user_id'))
    }
    migrator = SchemaMigrator(DB)
    DB.execute_sql('alter table citationtransaction drop constraint citationtransaction_transaction_id_fkey')
    DB.execute_sql('drop index citationtransaction_transaction_id')
    DB.execute_sql('alter table doitransaction drop constraint doitransaction_transaction_id_fkey')
    DB.execute_sql('drop index doitransaction_transaction_id')
    migrate(
        migrator.rename_column('citationtransaction', 'transaction_id', 'trans_old_id'),
        migrator.rename_column('doitransaction', 'transaction_id', 'trans_old_id')
    )
    for table_name, rel_info in table_rel.items():
        DB.execute_sql('alter table {} drop constraint {}_pkey'.format(table_name, table_name))
        rel_name, backref, pkey_columns = rel_info
        rel_obj = Relationships.get(Relationships.name == rel_name)
        migrate(
            migrator.add_column(
                table_name, 'relationship_id',
                ForeignKeyField(Relationships, field=Relationships.uuid, default=rel_obj.uuid, backref=backref)
            ),
            migrator.add_column(
                table_name, 'uuid',
                UUIDField(null=True)
            ),
            migrator.add_index(
                table_name,
                [fkey_meta.column for fkey_meta in DB.get_foreign_keys(table_name)],
                unique=True
            )
        )
        for row in DB.execute_sql('select {} from {}'.format(','.join(pkey_columns), table_name)):
            condition = []
            for key, value in zip(pkey_columns, row):
                param_val = value if isinstance(value, int) else u"'{}'".format(value)
                condition.append(u'{} = {}'.format(key, param_val))
            condition = u' and '.join(condition)
            DB.execute_sql(u'update {} set uuid = %s where {}'.format(table_name, condition), (str(uuid.uuid4()),))
        DB.execute_sql('alter table {} add constraint {}_pkey primary key (uuid)'.format(table_name, table_name))
    migrate(
        migrator.add_column(
            'citationtransaction', 'transaction_id',
            ForeignKeyField(TransactionUser, index=True, default=None, null=True, field=TransactionUser.uuid)
        ),
        migrator.add_column(
            'doitransaction', 'transaction_id',
            ForeignKeyField(TransactionUser, index=True, default=None, null=True, field=TransactionUser.uuid)
        )
    )
    for row in DB.execute_sql('select trans_old_id from citationtransaction'):
        cursor = DB.execute_sql('select uuid from transactionuser where transaction_id = {}'.format(row[0]))
        new_uuid = list(cursor)[0][0]
        DB.execute_sql(
            "update citationtransaction set transaction_id = '{}' where trans_old_id = {}".format(new_uuid, row[0]))
    for row in DB.execute_sql('select trans_old_id from doitransaction'):
        cursor = DB.execute_sql('select uuid from transactionuser where transaction_id = {}'.format(row[0]))
        new_uuid = list(cursor)[0][0]
        DB.execute_sql(
            "update doitransaction set transaction_id = '{}' where trans_old_id = {}".format(
                new_uuid, row[0]
            )
        )
    migrate(
        migrator.drop_column('citationtransaction', 'trans_old_id'),
        migrator.drop_column('doitransaction', 'trans_old_id'),
        migrator.add_not_null('citationtransaction', 'transaction_id'),
        migrator.add_not_null('doitransaction', 'transaction_id'),
    )
    for table_name, rel_info in table_rel.items():
        rel_name, backref, pkey_columns = rel_info
        new_index_name = '_'.join([table_name, pkey_columns[1], pkey_columns[0], 'relationship_id'])
        old_index_name = '_'.join([table_name, pkey_columns[0], pkey_columns[1]])
        DB.execute_sql('drop index if exists {}'.format(old_index_name))
        old_index_name = '_'.join([table_name, pkey_columns[1], pkey_columns[0]])
        DB.execute_sql('drop index if exists {}'.format(old_index_name))
        DB.execute_sql('create unique index {} on {} ({})'.format(
            new_index_name, table_name,
            ','.join([pkey_columns[1], pkey_columns[0], 'relationship_id'])
        ))
    DB.execute_sql(
        'alter table {table} add constraint {table}_pkey primary key (citation_id, transaction_id)'.format(
            table='citationtransaction'
        )
    )
    DB.execute_sql('create index transactionuser_transaction_id on transactionuser (transaction_id)')
# pylint: enable=too-many-locals


def update_schema():
    """Update schema from 2.0 to 3.0."""
    _rename_tables()
    _rename_columns()
    _create_tables()
    _add_relationship_columns()
