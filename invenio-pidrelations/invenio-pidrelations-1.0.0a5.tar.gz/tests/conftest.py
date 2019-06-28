# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import shutil
import sys
import tempfile

import pytest
from elasticsearch.exceptions import RequestError
from flask import Flask
from flask_babelex import Babel
from invenio_db import InvenioDB
from invenio_db import db as db_
from invenio_indexer import InvenioIndexer
from invenio_indexer.api import RecordIndexer
from invenio_pidstore import InvenioPIDStore
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records import InvenioRecords, Record
from invenio_search import InvenioSearch, current_search, current_search_client
from marshmallow import fields
from sqlalchemy_utils.functions import create_database, database_exists, \
    drop_database

from invenio_pidrelations import InvenioPIDRelations
from invenio_pidrelations.config import RelationType
from invenio_pidrelations.models import PIDRelation
from invenio_pidrelations.serializers.schemas import RelationSchema
from invenio_pidrelations.utils import resolve_relation_type_config

# add tests to the sys path
sys.path.append(os.path.dirname(__file__))


@pytest.yield_fixture()
def instance_path():
    """Temporary instance path."""
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)


@pytest.fixture()
def base_app(instance_path):
    """Flask application fixture."""
    app_ = Flask('testapp', instance_path=instance_path)
    app_.config.update(
        SECRET_KEY='SECRET_KEY',
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        TESTING=True,
    )
    InvenioPIDStore(app_)
    InvenioDB(app_)
    InvenioPIDRelations(app_)
    InvenioRecords(app_)
    InvenioIndexer(app_)
    InvenioSearch(app_)
    Babel(app_)
    return app_


@pytest.yield_fixture()
def app(base_app):
    """Flask application fixture."""
    with base_app.app_context():
        yield base_app


@pytest.yield_fixture()
def es(app):
    """Provide elasticsearch access."""
    try:
        list(current_search.create())
    except RequestError:
        list(current_search.delete(ignore=[400, 404]))
        list(current_search.create())
    current_search_client.indices.refresh()
    yield current_search_client
    list(current_search.delete(ignore=[404]))


@pytest.yield_fixture()
def db(app):
    """Database fixture."""
    if database_exists(str(db_.engine.url)):
        db_.session.remove()
        drop_database(str(db_.engine.url))
    create_database(str(db_.engine.url))
    db_.create_all()
    yield db_
    db_.session.remove()
    drop_database(db_.engine.url)
    # Dispose the engine in order to close all connections. This is
    # needed for sqlite in memory databases.
    db_.engine.dispose()


@pytest.fixture()
def version_relation(app, db):
    """Versioning relation."""
    return resolve_relation_type_config('version')


@pytest.fixture()
def draft_relation(app, db):
    """Versioning relation."""
    return resolve_relation_type_config('record_draft')


@pytest.fixture()
def recids(app, db):
    """Create recids fixture."""
    return {
        str(status): PersistentIdentifier.create(
            'recid', 'pid_status_{}'.format(status), object_type='rec',
            status=status
        ) for status in [PIDStatus.REGISTERED, PIDStatus.DELETED,
                         PIDStatus.RESERVED, PIDStatus.REDIRECTED]
    }


@pytest.fixture()
def version_pids(app, db, version_relation, draft_relation):
    """Create versionned PIDs."""
    h1 = PersistentIdentifier.create('recid', 'foobar', object_type='rec',
                                     status=PIDStatus.REGISTERED)
    h1v1 = PersistentIdentifier.create('recid', 'foobar.v1', object_type='rec',
                                       status=PIDStatus.REGISTERED)
    h1v2 = PersistentIdentifier.create('recid', 'foobar.v2', object_type='rec',
                                       status=PIDStatus.REGISTERED)
    h1v3 = PersistentIdentifier.create('recid', 'foobar.v3', object_type='rec',
                                       status=PIDStatus.REGISTERED)
    h1del1 = PersistentIdentifier.create('recid', 'foobar.del1',
                                         object_type='rec',
                                         status=PIDStatus.DELETED)
    h1del2 = PersistentIdentifier.create('recid', 'foobar.del2',
                                         object_type='rec',
                                         status=PIDStatus.DELETED)
    h1draft1 = PersistentIdentifier.create('recid', 'foobar.draft',
                                           object_type='rec',
                                           status=PIDStatus.RESERVED)
    h1deposit1 = PersistentIdentifier.create('recid', 'foobar.deposit',
                                             object_type='rec')
    VERSION = version_relation.id
    DRAFT = draft_relation.id
    PIDRelation.create(h1, h1v1, VERSION, 0)
    PIDRelation.create(h1, h1v2, VERSION, 1)
    PIDRelation.create(h1, h1v3, VERSION, 2)
    PIDRelation.create(h1, h1del1, VERSION, 3)
    PIDRelation.create(h1, h1del2, VERSION, 4)
    PIDRelation.create(h1, h1draft1, VERSION, 5)
    PIDRelation.create(h1draft1, h1deposit1, DRAFT, 0)

    h1.redirect(h1v3)

    h2 = PersistentIdentifier.create('recid', 'spam', object_type='rec',
                                     status=PIDStatus.REGISTERED)
    h2v1 = PersistentIdentifier.create('recid', 'spam.v1')
    PIDRelation.create(h2, h2v1, VERSION, 0)
    h2.redirect(h2v1)
    return [
        {
            'parent': h1,
            'children': [
                h1v1,
                h1v2,
                h1v3,
                h1del1,
                h1del2,
                h1draft1,
            ],
            'deposit': h1deposit1,
        },
        {
            'parent': h2,
            'children': [
                h2v1,
            ],
        },
    ]


