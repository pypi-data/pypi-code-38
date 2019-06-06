#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Schema update version 0.1 to 1.0."""
from peewee import Model, CharField, TextField, ForeignKeyField, DateTimeField
from playhouse.migrate import SchemaMigrator, migrate
from ..globals import DB
from ..all_objects import Users, Instruments, Transactions, AnalyticalTools


class OldProposals(Model):
    """This is the old proposals."""

    id = CharField(primary_key=True)

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """This is the meta class for OldTrans."""

        database = DB
        table_name = 'proposals'
        legacy_table_names = False
    # pylint: enable=too-few-public-methods


class OldTrans(Model):
    """This is the old transactions."""

    submitter = ForeignKeyField(Users, backref='transactions')
    instrument = ForeignKeyField(Instruments, backref='transactions')
    proposal = ForeignKeyField(OldProposals, backref='transactions')
    created = DateTimeField()
    updated = DateTimeField()
    deleted = DateTimeField(null=True)

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """This is the meta class for OldTrans."""

        database = DB
        table_name = 'transactions'
        legacy_table_names = False
    # pylint: enable=too-few-public-methods


class OldTransSIP(Model):
    """This is the old transsip."""

    id = ForeignKeyField(
        Transactions, index=True, primary_key=True,
        unique=True, backref='transsip'
    )
    submitter = ForeignKeyField(Users, backref='transsip')
    instrument = ForeignKeyField(Instruments, backref='transsip')
    proposal = ForeignKeyField(OldProposals, backref='transsip')
    created = DateTimeField()
    updated = DateTimeField()
    deleted = DateTimeField(null=True)

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """This is the meta class for OldTrans."""

        database = DB
        table_name = 'transsip'
        legacy_table_names = False
    # pylint: enable=too-few-public-methods


class OldTransSAP(Model):
    """This is the old transsap."""

    id = ForeignKeyField(
        Transactions, index=True, primary_key=True,
        unique=True, backref='transsap'
    )
    submitter = ForeignKeyField(Users, backref='transsap')
    analytical_tool = ForeignKeyField(AnalyticalTools, backref='transsap')
    proposal = ForeignKeyField(OldProposals, backref='transsap')
    created = DateTimeField()
    updated = DateTimeField()
    deleted = DateTimeField(null=True)

    # pylint: disable=too-few-public-methods
    class Meta(object):
        """This is the meta class for OldTrans."""

        database = DB
        table_name = 'transsap'
        legacy_table_names = False
    # pylint: enable=too-few-public-methods


def update_schema():
    """Update from 0.1 to 1.0."""
    migrator = SchemaMigrator(DB)

    OldTransSIP.create_table()
    OldTransSAP.create_table()

    migrate(
        migrator.add_column(
            'transactions',
            'description',
            TextField(null=True)
        )
    )
    for old_trans in OldTrans.select():
        transsip = OldTransSIP()
        for attr in ['submitter', 'instrument', 'proposal', 'created', 'updated', 'deleted']:
            setattr(transsip, attr, getattr(old_trans, attr))
        setattr(transsip, 'id', Transactions.get(
            Transactions.id == old_trans.id))
        transsip.save(force_insert=True)
    migrate(
        migrator.drop_column(
            'transactions',
            'submitter_id'
        ),
        migrator.drop_column(
            'transactions',
            'instrument_id'
        ),
        migrator.drop_column(
            'transactions',
            'proposal_id'
        )
    )
