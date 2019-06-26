import elasticsearch.helpers
from elasticsearch_dsl.connections import connections


class IndexUpdater(object):
    """
    Makes it easier to (bulk)index and re-index documents for a DocType.

    .. attribute:: doctype_class

        The :class:`ievv_opensource.ievv_elasticsearch2.doctype.DocType` subclass
        this IndexUpdater is for. See :meth:`.set_doctype_class`.
    """

    #: Low priority constant for the ``priority argument for :meth:`.bulk_reindex_by_priority`.
    PRIORITY_LOW = 'low'

    #: Medium priority constant for the ``priority argument for :meth:`.bulk_reindex_by_priority`.
    PRIORITY_MEDIUM = 'medium'

    #: High priority constant for the ``priority argument for :meth:`.bulk_reindex_by_priority`.
    PRIORITY_HIGH = 'high'

    def __init__(self, doctype_class=None):
        """
        Args:
            doctype_class: If this is not ``None``, __init__ will call :meth:`.set_doctype_class`
                with this as input.
        """
        self.doctype_class = None
        if doctype_class:
            self.set_doctype_class(doctype_class=doctype_class)

    def clone(self):
        return self.__class__()

    def set_doctype_class(self, doctype_class):
        """
        Set :attr:`~.IndexUpdater.doctype_class`.

        You normally do not call this directly - this is called during class creation
        of :class:`ievv_opensource.ievv_elasticsearch2.doctype.DocType` if the
        DocType subclass has an ``indexupdater`` attribute. Read more about this
        in the docs for :class:`ievv_opensource.ievv_elasticsearch2.doctype.DocTypeMeta`.

        Args:
            doctype_class: The :class:`ievv_opensource.ievv_elasticsearch2.doctype.DocType` subclass
                to set as the ``doctype_class``.
        """
        self.doctype_class = doctype_class

    def get_connection(self, using=None):
        """
        Get ElasticSearch client connection.

        Should not need to use this unless you are making a subclass and adding new features.

        Args:
            using: See :meth:`elasticsearch_dsl.connections.Connections.get_connection`.
                Defaults to the default connection for the DocType class.

        Returns:
            elasticsearch.client.Elasticsearch: An Elasticsearch object for the connection.
        """
        return connections.get_connection(using or self.doctype_class.get_doc_type_options().using)

    def __iterate_bulk_index_actions(self, doctype_object_iterable):
        for doctype_object in doctype_object_iterable:
            yield doctype_object.to_dict(include_meta=True)

    def bulk_index(self, doctype_object_iterable, using=None):
        """
        Bulk index the provided doctype objects using :func:`elasticsearch.helpers.bulk`.

        Args:
            doctype_object_iterable: An iteratable of DocType objects.
            using: See :meth:`.get_connection`.
        """
        actions = self.__iterate_bulk_index_actions(doctype_object_iterable=doctype_object_iterable)
        elasticsearch.helpers.bulk(
            client=self.get_connection(using=using),
            actions=actions)

    def make_doctype_object_iterable_from_queryset(self, queryset):
        """
        Make a :class:`ievv_opensource.ievv_elasticsearch2.doctype.DocType` object iterable
        from the provided queryset.

        Args:
            queryset: A Django QuerySet. This is expected to be a queryset for
                the ``model_class`` registered for the doctype_class.

        Returns:
            iterable: The created iterable.
        """
        for modelobject in queryset:
            yield self.doctype_class.modelmapper.to_doctype_object(modelobject=modelobject)

    def optimize_queryset_by_expected_result_count(self, queryset, expected_result_count):
        """
        The memory usage of Django QuerySets increase with the number of
        objects in the result. This can be avoided usig ``QuerySet.iterator()``,
        but that is slower. When we know the number of objects a query will
        return, we can automatically determine the method to use.

        This method sets the threshold for switching to ``iterator()`` at
        ``expected_result_count > 1000``. This should be an OK default, but
        you can adjust this and benchmark results for your use cases.

        Args:
            queryset: A Django QuerySet object.
            expected_result_count: The expected number of results.

        Returns:
            QuerySet: The modified/optimized QuerySet.
        """
        if expected_result_count > 1000:
            return queryset.iterator()
        else:
            return queryset.all()

    def make_queryset_from_model_ids(self, ids):
        return self.doctype_class.model_class.objects.filter(id__in=ids)

    def bulk_index_model_ids(self, ids, using=None):
        """
        Bulk index the provided IDs using :func:`elasticsearch.helpers.bulk`.

        This only works if the :attr:`.IndexUpdater.doctype_class` has a ``model_class``
        attribute, so this is intended for doctypes that subclass
        :class:`ievv_opensource.ievv_elasticsearch2.doctype.ModelDocType`.

        Args:
            ids: A list or set (or something that can be iterated and has a __len__())
                of Django model object IDs.
            using: See :meth:`.get_connection`.
        """
        if not hasattr(self.doctype_class, 'model_class'):
            raise AttributeError(
                'The doctype_class ({}.{}) for {}.{} does not have a model_class attribute.'.format(
                    self.doctype_class.__module__, self.doctype_class.__name__,
                    self.__class__.__module__, self.__class__.__name__))
        queryset = self.make_queryset_from_model_ids(ids=ids)
        queryset = self.optimize_queryset_by_expected_result_count(queryset=queryset,
                                                                   expected_result_count=len(ids))
        doctype_object_iterable = self.make_doctype_object_iterable_from_queryset(queryset=queryset)
        return self.bulk_index(doctype_object_iterable=doctype_object_iterable, using=using)

    def iterate_doctype_objects_for_reindexing(self, priority=None, using=None):
        """
        Iterate doctype objects for :meth:`.bulk_reindex_by_priority`.

        Unless this IndexUpdater is for a :class:`ievv_opensource.ievv_elasticsearch2.doctype.ModelDocType`,
        this method must be overridden in subclasses if you want to be able to reindex all your documents.

        If you override this method and your data source is Django, you should use
        :meth:`.optimize_queryset_by_expected_result_count` to wrap your
        queryset to ensure that your queries perform well no matter how many
        objects you are indexing.

        Args:
            priority: See :meth:`.bulk_reindex_by_priority`.
            using: See :meth:`.get_connection`. Use this if you connect to ElasticSearch
                to create the DocType iterable.

        Returns:
            iterator: Iterator of DocType objects.
        """
        if priority is not None:
            raise NotImplementedError('Support for priority {} is not implemented.'.format(priority))
        if hasattr(self.doctype_class, 'model_class'):
            queryset = self.doctype_class.model_class.objects.all()
            expected_result_count = queryset.count()
            self.optimize_queryset_by_expected_result_count(
                queryset=queryset,
                expected_result_count=expected_result_count
            )
            return self.make_doctype_object_iterable_from_queryset(
                queryset=queryset)
        else:
            raise NotImplementedError('Unless you are using this IndexUpdater with a '
                                      'ModelDocType, iterate_doctype_objects_for_reindexing() must '
                                      'be overridden.')

    def bulk_reindex_by_priority(self, priority=None, using=None):
        """
        Re-index documents of this DocType.

        The documents to reindex is retrieved using :meth:`.iterate_doctype_objects_for_reindexing`.
        You should normally override :meth:`.iterate_doctype_objects_for_reindexing`
        instead of this method.

        Args:
            priority: Only index items with the provided priority. Defaults to ``None`` which
                means reindex ALL documents. The intention of this argument is to enable you
                to segment you data into different priorities
                by overriding :meth:`.iterate_doctype_objects_for_reindexing`. Unless your app
                has very special needs, we recommend that you use :obj:`.IndexUpdater.PRIORITY_LOW`,
                :obj:`.IndexUpdater.PRIORITY_MEDIUM` and :obj:`.IndexUpdater.PRIORITY_HIGH` as constants
                for priorities. This is enough for most needs, and using a common set of priorities
                makes for more reusable code.
            using: See :meth:`.get_connection`.
        """
        doctype_object_iterable = self.iterate_doctype_objects_for_reindexing(priority=priority, using=using)
        self.bulk_index(
            doctype_object_iterable=doctype_object_iterable,
            using=using)
