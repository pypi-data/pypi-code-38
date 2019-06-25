from django.http import Http404
from django.views.generic import TemplateView as DjangoTemplateView
from pyelasticsearch import ElasticHttpNotFoundError

from ievv_opensource.ievv_elasticsearch import search


class ViewMixin:
    """
    Makes it a bit easier to search with paging.

    Examples:

        Minimal example::

            class MyView(TemplateView, searchview.ViewMixin):
                template_name = 'myapp/mytemplate.html'

                def get_search_query(self):
                    return {
                        'match_all': {}
                    }

                def get_context_data(self, **kwargs):
                    context = super().get_context_data(**kwargs)
                    context['searchpaginator'] = self.get_paginator()

        A more full featured example::

            class MyView(TemplateView, searchview.ViewMixin):
                template_name = 'myapp/mytemplate.html'
                page_size = 30
                paging_querystring_attribute = 'page'

                def get_search_query(self):
                    return {
                        'match_all': {}
                    }

                def get_search_sort(self):
                    return {'name': {'order': 'asc'}}

                def get_context_data(self, **kwargs):
                    context = super().get_context_data(**kwargs)
                    context['searchpaginator'] = self.get_paginator()


    You should normally just need to override:

    - :meth:`.get_search_query`.
    - :meth:`.get_search_sort` (optional).
    - :meth:`.get_page_size` or :obj:`.page_size` (optional).
    - :meth:`.get_resultitemwrapper` (optional).
    - :meth:`.get_paging_querystring_attribute` or :obj:`.paging_querystring_attribute` (optional).

    And call :meth:`.get_paginator` to retrieve results that you can iterate
    and ask for pagination information.
    """

    #: The number of items per page. Defaults to ``100``. See :meth:`~.ViewMixin.get_page_size`.
    page_size = 100

    #: See :meth:`~ViewMixin.get_search_index`. Defaults to ``None``.
    search_index = None

    #: See :meth:`~ViewMixin.get_search_doc_type`. Defaults to ``None``.
    search_doc_type = None

    #: The querystring attribute to use for paging. Defaults to ``p``.
    #: Used by :meth:`.get_paging_querystring_attribute`.
    paging_querystring_attribute = 'p'

    def get_page_size(self):
        """
        Get the page size.

        Defaults to returning :obj:`.page_size`.
        """
        return self.page_size

    def get_paging_querystring_attribute(self):
        """
        The querystring attribute to use for paging.
        Defaults to :obj:`.paging_querystring_attribute`.
        """
        return self.paging_querystring_attribute

    def get_current_page_number(self):
        """
        Get the current page number from ``request.GET[self.get_paging_querystring_attribute()]``.

        You can override this if you want to get the page number some other way.
        """
        pagenumber = self.request.GET.get(self.get_paging_querystring_attribute(), 0)
        try:
            pagenumber = int(pagenumber)
        except TypeError:
            pagenumber = 0
        return pagenumber

    def get_search_index(self):
        """
        Get the search index name.

        Defaults to :obj:`.search_index`.
        """
        return self.search_index

    def get_search_doc_type(self):
        """
        Get the document types to search. Can be a single document type
        or an iterable of document types.

        Defaults to :obj:`.search_doc_type`.
        """
        return self.search_doc_type

    def get_search_query(self):
        """
        Get the query attribute of the elasticsearch query.

        You MUST override this.

        While :meth:`.get_search_full_query` returns something like::

            {
                'query': {
                    'match_all': {}
                },
                'size': 20,
                'from': 40
            }

        This method should only return the value of the ``query`` key::

            {
                'match_all': {}
            }

        """
        raise NotImplementedError()

    def get_search_sort(self):
        """
        Get the sort dict for the search query.

        While :meth:`.get_search_full_query` returns something like::

            {
                'query': {
                    'match_all': {}
                },
                'sort': {'name': {'order': 'asc'}},
                'size': 20,
                'from': 40
            }

        This method should only return the value of the ``sort`` key::

            {'name': {'order': 'asc'}}

        Defaults to ``None``, which means no sorting is performed.
        """
        return None

    def get_search_full_query(self):
        """
        Builds the full ElasticSearch query dict including paging.

        You should normally not override this directly. Override
        :meth:`.get_search_query` and :meth:`.get_search_sort` instead.
        """
        full_query = {
            'query': self.get_search_query(),
        }
        page_size = self.get_page_size()
        if page_size:
            full_query['size'] = self.get_page_size()
            full_query['from'] = self.get_page_size() * self.get_current_page_number()

        sortdict = self.get_search_sort()
        if sortdict:
            full_query['sort'] = sortdict
        return full_query

    def get_paginated_search_kwargs(self):
        """
        Get the kwargs for :meth:`ievv_opensource.ievv_elasticsearch.search.Connection#paginated_search`.
        """
        kwargs = {
            'query': self.get_search_full_query(),
            'index': self.get_search_index(),
            'doc_type': self.get_search_doc_type(),
            'page_number': self.get_current_page_number(),
            'page_size': self.get_page_size(),
            'resultitemwrapper': self.get_resultitemwrapper()
        }
        return kwargs

    def get_resultitemwrapper(self):
        """
        See the ``resultitemwrapper`` argument for
        :class:`ievv_opensource.ievv_elasticsearch.search.Paginator`.
        """
        return None

    def get_paginator(self):
        """
        Performs the search and wraps it in a :class:`ievv_opensource.ievv_elasticsearch.search.Paginator`.

        Raises:
            :class:`django.http.response.Http404` if the search does not match
            any items. You will typically catch this exception and
            show a message in a normal search setting.
        """
        searchapi = search.Connection.get_instance()
        try:
            return searchapi.paginated_search(**self.get_paginated_search_kwargs())
        except ElasticHttpNotFoundError:  # If the search does not match any items
            raise Http404()


