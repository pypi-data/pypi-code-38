# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
# Copyright (C) 2018 RERO.
#
# Invenio-Circulation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Circulation search API."""

from elasticsearch_dsl import VERSION as ES_VERSION
from invenio_search.api import RecordsSearch

from invenio_circulation.errors import MissingRequiredParameterError

from ..proxies import current_circulation


class LoansSearch(RecordsSearch):
    """RecordsSearch for borrowed documents."""

    class Meta:
        """Search only on loans index."""

        index = "loans"
        doc_types = None

    def exclude(self, *args, **kwargs):
        """Add method `exclude` to old elastic search versions."""
        if ES_VERSION[0] == 2:
            from elasticsearch_dsl.query import Bool, Q
            return self.query(Bool(filter=[~Q(*args, **kwargs)]))
        else:
            return super(LoansSearch, self).exclude(*args, **kwargs)


def search_by_pid(item_pid=None, document_pid=None, filter_states=None,
                  exclude_states=None, sort_by_field=None, sort_order="asc"):
    """Retrieve loans attached to the given item or document."""
    search = current_circulation.loan_search

    if document_pid:
        search = search.filter("term", document_pid=document_pid)
    elif item_pid:
        search = search.filter("term", item_pid=item_pid)
    else:
        raise MissingRequiredParameterError(description=(
            "One of the parameters 'item_pid' "
            "or 'document_pid' is required."
        ))

    if filter_states:
        search = search.filter("terms", state=filter_states)
    elif exclude_states:
        search = search.exclude("terms", state=exclude_states)

    if sort_by_field:
        search = search.sort({sort_by_field: {"order": sort_order}})

    return search


def search_by_patron_item_or_document(patron_pid, item_pid=None,
                                      document_pid=None, filter_states=None):
    """Retrieve loans for patron given an item."""
    search = current_circulation.loan_search
    search = search \
        .filter("term", patron_pid=patron_pid)

    if item_pid:
        search = search.filter("term", item_pid=item_pid)
    if document_pid:
        search = search.filter("term", document_pid=document_pid)

    if filter_states:
        search = search.filter("terms", state=filter_states)

    return search


def search_by_patron_pid(patron_pid):
    """Retrieve loans of a patron."""
    search = current_circulation.loan_search
    search = search.filter("term", patron_pid=patron_pid)
    return search
