# -*- coding: utf-8 -*-
"""
This module defines a :class:`.Registry` of objects that takes care of automatically
updating the search index when we detect changes to the data in a
data store. The data store can be anything you like (Django ORM,
MongoDB, ...) - our examples use Django ORM.

This is completely decoupled from the :mod:`ievv_opensource.ievv_elasticsearch.search`
API.
"""
from __future__ import unicode_literals

import itertools

from django.conf import settings
from future.utils import with_metaclass
from pyelasticsearch import bulk_chunks, ElasticHttpNotFoundError

from ievv_opensource.ievv_elasticsearch import search
from ievv_opensource.ievv_elasticsearch.documentquery import DocumentQuery
from ievv_opensource.utils.singleton import Singleton


class AbstractDocumentMeta(type):
    """
    Metaclass for :class:`.AbstractDocument`.
    """
    def __new__(cls, name, parents, dct):
        if dct.get('objects', None) is None:
            dct['objects'] = DocumentQuery()
        new_class = super(AbstractDocumentMeta, cls).__new__(cls, name, parents, dct)
        new_class.objects.initialize(documentclass=new_class)
        return new_class


class AbstractDocument(with_metaclass(AbstractDocumentMeta, object)):
    """
    Base class for indexable documents for :class:`AbstractIndex`.
    """

    #: The document type to store this as in the index.
    doc_type = None

    #: The name of the index this document belongs to.
    #: This is set by :class:`.AbstractIndex` __init__ using :meth:`.set_index_name_for_all_document_classes`.
    index_name = None

    objects = None

    def get_document(self):
        """
        Get document for the ``doc`` argument of :meth:`pyelasticsearch.ElasticSearch.index_op`.
        """
        raise NotImplementedError()

    def get_id(self):
        """
        Get the ID to use for the indexed document. Defaults to ``None``,
        which means that a new document will be added to the index.
        """
        return None

    def get_parent_id(self):
        """
        Get the parent-child mapping parent ID document to use for the indexed document.
        This should only be overridden if you have a parent specified

        Defaults to ``None``, which means that no ``parent`` will be sent
        during indexing operations.
        """
        return None

    def get_index_op_kwargs(self):
        """
        Get kwargs for :meth:`pyelasticsearch.ElasticSearch.index_op`.

        You should not need to override this. Override :meth:`.get_document`,
        :meth:`.get_meta` and :obj:`~.AbstractDocument.doc_type`.
        """
        kwargs = {
            'doc': self.get_document(),
        }

        identifier = self.get_id()
        if identifier is not None:
            kwargs['id'] = identifier

        parent_id = self.get_parent_id()
        if parent_id is not None:
            kwargs['parent'] = parent_id

        return kwargs

    @classmethod
    def get_mapping_properties(cls):
        """
        Get the mapping properties for custom mappings for this
        document type. You only need to specify those mappings
        you do not want elasticsearch to create automatically.

        If you do not have any mappings, return ``None`` (or do not override).

        Examples:

            Simple example::

                class MyDocument(autoindex.AbstractDocument):
                    @classmethod
                    def get_mapping_properties(cls):
                        return {
                            'slug': {
                                'type': 'string',
                                'index': 'not_analyzed'
                            },
                            'author': {
                                'username': {
                                    'type': 'string',
                                    'index': 'not_analyzed'
                                }
                            }
                        }
        """
        return None

    @classmethod
    def get_mapping_parent_type(cls):
        """
        Get the type of the parent document for parent-child mapping.

        Lets say you have a Movie document, and want to create a
        parent-child relationship from the Category document with doc_type ``category``
        to the Movie. In the Movie document class, you would have to:

        - Override this method and return ``"category"``.
        - :meth:`.get_parent_id` and return the ID of the category.
        """
        return None

    @classmethod
    def get_mapping(cls):
        mappingdict = {}

        properties = cls.get_mapping_properties()
        if properties is not None:
            mappingdict['properties'] = properties

        parent_type = cls.get_mapping_parent_type()
        if parent_type is not None:
            mappingdict['_parent'] = {
                'type': parent_type
            }
        return mappingdict


class AbstractDictDocument(AbstractDocument):
    """
    Extends :class:`.AbstractDocument` to make it easy to
    put dicts in the database.
    """
    def __init__(self, document, id):
        """
        Parameters:
            document: A dict that pyelasticsearch can convert to JSON.
            id: The ElasticSearch id of the document. Set to ``None``
                to autocreate one.
        """
        self.document = document
        self.id = id

    def get_document(self):
        return self.document

    def get_id(self):
        return self.id


