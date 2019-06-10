#
# Copyright (c) 2019 UCT Prague.
# 
# cli.py is part of Invenio Explicit ACLs 
# (see https://github.com/oarepo/invenio-explicit-acls).
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Command-line client extension."""

import json
import sys

import click
from flask import cli, current_app
from invenio_db import db
from invenio_indexer import current_record_to_index
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import current_jsonschemas
from invenio_records import Record
from invenio_records.models import RecordMetadata
from sqlalchemy import cast

from invenio_explicit_acls.models import ACL
from invenio_explicit_acls.proxies import current_explicit_acls


@click.group(name='explicit-acls')
def explicit_acls():
    """Invenio ACLs commands."""


@explicit_acls.command()
@click.argument('schema')
@cli.with_appcontext
def prepare(schema):  # pragma no cover
    """
        Setup schema to be used with invenio explicit acls.

    :param schema:       the name of the schema that should be prepared for explicit ACLs
    """
    prepare_impl(schema)


def prepare_impl(schema):
    """
        Setup schema to be used with invenio explicit acls.

    :param schema:       the name of the schema that should be prepared for explicit ACLs
    """
    current_explicit_acls.prepare(schema)


@explicit_acls.command(name='list')
@cli.with_appcontext
def list_schemas():  # pragma no cover
    """List all schemas registered in invenio."""
    list_schemas_impl()


def list_schemas_impl():
    """List all schemas registered in invenio."""
    for schema in current_jsonschemas.list_schemas():
        print("   ", schema)


@explicit_acls.command(name='full-reindex')
@click.option('--verbose/--no-verbose', default=False)
@click.option('--records/--no-records', default=True)
@cli.with_appcontext
def full_reindex(verbose, records):  # pragma no cover
    """Updates index of all ACLs and optionally reindexes all documents."""
    full_reindex_impl(verbose, records)


def _get_record_ids(schema):
    """Returns iterable of ids of records with the given $schema."""
    full_schema = current_jsonschemas.path_to_url(schema)

    if db.engine.dialect.name == 'postgresql':
        import sqlalchemy.dialects.postgresql
        for x in db.session.query(RecordMetadata.id).filter(
            RecordMetadata.json['$schema'] == cast(schema, sqlalchemy.dialects.postgresql.JSONB)
        ):
            yield str(x[0])

        for x in db.session.query(RecordMetadata.id).filter(
            RecordMetadata.json['$schema'] == cast(full_schema, sqlalchemy.dialects.postgresql.JSONB)
        ):
            yield str(x[0])

    else:
        # no postgres, do the iteration
        for rec in RecordMetadata.query.all():
            if rec.json.get('$schema') in (schema, full_schema):
                yield str(rec.id)


def full_reindex_impl(verbose, records, in_bulk=True):
    """Updates index of all ACLs and optionally reindexes all documents."""
    # 1. for each ACL update the ACL's index etc
    if verbose:
        print('Reindexing ACLs')
    for acl in ACL.query.all():
        if verbose:
            print('Updating ACL representation for', acl)
        acl.update()
    if not records:
        return
    # 2. for each of ACL enabled indices reindex all documents
    uuids = set()
    for schema in current_explicit_acls.enabled_schemas:
        if verbose:
            print('Getting records for schema', schema)
        # filter all records with the given schema
        recs = set(_get_record_ids(schema))
        if verbose:
            print('   ... collected %s records' % len(recs))
        uuids.update(recs)

    if verbose:
        print('Adding %s records to indexing queue' % len(uuids))

    if in_bulk:
        RecordIndexer().bulk_index(uuids)

        if verbose:
            print('Running bulk indexer on %s records' % len(uuids))
        RecordIndexer(version_type=None).process_bulk_queue(
            es_bulk_kwargs={'raise_on_error': False})
    else:
        indexer = RecordIndexer()
        for rec_uuid in uuids:
            r = Record.get_record(rec_uuid)
            indexer.index(r)


@explicit_acls.command()
@click.argument('record')
@click.option('--debug/--no-debug', default=False)
@cli.with_appcontext
def explain(record, debug):  # pragma no cover
    """
    Explains which ACLs will be applied to a record and what the added ACL property will look like.

    :param record a path to a file containing record metadata or '-' to read the metadata from stdin.
    """
    explain_impl(record, debug)


def explain_impl(record, debug):
    """
    Explains which ACLs will be applied to a record and what the added ACL property will look like.

    :param record a path to a file containing record metadata or '-' to read the metadata from stdin.
    """
    class Model:
        def __init__(self):
            self.id = 'record-id'

    with open(record, 'r') if record is not "-" else sys.stdin as f:
        record_metadata = json.load(f)
        if '$schema' not in record_metadata:
            print('Please add $schema to record metadata')
            return
        invenio_record = Record(record_metadata)
        invenio_record.model = Model()

        schema = record_metadata['$schema']
        if schema.startswith('http://') or schema.startswith('https://'):
            schema = current_jsonschemas.url_to_path(schema)

        print('Possible ACLs')
        for acl in ACL.query.all():
            if schema in acl.schemas:
                print('    ', type(acl).__name__, acl)

                for k in dir(acl):
                    if k.startswith('_'): continue
                    if k in ('metadata', 'query'): continue
                    val = getattr(acl, k)
                    if not callable(val) and val:
                        if isinstance(val, list):
                            print('        %s = %s' % (k, [str(x) for x in val]))
                        else:
                            print('        %s = %s' % (k, val))
        print()

        applicable_acls = []
        for acl in current_explicit_acls.acl_models:
            print('Checking ACLs of type', acl)
            if debug and hasattr(acl, '_get_percolate_query'):
                index, _doc_type = current_record_to_index(invenio_record)
                index = acl.get_acl_index_name(index)
                doc_type = current_app.config['INVENIO_EXPLICIT_ACLS_DOCTYPE_NAME']
                print('   Will run percolate query on index %s and doc_type %s:' % (index, doc_type))
                print(
                    '\n'.join(
                        '        ' + x for x in
                        json.dumps(acl._get_percolate_query(invenio_record), indent=4).split('\n')
                    )
                )
            found_acls = list(acl.get_record_acls(invenio_record))
            for acl in found_acls:
                print('    found match: %s with priority of %s' % (acl, acl.priority))
                for actor in acl.actors:
                    print('        ', actor)
            applicable_acls.extend(found_acls)
        print()

        if not applicable_acls:
            print('The record is not matched by any ACLs')
            return

        matching_acls = list(current_explicit_acls.get_record_acls(invenio_record))

        print('Of these, the following ACLs will be used (have the highest priority):')
        for acl in matching_acls:
            print('    ', acl)
            for actor in acl.actors:
                print('        ', actor)

        print()

        print('The ACLs will get serialized to the following element')
        print(json.dumps({
            '_invenio_explicit_acls': current_explicit_acls.serialize_record_acls(matching_acls)
        }, indent=4))