class View(DjangoTemplateView, ViewMixin):
    """
    A Django TemplateView with :class:`.ViewMixin`.

    For usage example, see :class:`.ViewMixin` (just inherit from
    this class instead of TemplateView and ViewMixin)
    """


class SortMixin:
    """
    Mixin class for sort-keyword in the querystring based sort (E.g.: ``?o=name``).

    This MUST be mixed in before :class:`.View` (or :class:`.ViewMixin`), since
    it overrides :meth:`.ViewMixin.get_search_sort`.

    Examples:

        Simple example of a map where ``?o=name`` sorts by name
        ascending and ``?o=created`` sorts by created datetime descending::

            class MySortView(searchview.SortMixin, searchview.View):
                default_sort_keyword = 'name'

                sort_map = {
                    'name': {'name': {'order': 'asc'}},
                    'created': {'created_datetime': {'order': 'desc'}},
                }

                def get_search_query(self):
                    return {
                        'match_all': {}
                    }

                def get_context_data(self, **kwargs):
                    context = super().get_context_data(**kwargs)
                    context['searchpaginator'] = self.get_paginator()

        The default if ``?o`` is not specified will be to sort by name ascending.

    You should normally just need to override:

    - :meth:`.get_sort_map` or :obj:`.sort_map`
    - :meth:`.get_default_sort_keyword` or :obj:`.default_sort_keyword`.

    If you do not get the sort keyword from the querystring, you also
    need to override :meth:`.get_sort_keyword`.

    If you do not want to use ``o`` as the querystring attribute
    for sort keywords, you need to override :meth:`.get_sort_querystring_attribute`
    or :obj:`.sort_querystring_attribute`.
    """

    #: The querystring attribute to use for sort. Used by
    #: :meth:`.get_sort_querystring_attribute`.
    #: Defaults to ``o`` (for ordering). We use ``o`` instead of
    #: ``s`` to avoid collision with :class:`.SearchMixin`.
    sort_querystring_attribute = 'o'

    #: The default sort keyword to use when ordering is
    #: not specified in the querystring.
    #: Defaults to ``"default"``.
    default_sort_keyword = 'default'

    #: See :meth:`.get_sort_map`.
    sort_map = {}

    def get_sort_querystring_attribute(self):
        """
        The querystring attribute to use for sort.
        Defaults to :obj:`.sort_querystring_attribute`.
        """
        return self.sort_querystring_attribute

    def get_default_sort_keyword(self):
        """
        Get the default sort keyword to use when ordering is not
        specified in the querystring. Defaults to
        :obj:`default_sort_keyword`.
        """
        return self.default_sort_keyword

    def get_sort_keyword(self):
        """
        Get the sort keyword. Defaults to getting it from the
        querystring argument defined by :meth:`.get_sort_querystring_attribute`,
        and falling back to :meth:`.get_default_sort_keyword`.
        """
        return self.request.GET.get(
            self.sort_querystring_attribute,
            self.get_default_sort_keyword())

    def get_sort_map(self):
        """
        Get a mapping object that maps keywords
        to sort dicts compatible with elasticsearch.
        Defaults to :obj:`.sort_map`.
        """
        if self.sort_map:
            return self.sort_map
        else:
            raise NotImplementedError('You must override get_sort_map or set sort_map.')

    def get_search_sort_by_keyword(self, keyword):
        """
        Get the elasticsearch sort dict by looking up the
        given ``keyword`` in :meth:`.get_sort_map`.

        If the given ``keyword`` is not in :meth:`.get_sort_map`,
        we fall back on :meth:`.get_default_sort_keyword`.
        """
        sort_map = self.get_sort_map()
        try:
            return sort_map[keyword]
        except KeyError:
            return sort_map[self.get_default_sort_keyword()]

    def get_search_sort(self):
        """
        Overrides :meth:`.ViewMixin.get_search_sort` and gets
        the value of the sort dict by via :meth:`.get_search_sort_by_keyword`
        with :meth:`.get_sort_keyword` as the keyword argument.

        This means that you should not override this method, but instead override:

        - :meth:`.get_sort_map` (or :obj:`.sort_map`)
        - :meth:`.get_default_sort_keyword` (or :obj:`.default_sort_keyword`)
        """
        return self.get_search_sort_by_keyword(self.get_sort_keyword())


