# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ievv_opensource.ievv_elasticsearch import search


class DocumentQuery(object):
    """
    Query API for :class:`ievv_opensource.ievv_elasticsearch.autoindex.AbstractDocument`.

    Wraps many of the methods in :class:`ievv_opensource.ievv_elasticsearch.search.Connection`
    with methods that does not require you to specify ``index`` and ``doc_type``.

    It is easy to use::

        MyDocument.objects.wrapped_search_all()
        MyDocument.objects.get(id=10)
        MyDocument.objects.wrapped_get(id=10)

    Just read the docs for :class:`ievv_opensource.ievv_elasticsearch.search.Connection`,
    and ignore the ``index`` and ``doc_type`` arguments (they are added automatically).

    You can create your own custom DocumentQuery subclass and add it to your
    :class:`ievv_opensource.ievv_elasticsearch.autoindex.AbstractDocument` like this::

        from ievv_opensource.ievv_elasticsearch import autoindex

        class MyDocumentQuery(autoindex.DocumentQuery):
            def search_for_john(self):
                return self.wrapped_search('name:joe')

        class MyDocument(autoindex.AbstractDocument):
            objects = MyDocumentQuery()
            # ... other code required by AbstractDocument ...
    """
    def __init__(self):
        self.documentclass = None

    def initialize(self, documentclass):
        self.documentclass = documentclass

    def get_common_search_and_get_kwargs(self):
        return {
            'index': self.documentclass.index_name,
            'doc_type': self.documentclass.doc_type
        }

    def __wrap_searchapi_method(self, methodname, *args, **kwargs):
        searchapi = search.Connection.get_instance()
        full_kwargs = self.get_common_search_and_get_kwargs()
        full_kwargs.update(**kwargs)
        return getattr(searchapi, methodname)(*args, **full_kwargs)

    def index(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.index`
        except that you do not have to specify ``index`` or ``doc_type`` (they are
        added automatically before calling the low level API).
        """
        return self.__wrap_searchapi_method('index', *args, **kwargs)

    def bulk_index(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.bulk_index`
        except that you do not have to specify ``index`` or ``doc_type`` (they are
        added automatically before calling the low level API).
        """
        return self.__wrap_searchapi_method('bulk_index', *args, **kwargs)

    def bulk(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.bulk`
        except that you do not have to specify ``index`` or ``doc_type`` (they are
        added automatically before calling the low level API).
        """
        return self.__wrap_searchapi_method('bulk', *args, **kwargs)

    def search(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.search`
        except that you do not have to specify ``index`` or ``doc_type`` (they are
        added automatically before calling the low level API).
        """
        return self.__wrap_searchapi_method('search', *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.delete`
        except that you do not have to specify ``index`` or ``doc_type`` (they are
        added automatically before calling the low level API).
        """
        return self.__wrap_searchapi_method('delete', *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.get`
        except that you do not have to specify ``index`` or ``doc_type`` (they are
        added automatically before calling the low level API).
        """
        return self.__wrap_searchapi_method('get', *args, **kwargs)

    def wrapped_get(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.wrapped_get`
        except that you do not have to specify ``index`` or ``doc_type`` (they are
        added automatically before calling the low level API).
        """
        return self.__wrap_searchapi_method('wrapped_get', *args, **kwargs)

    def get_or_none(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.get_or_none`
        except that you do not have to specify ``index`` or ``doc_type`` (they are
        added automatically before calling the low level API).
        """
        return self.__wrap_searchapi_method('get_or_none', *args, **kwargs)

    def wrapped_get_or_none(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.wrapped_get_or_none`
        except that you do not have to specify ``index`` or ``doc_type`` (they are
        added automatically before calling the low level API).
        """
        return self.__wrap_searchapi_method('wrapped_get_or_none', *args, **kwargs)

    def wrapped_search(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.wrapped_search`
        except that you do not have to specify ``index`` or ``doc_type`` (they are
        added automatically before calling the low level API).
        """
        return self.__wrap_searchapi_method('wrapped_search', *args, **kwargs)

    def paginated_search(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.paginated_search`
        except that you do not have to specify ``index`` or ``doc_type`` (they are
        added automatically before calling the low level API).
        """
        return self.__wrap_searchapi_method('paginated_search', *args, **kwargs)

    def search_all(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.search_all`
        except ``index`` and ``doc_type`` is automatically restricted to this
        Document.
        """
        return self.__wrap_searchapi_method('search_all', *args, **kwargs)

    def wrapped_search_all(self, *args, **kwargs):
        """
        Works just like :meth:`ievv_opensource.ievv_elasticsearch.search.Connection.wrapped_search_all`
        except ``index`` and ``doc_type`` is automatically restricted to this
        Document.
        """
        return self.__wrap_searchapi_method('wrapped_search_all', *args, **kwargs)