@pytest.fixture()
def nested_pids_and_relations(app, db):
    """Fixture for a nested PIDs and the expected serialized relations."""
    # Create some PIDs and connect them into different nested PID relations
    pids = {}
    for idx in range(1, 12):
        pid_value = str(idx)
        p = PersistentIdentifier.create('recid', pid_value, object_type='rec',
                                        status=PIDStatus.REGISTERED)
        pids[idx] = p

    VERSION = resolve_relation_type_config('version').id

    #    1  (Version)
    #  / | \
    # 2  3 4
    PIDRelation.create(pids[1], pids[2], VERSION, 0)
    PIDRelation.create(pids[1], pids[3], VERSION, 1)
    PIDRelation.create(pids[1], pids[4], VERSION, 2)

    # Define the expected PID relation tree for of the PIDs
    expected_relations = {}
    expected_relations[4] = {
        u'relations': {
            'version': [
                {u'children': [{u'pid_type': u'recid',
                                u'pid_value': u'2'},
                               {u'pid_type': u'recid',
                                u'pid_value': u'3'},
                               {u'pid_type': u'recid',
                                u'pid_value': u'4'}],
                 u'index': 2,
                 u'is_child': True,
                 u'previous': {'pid_type': 'recid', 'pid_value': '3'},
                 u'next': None,
                 u'is_last': True,
                 u'is_parent': False,
                 u'parent': {u'pid_type': u'recid',
                             u'pid_value': u'1'},
                 u'type': 'version'
                 }
            ],
        }
    }
    return pids, expected_relations


class CustomRelationSchema(RelationSchema):
    """PID relation Schema containing only children and one extra field."""

    class Meta:
        """Meta fields of the schema."""

        fields = ("children", "has_three_children", )

    has_three_children = fields.Method('dump_has_three_children')

    def dump_has_three_children(self, obj):
        """Dump information if relation has exactly three children."""
        return obj.children.count() == 3


@pytest.yield_fixture()
def custom_relation_schema(app):
    """Fixture for PID relations config with custom schemas."""
    orig = app.config['PIDRELATIONS_RELATION_TYPES']
    app.config['PIDRELATIONS_RELATION_TYPES'] = [
        RelationType(0, 'version', 'Version',
                     'invenio_pidrelations.contrib.'
                     'versioning:PIDNodeVersioning',
                     CustomRelationSchema),
    ]
    yield app
    app.config['PIDRELATIONS_RELATION_TYPES'] = orig


@pytest.fixture()
def records(pids, db):
    """Fixture for the records."""
    pid_versions = ['h1v1', 'h1v2', 'h2v1']
    schema = {
        'type': 'object',
        'properties': {
            'title': {'type': 'string'},
        },
    }
    data = {
        name: {'title': 'Test version {}'.format(name),
               'recid': pids[name].pid_value,
               '$schema': schema}
        for name in pid_versions
    }
    records = dict()
    for name in pid_versions:
        record = Record.create(data[name])
        pids[name].assign('rec', record.id)
        records[name] = record
    return records


@pytest.fixture()
def indexed_records(es, records):
    """Fixture for the records, which are already indexed."""
    # es.indices.flush('*')
    # # delete all elasticsearch indices and recreate them
    # for deleted in current_search.delete(ignore=[404]):
    #     pass
    # for created in current_search.create(None):
    #     pass
    # flush the indices so that indexed records are searchable
    for pid_name, record in records.items():
        RecordIndexer().index(record)
    es.indices.flush('*')
    return records