class SearchMixin:
    """
    Mixin class that makes it slightly easier to add search
    via a querystring attribute (defaults to ``?s=<search_string>``).

    This is perfect for views that use ElasticSearch for traditional
    search where a user types in a string, and we wish to search
    some fields for that string.

    This MUST be mixed in before :class:`.View` (or :class:`.ViewMixin`) , since
    it overrides :meth:`.ViewMixin.get_search_query`.

    Can safely be used with :class:`.SortMixin`. The order of
    :class:`.SortMixin` and :class:`.SearchMixin` does not
    matter, but they must both be mixed in before :class:`.View`
    (or :class:`.ViewMixin`).

    Examples:

        Minimal example::

            class MySearchView(searchview.SearchMixin, searchview.View):
                search_query_fields = ['name', 'email']

                def get_context_data(self, **kwargs):
                    context = super().get_context_data(**kwargs)
                    context['searchpaginator'] = self.get_paginator()

    """
    #: The querystring attribute to use for sort. Used by
    #: :meth:`.get_sort_querystring_attribute`.
    #: Defaults to ``s``.
    search_querystring_attribute = 's'

    #: List of fields for :meth:`.get_search_query_fields`.
    #: Defaults to empty list, so you need to set this,
    #: or override :meth:`.get_search_query_fields`.
    search_query_fields = []

    def get_search_querystring_attribute(self):
        """
        The querystring attribute to use for search.
        Defaults to :obj:`.search_querystring_attribute`.
        """
        return self.search_querystring_attribute

    def clean_search_string(self, search_string):
        """
        Can be overridden to clean/modify the search_string.

        Does nothing by default.

        Used by :meth:`.get_search_string`.
        """
        return search_string

    def get_search_string(self):
        """
        Get the search string.

        We get the search string from the querystring, and clean it with
        :meth:`.clean_search_string` before returning it.
        """
        search_string = self.request.GET.get(self.get_search_querystring_attribute(), '')
        return self.clean_search_string(search_string)

    def get_search_query_fields(self):
        """
        Get the fields for the ``multi_match`` query performed by
        :meth:`.get_search_query_with_search_string`.

        Defaults to :obj:`.search_query_fields`
        """
        if self.search_query_fields:
            return self.search_query_fields
        else:
            raise NotImplementedError('You must override get_search_query_fields() or set search_query_fields.')

    def get_search_query_with_search_string(self, search_string):
        """
        Called by :meth:`.get_search_query` when :meth:`.get_search_string`
        returns something.

        Defaults to a ``multi_matach`` query with the fields returned
        by :meth:`.get_search_query_fields`.

        You will not need to override this for simple cases, but for more
        complex queries with boosting, filtering, etc. you will most likely
        have to override this.
        """
        return {
            'multi_match': {
                'query': search_string,
                'fields': self.get_search_query_fields()
            }
        }

    def get_search_query_without_search_string(self):
        """
        Called by :meth:`.get_search_query` when :meth:`.get_search_string`
        returns empty string or ``None``.

        Defaults to a ``match_all`` query.
        """
        return {
            'match_all': {}
        }

    def get_search_query(self):
        """
        Overrides :meth:`.ViewMixin.get_search_query` and splits the logic into
        two separate states:

        1. We have a search string, call :meth:`.get_search_query_with_search_string`.
        2. We do not have a search string, call :meth:`.get_search_query_without_search_string`.

        You should not need to override this method, but instead override:

        - :meth:`.get_search_fields` or perhaps :meth:`.get_search_query_with_search_string` (for advanced cases).
        - Perhaps :meth:`.get_search_query_without_search_string`.
        """
        search_string = self.get_search_string()
        if search_string:
            return self.get_search_query_with_search_string(search_string)
        else:
            return self.get_search_query_without_search_string()
