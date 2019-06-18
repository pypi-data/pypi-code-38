# -*- coding: utf-8 -*-
import logging
from rq import Connection, Queue
from sqlalchemy import event
from sqlalchemy.orm import object_session
from zope.interface import Interface

log = logging.getLogger()


class IIndexer(Interface):
    pass


class Indexer(object):
    """
    Handles the indexing of the DB to ES.
    This object contains a number listeners.
    First a list of the changes to be made will be kept.
    In case of a commit, these changes will also be executed.
    """

    def __init__(self, settings, index_operation, index_operation_name, cls):
        self.sessions = set()
        self.index_operation = index_operation
        self.index_operation_name = index_operation_name
        self._register_event_listeners(cls)
        self.settings = settings
        self.cls_name = cls.__name__

    def _register_event_listeners(self, cls):
        """
        :param cls: DB class
        """
        event.listen(cls, 'after_insert', self._new_listener)
        event.listen(cls, 'after_update', self._update_listener)
        event.listen(cls, 'after_delete', self._delete_listener)

    @staticmethod
    def _update_listener(mapper, connection, target):
        _add_to_session_list(target, operation='UPDATE')

    @staticmethod
    def _new_listener(mapper, connection, target):
        _add_to_session_list(target, operation='ADD')

    @staticmethod
    def _delete_listener(mapper, connection, target):
        _add_to_session_list(target, operation='REMOVE')

    def register_session(self, session, redis=None):
        session.redis = redis
        session.index_new = session.index_new if hasattr(session, 'index_new') else {}
        session.index_new[self.cls_name] = set()
        session.index_dirty = session.index_dirty if hasattr(session, 'index_dirty') else {}
        session.index_dirty[self.cls_name] = set()
        session.index_deleted = session.index_deleted if hasattr(session, 'index_deleted') else {}
        session.index_deleted[self.cls_name] = set()
        self.sessions.add(session)
        event.listen(session, 'after_commit', self.after_commit_listener)
        event.listen(session, 'after_rollback', self.after_rollback_listener)

    def after_commit_listener(self, session):
        """
        Processing the changes.
        All new or changed items are now indexed. All deleted items are now removed from the index.
        """
        log.info('Commiting indexing orders for session %s' % session)
        try:
            if not any((session.index_new[self.cls_name],
                        session.index_dirty[self.cls_name],
                        session.index_deleted[self.cls_name])):
                return
            if session.redis is not None:
                self._queue_job(session.redis,
                                self.settings['redis.queue_name'],
                                self.index_operation_name,
                                session.index_new[self.cls_name],
                                session.index_dirty[self.cls_name],
                                session.index_deleted[self.cls_name],
                                self.settings)
            else:
                log.info('Redis not found, falling back to indexing synchronously without redis')
                self.index_operation(
                    session.index_new[self.cls_name],
                    session.index_dirty[self.cls_name],
                    session.index_deleted[self.cls_name],
                    self.settings
                )
            session.index_new[self.cls_name].clear()
            session.index_dirty[self.cls_name].clear()
            session.index_deleted[self.cls_name].clear()
        except AttributeError:
            log.warning('Trying to commit indexing orders, but indexing sets are not present.')

    @staticmethod
    def _queue_job(redis, queue_name, delegate, *args):
        """
            creates a new job on the queue
            :param redis: redis
            :param delegate: method to be executed by the queue. Use fully qualified method name as String.
            :param args:  arguments of the method
            :return: job_id
            """
        log.info('Queuing job...')
        with Connection(redis):
            q = Queue(queue_name)
            job = q.enqueue(delegate, *args)
            return job.id

    def after_rollback_listener(self, session):
        """
        Rollback of the transaction, undo the indexes.
        If our transaction is terminated, we will reset the
        indexing assignments.
        """
        log.info('Removing indexing orders.')
        try:
            session.index_new[self.cls_name].clear()
            session.index_dirty[self.cls_name].clear()
            session.index_deleted[self.cls_name].clear()
        except (AttributeError, KeyError):
            log.warning('Trying to remove indexing orders, but indexing sets are not present.')

    def remove_session(self, session):
        """
        :param sqlalchemy.session.Session session: Database session to remove
        """
        try:
            del session.redis
        except AttributeError:
            pass
        try:
            del session.index_new[self.cls_name]
            del session.index_dirty[self.cls_name]
            del session.index_deleted[self.cls_name]
        except (AttributeError, KeyError):
            log.warning('Removing a session that has no indexing sets.')
        self.sessions.remove(session)


def _add_to_session_list(target, operation):
    session = object_session(target)
    try:
        if operation == 'ADD':
            session.index_new[target.__class__.__name__].add(target.id)
        elif operation == 'UPDATE':
            session.index_dirty[target.__class__.__name__].add(target.id)
        elif operation == 'REMOVE':
            session.index_deleted[target.__class__.__name__].add(target.id)
        log.info(operation + ': ' + str(target) + ' {0} from index'.format(target.id))
    except (AttributeError, KeyError):
        log.warning(
            'Trying to register a ' + str(target) +
            ' for indexing ' + operation + ', but indexing sets are not present.')