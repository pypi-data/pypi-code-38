#
# Copyright (c) 2019 UCT Prague.
# 
# tasks.py is part of Invenio Explicit ACLs 
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
"""Celery tasks for ACL aware ES reindex."""
import datetime
import logging

import elasticsearch
from celery import shared_task
from invenio_indexer.api import RecordIndexer
from invenio_records import Record
from invenio_search import current_search_client
from sqlalchemy.orm.exc import NoResultFound

from invenio_explicit_acls.models import ACL
from invenio_explicit_acls.proxies import current_explicit_acls
from invenio_explicit_acls.utils import schema_to_index

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def acl_changed_reindex(acl_id):
    """
    ACL has been changed so reindex all the documents in the given index.

    :param acl_id:   id of ACL instance
    """
    logger.info('Reindexing started for ACL=%s', acl_id)

    timestamp = datetime.datetime.now().astimezone().isoformat()

    acl = ACL.query.filter_by(id=acl_id).one_or_none()

    if not acl:
        # deleted in the meanwhile, so just return
        return          # pragma no cover

    # make sure all indices are flushed so that no resource is obsolete in index
    for schema in acl.schemas:
        current_search_client.indices.flush(index=schema_to_index(schema)[0])

    indexer = RecordIndexer()
    updated_count = 0
    removed_count = 0

    for id in acl.get_matching_resources():
        try:
            rec = Record.get_record(id)
        except:     # pragma no cover
            # record removed in the meanwhile by another thread/process,
            # indexer should have been called to remove it from ES
            # won't test this so pragma no cover
            continue
        try:
            indexer.index(rec)
            updated_count += 1
        except Exception as e:  # pragma no cover
            logger.exception('Error indexing ACL for resource %s: %s', id, e)

    # reindex the resources those were indexed by this acl but no longer should be
    for id in acl.used_in_records(older_than_timestamp=timestamp):
        try:
            rec = Record.get_record(id)
        except NoResultFound:                           # pragma no cover
            continue
        except:                                         # pragma no cover
            logger.exception('Unexpected exception in record reindexing')
            continue

        try:
            removed_count += 1
            indexer.index(rec)
        except:     # pragma no cover
            logger.exception('Error indexing ACL for obsolete resource %s', id)

    logger.info('Reindexing finished for ACL=%s, acl applied to %s records, acl removed from %s records',
                acl_id, updated_count, removed_count)


@shared_task(ignore_result=True)
def acl_deleted_reindex(schemas, acl_id):
    """
    ACL has been deleted so reindex all the documents that contain reference to it.

    :param index: the index of documents
    :param record_acl_id:   if of the ACL instance that has been deleted
    """
    logger.info('Reindexing started for deleted ACL=%s', acl_id)

    acl = ACL.query.filter_by(id=acl_id).one_or_none()

    if acl:     # pragma no cover
        raise AttributeError('ACL with id %s is still in the database, '
                             'please remove it before calling current_explicit_acls.reindex_acl_removed' % acl_id)

    indexer = RecordIndexer()

    query = {
        "nested": {
            "path": "_invenio_explicit_acls",
            "query": {
                "term": {
                    "_invenio_explicit_acls.id": acl_id
                }
            }
        }
    }
    removed_count = 0
    for schema in schemas:
        current_search_client.indices.flush(index=schema_to_index(schema)[0])
        try:
            index, doc_type = schema_to_index(schema)

            for doc in elasticsearch.helpers.scan(
                current_search_client,
                query={
                    "query": query,
                    "_source": False,
                },
                index=index,
                doc_type=doc_type
            ):
                try:
                    indexer.index(Record.get_record(doc['_id']))
                    removed_count += 1
                except NoResultFound:                           # pragma no cover
                    continue
                except:                                         # pragma no cover
                    logger.exception('Unexpected exception in record reindexing')
                    continue
        except:     # pragma no cover
            logger.exception('Error removing ACL from schema %s', schema)

    logger.info('Reindexing finished for deleted ACL=%s, acl removed from %s records', acl_id, removed_count)
