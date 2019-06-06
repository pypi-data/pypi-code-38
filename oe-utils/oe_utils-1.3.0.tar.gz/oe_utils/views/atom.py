# -*- coding: utf-8 -*-
from feedgen.feed import FeedGenerator
import abc


class AbstractAtomFeedView:

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_current_atom_feed(self):
        """
        Retrieve the current atom feed
        :return: JSON representation of the feed
        """

    @abc.abstractmethod
    def get_atom_feed(self):
        """
        Retrieve a particular feed identified by its id, identical to the source
        :return: JSON representation of the feed
        """

    @abc.abstractmethod
    def get_atom_feed_entry(self):
        """
        Retrieve a particular feed entry identified by its id, identical to the source
        :return: JSON representation of the feed entry
        """

    @abc.abstractmethod
    def archive_current_feed(self):
        """
        archive the current feed
        """


class AtomFeedView(AbstractAtomFeedView):
    """
    This is an implementation of the :class:`AbstractAtomFeedView` that adds a
    generic methods in a pylons pyramid application
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, request, atom_feed_manager, get_atom_feed_url, generate_atom_feed=None):
        """
        Functions that can be used in a pylons pyramid application

        :param request:
        :param atom_feed_manager: object of class oe_daemonutils.data.data_manager.AtomFeedManager
        :param get_atom_feed_url: the route name of the pyramid application to retrieve the atom feed
        """
        self.request = request
        self.atom_feed_manager = atom_feed_manager
        self.get_atom_feed_url = get_atom_feed_url
        self.generate_atom_feed = generate_atom_feed if generate_atom_feed else self._generate_atom_feed

    def get_current_atom_feed(self):
        return self.request.route_url(self.get_atom_feed_url, id=self.atom_feed_manager.current_feed.id)

    def get_atom_feed(self):
        feed_id = int(self.request.matchdict['id'])
        current_feed = self.atom_feed_manager.current_feed
        if feed_id == current_feed.id:
            feed = current_feed
            atom_feed = self.generate_atom_feed(feed).atom_str(pretty=True)
        else:
            atom_feed = self.atom_feed_manager.get_from_archive(feed_id)
        return atom_feed

    def get_atom_feed_entry(self):
        return self.atom_feed_manager.get_atom_feed_entry(int(self.request.matchdict['id']))

    def _archive_entire_feed(self, feed):
        current_atom_feed = self.generate_atom_feed(feed)
        new_feed = self.atom_feed_manager.save_new_feed()
        new_feed.uri = self.request.route_url(self.get_atom_feed_url, id=new_feed.id)
        current_atom_feed.link(
            href=new_feed.uri,
            rel='next-archive'
        )
        self.atom_feed_manager.archive_feed(feed.id, current_atom_feed)

    def _split_feed_and_archive(self, feed, split):
        leftover = feed.entries[split:]
        feed.entries = feed.entries[:split]
        current_atom_feed = self.generate_atom_feed(feed)
        new_feed = self.atom_feed_manager.feed_model()
        for leftover_entry in leftover:
            from sqlalchemy.orm import make_transient
            make_transient(leftover_entry)
            leftover_entry.feed = None
            leftover_entry.feed_id = None
        new_feed.entries = leftover
        new_feed = self.atom_feed_manager.save_object(new_feed)
        new_feed.uri = self.request.route_url(self.get_atom_feed_url, id=new_feed.id)
        current_atom_feed.link(
            href=new_feed.uri,
            rel='next-archive'
        )
        self.atom_feed_manager.archive_feed(feed.id, current_atom_feed)
        if len(new_feed.entries) > split:
            self._split_feed_and_archive(new_feed, split)

    def archive_current_feed(self):
        settings = self.request.registry.settings
        split = settings.get('feed.archive.split', None)
        current_feed = self.atom_feed_manager.current_feed
        if len(current_feed.entries) > 0:
            if split:
                split = int(split)
                self._split_feed_and_archive(current_feed, split)
            else:
                self._archive_entire_feed(current_feed)

    def link_to_sibling(self, feed, sibling_type, atom_feed):
        """
        Adding previous or next links to the given feed
        self._link_to_sibling(feed, 'previous', atom_feed)
        self._link_to_sibling(feed, 'next', atom_feed)

        :param feed: a feed object
        :param sibling_type: 'previous' or 'next'
        :param atom_feed: an atom feed like `feedgen.feed.FeedGenerator`
        """
        sibling = self.atom_feed_manager.get_sibling(feed.id, sibling_type)
        if sibling:
            rel = "prev-archive" if sibling_type == "previous" else "next-archive"
            atom_feed.link(href=self.request.route_url(self.get_atom_feed_url, id=sibling.id),
                           rel=rel)

    def init_atom_feed(self, feed):
        """
        Initializing an atom feed `feedgen.feed.FeedGenerator` given a feed object

        :param feed: a feed object
        :return: an atom feed `feedgen.feed.FeedGenerator`
        """
        atom_feed = FeedGenerator()
        atom_feed.id(id=self.request.route_url(self.get_atom_feed_url, id=feed.id))
        atom_feed.link(href=self.request.route_url(self.get_atom_feed_url, id=feed.id), rel='self')
        atom_feed.language('nl-BE')
        self.link_to_sibling(feed, 'previous', atom_feed)
        self.link_to_sibling(feed, 'next', atom_feed)
        return atom_feed

    def _generate_atom_feed(self, feed):
        """
        A function returning a feed like `feedgen.feed.FeedGenerator`.
        The function can be overwritten when used in other applications.

        :param feed: a feed object
        :return: an atom feed `feedgen.feed.FeedGenerator`
        """
        atom_feed = self.init_atom_feed(feed)
        atom_feed.title("Feed")
        return atom_feed