class AbstractIndex(object):
    """
    Base class for describing a search index.

    To register an index:

    1. Create a subclass of ``AbstractIndex`` and implement
       :meth:`~.AbstractIndex.iterate_all_documents` and override
       :obj:`~.AbstractIndex.document_classes`.
    2. Register the index with :class:`.Registry`.


    Examples:

        Minimal implementation for indexing a Django Product model::

            from ievv_opensource.ievv_elasticsearch import searchindex

            class ProductDocument(searchindex.AbstractDictDocument):
                doc_type = 'product'

            class ProductIndex(searchindex.AbstractIndex):
                name = 'products'
                document_classes = [
                    ProductDocument
                ]

                def iterate_all_documents(self):
                    for product in Product.objects.iterator():
                        yield ProductDocument({
                            'name': product.name,
                            'price': product.price
                        }, id=product.pk)

        If you want a more general search index of sellable items, you could
        do something like this::

            from ievv_opensource.ievv_elasticsearch import searchindex

            class ProductDocument(searchindex.AbstractDictDocument):
                doc_type = 'product'

            class ServiceDocument(searchindex.AbstractDictDocument):
                doc_type = 'service'

            class SellableItemIndex(searchindex.AbstractIndex):
                name = 'sellableitems'

                def iterate_all_documents(self):
                    for product in Product.objects.iterator():
                        yield ProductDocument({
                            'name': product.name,
                            'price': product.price,
                            'quantity': product.quantity
                        }, id=product.pk)
                    for service in Service.objects.iterator():
                        yield ServiceDocument({
                            'name': service.name,
                            'price': service.price,
                        }, id=service.pk)

        You could also move the document creation into the index document classes like
        this::

            class ProductDocument(searchindex.AbstractDictDocument):
                doc_type = 'product'

                def __init__(self, product):
                    self.product = product

                def get_id(self):
                    return self.product.id

                def get_document(self):
                   return {
                        'name': self.product.name,
                        'price': self.product.price,
                        'quantity': self.product.quantity
                   }

            class SellableItemIndex(searchindex.AbstractIndex):
                # ... same as above

                def iterate_all_documents(self):
                    for product in Product.objects.iterator():
                        yield ProductDocument(product)
                    # ...

    """

    #: The name of the index. Must be set in subclasses.
    name = None

    #: The number of docs to index per chunk when bulk updating the index.
    bulk_index_docs_per_chunk = 500

    #: The number of bytes to index per chunk when bulk updating the index.
    bulk_index_bytes_per_chunk = 10000

    #: The :class:`.AbstractDocument` classes used in this index.
    #: Can also be overridden via :meth:`.get_document_classes`.
    document_classes = []

    def __init__(self):
        self.set_index_name_for_all_document_classes()

    def set_index_name_for_all_document_classes(self):
        """
        Called by __init__ to set the :obj:`.AbstractDocument.index_name` of
        all documents in :obj:`~.AbstractIndex.document_classes`.
        """
        for document_class in self.document_classes:
            document_class.index_name = self.name

    def create(self):
        """
        Create the index and put any custom mappings.

        You should not need to override this, instead
        you should override :meth:`.get_document_classes` (and
        :meth:`.AbstractDocument.get_mapping_properties`), and
        :meth:`.get_settings`.
        """
        searchapi = search.Connection.get_instance()
        searchapi.elasticsearch.create_index(
            index=self.name, settings=self.get_settings())
        self.create_mappings()

    def get_settings(self):
        """
        Override this to provide settings for
        :meth:`pyelasticsearch.ElasticSearch.create_index` (which
        is called by :meth:`.create`.
        """
        return None

    def get_document_classes(self):
        """
        Returns an iterable of the :class:`.AbstractDocument`
        classes used in this index. Defaults to :obj:`.document_classes`.
        """
        return self.document_classes

    def get_document_classes_for_mapping(self):
        """
        Get the document classes for mapping. You normally do not
        have to override this - it only return :meth:`.get_document_classes`
        reversed. It is reversed because parent-child mappings have to be
        created in the child before the parent mapping can be created, but you
        normally want to index parents before children.
        """
        return reversed(self.get_document_classes())

    def create_mappings(self):
        """
        Create mappings.

        You should not need to override this, but instead you
        should override :meth:`.get_document_classes` (and
        :meth:`.AbstractDocument.get_mapping_properties`).
        """
        searchapi = search.Connection.get_instance()
        for document_class in self.get_document_classes_for_mapping():
            mappingdict = document_class.get_mapping()
            if mappingdict:
                searchapi.elasticsearch.put_mapping(self.name, document_class.doc_type, {
                    document_class.doc_type: mappingdict
                })

    def iterate_all_documents(self):
        """
        Iterate over all documents returning documents that are ready to be added to
        the index.

        Returns:
            An iterable of :class:`.AbstractDocument`.
        """
        raise NotImplementedError()

    def iterate_important_documents(self):
        """
        Just like :meth:`.iterate_all_documents`, but just yield the most important
        documents in case of a complete search index wipeout/rebuild.

        This is typically the newest and most important documents in the database.

        Defaults to returning an empty list.
        """
        return []

    def _iterate_index_operations(self, index_documents):
        searchapi = search.Connection.get_instance()
        for index_document in index_documents:
            kwargs = index_document.get_index_op_kwargs()
            yield searchapi.elasticsearch.index_op(**kwargs)

    def index_items(self, index_documents):
        """
        Index the given index_documents.

        Iterates over the given ``index_documents``, and send documents to
        :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.bulk` in
        batches of ``IEVV_ELASTICSEARCH_INDEX_BATCH_SIZE`` index_documents.

        Parameters:
            index_documents: An iterable of :class:`.AbstractDocument`.
        """
        searchapi = search.Connection.get_instance()

        for doc_type, index_documents_of_doc_type in itertools.groupby(
                index_documents,
                key=lambda index_document: index_document.doc_type):
            for chunk in bulk_chunks(
                    self._iterate_index_operations(index_documents_of_doc_type),
                    docs_per_chunk=self.bulk_index_docs_per_chunk,
                    bytes_per_chunk=self.bulk_index_bytes_per_chunk):
                searchapi.elasticsearch.bulk(chunk, index=self.name, doc_type=doc_type)

        # NOTE: We should be able to let AbstractDocument.get_index_op_kwargs()
        #       include the doc_type, and avoid the groupby(), but that randomly
        #       raises an exception complaining about missing type.
        # for chunk in bulk_chunks(
        #         self._iterate_index_operations(index_documents),
        #         docs_per_chunk=self.bulk_index_docs_per_chunk,
        #         bytes_per_chunk=self.bulk_index_bytes_per_chunk):
        #     searchapi.elasticsearch.bulk(chunk, index=self.name)

        if getattr(settings, 'IEVV_ELASTICSEARCH_AUTOREFRESH_AFTER_INDEXING', False):
            searchapi.refresh()

    def register_index_update_triggers(self):
        """
        Override this to register behaviors that trigger updates to the
        index. This is typically something like this:

        - Register one or more post_save signals that updates the
          index in realtime (be very careful with this since it can
          easily become a bottleneck).
        - Register one or more post_save signals that updates the
          index via a Celery job or some other background queue.

        Does nothing by default, so it is up to you to override it if
        you want to register any triggers.
        """

    def delete_index(self):
        """
        Delete this index.
        """
        searchapi = search.Connection.get_instance()
        searchapi.delete_index(self.name)

    @classmethod
    def get_instance(cls):
        """
        Get an instance of this class.

        Use this instead of instanciating the class directly.
        """
        return Registry.get_instance().get(cls.name)

    def rebuild_index(self):
        """
        Rebuild this index completely.

        Very useful when writing tests, but probably a bit less
        than optimal in production code/batch tasks unless you
        have a really small index. In production you should
        most likely want to create a management command to rebuild
        the index with the most recent/most important documents
        beeing indexed first.
        """
        try:
            self.delete_index()
        except ElasticHttpNotFoundError:
            pass
        self.create()
        self.index_items(self.iterate_all_documents())


