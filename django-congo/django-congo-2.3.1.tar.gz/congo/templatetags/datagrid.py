# -*- coding: utf-8 -*-
import urllib
from django import template
register = template.Library()


PAGINATION_DEFAULT = 20

@register.inclusion_tag('datagrid/pagination_size_frag.html', takes_context = True)
def render_pagination_size_widget(context):
    "Usage {% render_pagination_size_widget %}"
    payload = {}
    payload['page_sizes'] = [1, 10, 20, 50, 100, 500]
    if 'request' in context:

        request = context['request']
        getvars = request.GET.copy()
        if 'page_size' in getvars:
            payload['current_page_size'] = int(getvars['page_size'])
            del getvars['page_size']
        else:
            from django.conf import settings
            payload['current_page_size'] = getattr(settings, 'PAGINATION_DEFAULT_PAGINATION', PAGINATION_DEFAULT)
        if 'page' in getvars:
            del getvars['page']
        if len(getvars.keys()) > 0:
            payload['getpagingvars'] = zip(getvars.keys(), getvars.values())
        else:
            payload['getpagingvars'] = []
    return payload


@register.inclusion_tag('datagrid/get_search_form.html', takes_context = True)
def get_search_form(context):
    getvars = {}
    if 'request' in context:
        request = context['request']
        getvars = request.GET.copy()
        if 'q' in getvars:
            searchterm = getvars['q']
            del getvars['q']
            return {'getvars':getvars.items(), 'searchterm': searchterm}
        else:
            return {'getvars':[], 'searchterm': ''}



@register.inclusion_tag('datagrid/get_filter_form.html', takes_context = True)
def get_filter_form(context):
    #TODO

    return context



@register.inclusion_tag('utils/datagrid/paginator.html', takes_context = True)
def paginator(context, adjacent_pages = 3):
    datagrid = context.get('datagrid')

    page_nums = range(max(1, datagrid.page.number - adjacent_pages), min(datagrid.paginator.num_pages, datagrid.page.number + adjacent_pages) + 1)

    return {
        'count': datagrid.paginator.count,
        'results_per_page': datagrid.paginate_by,
        'page_num': datagrid.page.number,
        'pages': datagrid.paginator.num_pages,
        'page_numbers': page_nums,
        'has_prev': datagrid.page.has_previous(),
        'has_next': datagrid.page.has_next(),
        'prev_page_num': datagrid.page.previous_page_number() if datagrid.page.has_previous() else None,
        'next_page_num': datagrid.page.next_page_number() if datagrid.page.has_next() else None,
        'prev_page_url': datagrid.get_prev_page_url(),
        'next_page_url': datagrid.get_next_page_url(),
        'prev_page_url': datagrid.get_first_page_url(),
        'next_page_url': datagrid.get_last_page_url(),
    }
