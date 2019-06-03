"""Template tag to include the search bar
"""
from django import template

from core_explore_common_app.components.query import api as query_api
from core_explore_common_app.components.query.models import Query
from core_explore_common_app.views.user.ajax import add_local_data_source
from core_explore_keyword_app.forms import KeywordForm

register = template.Library()


@register.inclusion_tag('core_explore_keyword_app/user/embedded_search_bar.html',
                        takes_context=True)
def show_search_bar(context):
    """ Include the search bar in a template.

    Args:
        context: Context

    Returns:

    """
    request = context['request']

    # create Query
    query = Query(user_id=str(request.user.id), templates=[])

    # add local data source to the query
    add_local_data_source(request, query)

    # set visibility
    query_api.set_visibility_to_query(query)

    # upset the query
    query_api.upsert(query)

    # create keyword form
    data_form = {
        'query_id': str(query.id),
        'user_id': query.user_id,
    }

    search_form = KeywordForm(data=data_form)

    context = {
        "data": {
            'search_form': search_form,
            'query_id': search_form.data['query_id'],
         }
    }

    return template.RequestContext(request, context)