class Registry(Singleton):
    """
    Registry of :class:`.AbstractIndex` objects.

    Examples:

        First, define an index (see :class:`.AbstractIndex`).

        Register the searchindex with the searchindex registry via an AppConfig for your
        Django app::

            from django.apps import AppConfig
            from ievv_opensource.ievv_elasticsearch import searchindex

            from myapp import elasticsearch_indexes


            class MyAppConfig(AppConfig):
                name = 'myapp'

                def ready(self):
                    searchindex.Registry.get_instance().add(elasticsearch_indexes.SellableItemIndex)
    """

    def __init__(self):
        super(Registry, self).__init__()
        self._indexes = {}

    def add(self, searchindex_class):
        """
        Add the given ``searchindex_class`` to the registry.
        """
        if searchindex_class.name in self._indexes:
            raise ValueError('A search index named "{}" is already registered in the search '
                             'index registry.'.format(searchindex_class.name))
        searchindex = searchindex_class()
        self._indexes[searchindex.name] = searchindex
        if not getattr(settings, 'IEVV_ELASTICSEARCH_DO_NOT_REGISTER_INDEX_UPDATE_TRIGGERS', None):
            searchindex.register_index_update_triggers()

    def get(self, indexname):
        """
        Get the index named ``indexname``.

        Returns: An :class:`.AbstractIndex` or ``None`` if no index matching
            the given ``indexname`` is found.
        """
        return self._indexes.get(indexname, None)

    def get_indexnames(self):
        """
        Get a view with the names of all indexes.
        """
        return self._indexes.keys()

    def __contains__(self, indexname):
        """
        Check if an index with the given name is in the registry.
        """
        return indexname in self._indexes


class MockableRegistry(Registry):
    """
    A non-singleton version of :class:`.Registry`. For tests.

    Typical usage in a test::

        class MockSearchIndex(searchindex.AbstractIndex):
            name = 'myindex'
            # ...

        mockregistry = searchindex.MockableRegistry()
        mockregistry.add(searchindex.MockSearchIndex())

        with mock.patch('ievv_opensource.ievv_elasticsearch.searchindex.Registry.get_instance',
                        lambda: mockregistry):
            pass  # ... your code here ...
    """

    def __init__(self):
        self._instance = None  # Ensure the singleton-check is not triggered
        super(MockableRegistry, self).__init__()
