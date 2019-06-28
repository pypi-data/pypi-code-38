# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Minimal Flask application example.

First install Invenio-PIDRelations, setup the application and load
fixture data by running:

.. code-block:: console

   $ pip install -e .[all]
   $ cd examples
   $ ./app-setup.sh
   $ ./app-fixtures.sh

Next, start the development server:

.. code-block:: console

   $ export FLASK_APP=app.py FLASK_DEBUG=1
   $ flask run

and open the example application in your browser:

.. code-block:: console

    $ open http://127.0.0.1:5000/

To reset the example application run:

.. code-block:: console

    $ ./app-teardown.sh
"""

from __future__ import absolute_import, print_function

from flask import Flask, redirect, render_template, request, url_for
from invenio_db import InvenioDB, db
from invenio_indexer import InvenioIndexer
from invenio_indexer.signals import before_record_index
from invenio_pidstore import InvenioPIDStore
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.recordid import RecordIdProvider
from invenio_pidstore.resolver import Resolver
from invenio_records import InvenioRecords
from invenio_records.api import Record
from invenio_records_ui import InvenioRecordsUI
from marshmallow import Schema, fields

from invenio_pidrelations import InvenioPIDRelations
from invenio_pidrelations.contrib.versioning import PIDNodeVersioning, \
    versioning_blueprint
from invenio_pidrelations.indexers import index_relations
from invenio_pidrelations.models import PIDRelation
from invenio_pidrelations.utils import resolve_relation_type_config

# Create Flask application
app = Flask(__name__, template_folder='.')
app.config.update(dict(
    TEMPLATES_AUTO_RELOAD=True,
    CELERY_ALWAYS_EAGER=True,
    CELERY_RESULT_BACKEND='cache',
    CELERY_CACHE_BACKEND='memory'))

InvenioDB(app)
InvenioPIDStore(app)
InvenioPIDRelations(app)
app.register_blueprint(versioning_blueprint)
InvenioIndexer(app)
InvenioRecords(app)
InvenioRecordsUI(app)
before_record_index.connect(index_relations, sender=app)

record_resolver = Resolver(
    pid_type='recid', object_type='rec', getter=Record.get_record
)


class SimpleRecordSchema(Schema):
    """Tiny schema for our simple record."""

    recid = fields.Str()
    title = fields.Str()
    body = fields.Str()


@app.route('/')
def index():
    relation_id = resolve_relation_type_config('version').id
    heads = (
        PersistentIdentifier.query
        .join(
            PIDRelation,
            PIDRelation.parent_id == PersistentIdentifier.id)
        .filter(
            PIDRelation.relation_type == relation_id)
        .distinct())
    return render_template('index.html', heads=heads)


@app.route('/create', methods=['POST'])
def create():
    create_simple_record(request.form)
    return redirect(url_for('index'))


@app.template_filter()
def to_record(pid):
    schema = SimpleRecordSchema()
    schema.context = dict(pid=pid)
    rec = schema.dump(record_resolver.resolve(pid.pid_value)[1])
    return rec.data


def create_simple_record(data):
    # Create the record and mint a PID
    metadata, errors = SimpleRecordSchema().load(data)
    parent = data.get('parent')
    if parent != 'new':
        metadata['conceptrecid'] = parent

    rec = Record.create(metadata)

    record_minter(rec.id, rec)
    db.session.commit()


def record_minter(record_uuid, data):
    parent = data.get('conceptrecid')
    if not parent:
        parent_pid = RecordIdProvider.create(object_type='rec',
                                             object_uuid=None,
                                             status=PIDStatus.REGISTERED).pid
        data['conceptrecid'] = parent_pid.pid_value
    else:
        parent_pid = PersistentIdentifier.get(
            pid_type=RecordIdProvider.pid_type, pid_value=parent)
    provider = RecordIdProvider.create('rec', record_uuid)
    data['recid'] = provider.pid.pid_value

    versioning = PIDNodeVersioning(pid=parent_pid)
    versioning.insert_child(child_pid=provider.pid)
    return provider.pid
