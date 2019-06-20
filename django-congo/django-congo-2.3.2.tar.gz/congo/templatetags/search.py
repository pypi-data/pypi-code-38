# -*- coding: utf-8 -*-
from django.template import Library

register = Library()

@register.simple_tag()
def filter_add(*args):
    if len(args) == 3:
        filterset, filter_name, value = args
        f = filterset.get_filter(filter_name)
    elif len(args) == 2:
        f, value = args
        filterset = f.filterset
    else:
        return ''

    query_dict = f.get_query_dict(add_values = [value])

    if filterset.page_param in query_dict:
        del query_dict[filterset.page_param]

    return query_dict.urlencode()

@register.simple_tag()
def filter_del(*args):
    if len(args) == 3:
        filterset, filter_name, value = args
        f = filterset.get_filter(filter_name)
    elif len(args) == 2:
        f, value = args
        filterset = f.filterset
    else:
        return ''

    query_dict = f.get_query_dict(del_values = [value])

    if filterset.page_param in query_dict:
        del query_dict[filterset.page_param]

    return query_dict.urlencode()

@register.simple_tag()
def map_filter_value(*args):
    if len(args) == 3:
        filterset, filter_name, value = args
        f = filterset.get_filter(filter_name)
    elif len(args) == 2:
        f, value = args
    else:
        return ''

    return f.map_value(value)

@register.simple_tag()
def page_url(filterset, page_num):
    query_dict = filterset.get_query_dict()

    if page_num > 1:
        query_dict[filterset.page_param] = page_num
    elif filterset.page_param in query_dict:
        del query_dict[filterset.page_param]

    return query_dict.urlencode()

@register.simple_tag()
def ordering_url(ordering, asc):
    order_by = ordering.asc_ordering_name if asc else ordering.desc_ordering_name
    query_dict = ordering.get_query_dict(order_by)

    if ordering.filterset.page_param in query_dict:
        del query_dict[ordering.filterset.page_param]

    return query_dict.urlencode()

@register.simple_tag()
def reset_search_url(filterset, search_param = 'q'):
    query_dict = filterset.get_query_dict()
    if search_param in query_dict:
        del query_dict[search_param]
    return query_dict.urlencode()
