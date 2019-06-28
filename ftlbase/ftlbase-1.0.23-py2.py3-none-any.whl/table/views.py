#!/usr/bin/env python
# coding: utf-8
import json

import django.db.models.fields
from django.core.exceptions import FieldError
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse
from django.views.generic.list import BaseListView

from table.forms import QueryDataForm
from table.tables import TableDataMap

try:
    unicode = unicode
except (ImportError, NameError):
    # 'unicode' is undefined, must be Python 3
    from urllib.parse import unquote
    from functools import reduce

    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    from urllib import unquote

    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(
            self.convert_context_to_json(context),
            content_type='application/json',
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        """
        Convert the context dictionary into a JSON object.
        """
        return json.dumps(context, cls=DjangoJSONEncoder)


def find_field(cls, lookup):
    """Take a root class and a field lookup string
    and return the model field if it exists or raise
    a django.db.models.fields.FieldDoesNotExist if the
    field is not found."""

    if lookup is None:
        return None

    lookups = list(reversed(lookup.split("__")))

    field = None

    while lookups:

        f = lookups.pop()

        # will raise FieldDoesNotExist exception if not found
        field = cls._meta.get_field(f)

        try:
            cls = field.rel.to
        except AttributeError:
            if lookups:
                # not all lookup fields were used
                # must be an incorrect lookup
                raise django.db.models.fields.FieldDoesNotExist(lookup)

    return field


BOOL_TYPE = django.db.models.fields.BooleanField().get_internal_type()


class FeedDataView(JSONResponseMixin, BaseListView):
    """
    The view to feed ajax data of table.
    """

    context_object_name = 'object_list'

    def get(self, request, *args, **kwargs):
        if not hasattr(self, 'token'):
            self.token = kwargs["token"]
        self.columns = TableDataMap.get_columns(self.token)

        query_form = QueryDataForm(request.GET)
        if query_form.is_valid():
            self.query_data = query_form.cleaned_data
        else:
            return self.render_to_response({"error": "Query form is invalid."})

        # Busca filtros do request da URL
        self.search_filters = {}
        self.search_filters.update(self.request.GET.dict())

        return BaseListView.get(self, request, *args, **kwargs)

    def get_queryset(self):
        model = TableDataMap.get_model(self.token)
        if model is None:
            return None
        return model.objects.all()

    def filter_queryset(self, queryset):
        def get_filter_arguments(filter_target):
            """
            Get `Q` object passed to `filter` function.
            """
            queries = []
            fields = [col.field for col in self.columns if col.searchable]
            for field in fields:
                key = "__".join(field.split(".") + ["icontains"])
                value = filter_target
                queries.append(Q(**{key: value}))
            return reduce(lambda x, y: x | y, queries)

        filter_text = self.query_data["sSearch"]
        if filter_text:
            for target in filter_text.split():
                queryset = queryset.filter(get_filter_arguments(target))
        # return queryset

        return self.filter_queryset2(queryset)

    def filter_queryset2(self, queryset):
        """ filter the input queryset according to column definitions.

        This method is awful :(
        """
        fieldsW = [col.field for col in self.columns]

        for col_num, field in enumerate(fieldsW):

            search_term = self.search_filters.get("sSearch_%d" % col_num, None)
            # try:
            # search_term = self.query_data["sSearch_%d" % col_num]
            # except KeyError:
            # search_term = None
            # filtering = self.search_fields.get(field, True)
            filtering = self.columns[col_num].searchable

            try:
                mdl_field = find_field(TableDataMap.get_model(self.token), field)
            except django.db.models.fields.FieldDoesNotExist:
                mdl_field = None
            # print >>sys.stderr, search_term
            # print >>sys.stderr, mdl_field
            # print >>sys.stderr, "sSearch_%d" % col_num

            if filtering and search_term:
                if isinstance(filtering, basestring):
                    if 'select' in self.extra and field in self.extra['select']:
                        queryset = queryset.extra(where=["{0} LIKE %s".format(field)],
                                                  params=["%{0}%".format(search_term)])
                    else:
                        queryset = queryset.filter(**{filtering: search_term})
                else:

                    try:
                        # iterable of search fields e.g. search_fields = {"name": ("first_name", "last_name",)}
                        queries = reduce(lambda q, f: q | Q(**{f: search_term}), filtering, Q())
                        queryset = queryset.filter(queries)

                    except TypeError:

                        if mdl_field and mdl_field.get_internal_type() == BOOL_TYPE:
                            import ipdb
                            ipdb.set_trace()

                            filtering = field
                            if search_term == "False":
                                search_term = False
                            elif search_term == "True":
                                search_term = True
                            else:
                                search_term = None
                        else:
                            # fall back to default search (e.g order_fields ={"first_name": True})
                            filtering = "{0}__icontains".format(field)
                        try:
                            queryset = queryset.filter(**{filtering: search_term})
                        except FieldError:
                            raise TypeError("You can not filter on the '{field}' field. Filtering on"
                                            " GenericForeignKey's and callables must be explicitly "
                                            "disabled in `search_fields`".format(
                                field=field))
        # print >>sys.stderr, list(queryset)
        return queryset

    def sort_queryset(self, queryset):
        def get_sort_arguments():
            """
            Get list of arguments passed to `order_by()` function.
            """
            arguments = []
            for key, value in self.query_data.items():
                if not key.startswith("iSortCol_"):
                    continue
                field = self.columns[value].field.replace('.', '__')
                dir = self.query_data["sSortDir_" + key.split("_")[1]]
                if dir == "asc":
                    arguments.append(field)
                else:
                    arguments.append("-" + field)
            return arguments

        order_args = get_sort_arguments()
        if order_args:
            queryset = queryset.order_by(*order_args)
        return queryset

    def paging_queryset(self, queryset):
        start = self.query_data["iDisplayStart"]
        length = self.query_data["iDisplayLength"]
        if length < 0:
            return queryset
        else:
            return queryset[start: start + length]

    def convert_queryset_to_values_list(self, queryset):
        # FIXME: unit test
        return [
            [col.render(obj) for col in self.columns]
            for obj in queryset
        ]

    def get_queryset_length(self, queryset):
        return queryset.count()

    def get_context_data(self, **kwargs):
        """
        Get context data for datatable server-side response.
        See http://www.datatables.net/usage/server-side
        """
        sEcho = self.query_data["sEcho"]

        context = super(BaseListView, self).get_context_data(**kwargs)
        queryset = context["object_list"]
        if queryset is not None:
            total_length = self.get_queryset_length(queryset)
            queryset = self.filter_queryset(queryset)
            display_length = self.get_queryset_length(queryset)

            queryset = self.sort_queryset(queryset)
            queryset = self.paging_queryset(queryset)
            values_list = self.convert_queryset_to_values_list(queryset)
            context = {
                "sEcho": sEcho,
                "iTotalRecords": total_length,
                "iTotalDisplayRecords": display_length,
                "aaData": values_list,
            }
        else:
            context = {
                "sEcho": sEcho,
                "iTotalRecords": 0,
                "iTotalDisplayRecords": 0,
                "aaData": [],
            }
        return context

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context)
