# -*- coding: utf-8 -*-
from oe_utils.data.data_transfer_objects import ResultDTO
import os
from sqlalchemy.sql import desc
from oe_utils.data.models import Wijziging


class DataManager(object):
    """
    A datamanager base class.
    """

    @staticmethod
    def process_ranged_query(query, result_range):
        """

        :param query: the query to be processed
        :param result_range: :class: 'oe_utils.range_parser.Range'
        :return: :class:`oe_utils.data.data_transfer_objects.ResultDTO`
        """
        total = query.count()
        if result_range is not None:
            data = query \
                .offset(result_range.start) \
                .limit(result_range.get_page_size()) \
                .all()
        else:
            data = query.all()
        return ResultDTO(data, total)

    @staticmethod
    def ordered_result_list(query, model_type, sortlist):
        for sorttuple in sortlist:
            if hasattr(model_type, sorttuple[0]):
                attr = getattr(model_type, sorttuple[0])
                query = query.order_by(attr.asc()) if sorttuple[1] == 'asc' else query.order_by(attr.desc())
        return query

    def __init__(self, session, cls):
        """

        :param session: a db session
        :param cls: the class of the objects to manage
        :return:
        """
        if not session.autoflush:
            raise ValueError("Session autoflush must be True.")
        self.session = session
        self.cls = cls

    def get_one(self, object_id):
        """
        Retrieve an object by its object_id

        :param object_id: the objects id.
        :return: the requested object
        :raises: :class: NoResultFound when the object could not be found
        """
        return self.session.query(self.cls).filter_by(id=object_id).one()

    def get_one_for_update(self, object_id):
        """
        Retrieve an object by its object_id
        Does a select for update on the row, results in row level lock for the duration of the transaction

        :param object_id: the objects id.
        :return: the requested object
        :raises: :class: NoResultFound when the object could not be found
        """
        return self.session.query(self.cls).with_for_update().filter_by(id=object_id).one()

    def get(self, object_id, cls=None):
        """
        Retrieve an object by its object_id

        :param: object_id: the objects id.
        :param: cls: the objects class, if None use the default class from the datamanager
        :return: the requested object or None if not found
        """
        cls = self.cls if cls is None else cls
        return self.session.query(cls).get(object_id)

    def get_for_update(self, object_id, cls=None):
        """
        Retrieve an object by its object_id
        Does a select for update on the row, results in row level lock for the duration of the transaction

        :param: object_id: the objects id.
        :param: cls: the objects class, if None use the default class from the datamanager
        :return: the requested object or None if not found
        """
        cls = self.cls if cls is None else cls
        return self.session.query(cls).with_for_update().get(object_id)

    def delete(self, object_id):
        """
        Delete an object by its id

        :param object_id: the objects id.
        :return: the deleted object
        :raises: :class: NoResultFound when the object could not be found
        """
        obj = self.session.query(self.cls).filter_by(id=object_id).one()
        self.session.delete(obj)
        return obj

    def save(self, obj):
        """
        save an object

        :param obj: the object
        :return: the saved object
        """
        if obj not in self.session:
            self.session.add(obj)
        else:
            obj = self.session.merge(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj


class FeedArchiveNotFound(Exception):
    pass


class AtomFeedManager(object):
    """
    A data manager for feeds.
    """
    def __init__(self, session, feed_repository, feed_model, feedentry_model):
        """
        :param session: a db session
        :param feed_repository: a repository to store the archived feeds
        """
        self.session = session
        self.feed_repository = feed_repository
        self.feed_model = feed_model
        self.feedentry_model = feedentry_model
        self._current_feed = None

    @property
    def current_feed(self):
        if self._current_feed is None:
            self._current_feed = self.session.query(self.feed_model).order_by(desc(self.feed_model.id)).first()
        return self._current_feed

    def get_sibling(self, feed_id, sibling_type):
        """
        get a previous/next sibling from a feed
        :param feed_id: id of the feed
        :param sibling_type: sibling type ('previous', 'next')
        :return: the sibling
        """
        if sibling_type == 'previous':
            query = self.session.query(self.feed_model).filter(self.feed_model.id < feed_id)
            order_clause = desc(self.feed_model.id)
        elif sibling_type == 'next':
            query = self.session.query(self.feed_model).filter(self.feed_model.id > feed_id)
            order_clause = self.feed_model.id
        else:
            raise Exception('Unhandled sibling relation type')  # pragma no cover
        if query.count() > 0:
            return query.order_by(order_clause).first()
        else:
            return None

    def save_new_feed(self):
        """
        Save a new feed object to the db
        :return: the saved object
        """
        obj = self.feed_model()
        return self.save_object(obj)

    def save_object(self, obj):
        """
        Save an object to the db
        :param obj: the object to save
        :return: the saved object
        """
        self.session.add(obj)
        self.session.flush()
        return obj

    def get_from_archive(self, feed_id):
        """
        Retrieves feed that was persisted as .xml file by its id (= filename)
        Note: No check on feed validity. file content is assumed correct
        :param feed_id:
        :return: the atom feed as string
        """
        file_path = self.feed_repository + '/' + str(feed_id) + '.xml'
        if not os.path.isfile(file_path):
            raise FeedArchiveNotFound()
        with open(file_path, 'r') as rec_file:
            return rec_file.read()

    def get_atom_feed_entry(self, feedentry_id):
        """
        Get a specific feed entry
        :param id: id of the feed entry to retrieve
        :return: the feed entry
        """
        return self.session.query(self.feedentry_model).filter(
            self.feedentry_model.id == feedentry_id
        ).one()

    def archive_feed(self, feed_id, feed):
        """
        Archive a feed
        :param feed_id: the feed id of the feed to archive
        :param feed: the feed to archive
        """
        with open(self.feed_repository + '/' + str(feed_id) + '.xml', 'w') as rec_file:
            rec_file.write(feed.atom_str(pretty=True))
        if feed_id == self.current_feed.id:
            self._current_feed = None


class AuditManager(DataManager):
    """
    A data manager for audit revisions.
    """

    def __init__(self, session):
        """
        :param session: a db session
        """
        super(AuditManager, self).__init__(session, Wijziging)
        self.session = session

    @staticmethod
    def create_revision():
        """
        Create a new revision object

        :return: new revision object
        """
        return Wijziging()
