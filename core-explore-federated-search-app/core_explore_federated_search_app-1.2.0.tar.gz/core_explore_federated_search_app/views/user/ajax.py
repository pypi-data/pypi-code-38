""" Ajax User core explore federated
"""
import json
from urlparse import urljoin

from django.core.urlresolvers import reverse
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render

import core_explore_common_app.components.query.api as api_query
import core_federated_search_app.components.instance.api as instance_api
from core_explore_common_app.components.abstract_query.models import Authentication, DataSource


def get_data_source_list_federated(request):
    """ Ajax method to fill the list of data sources.

    Args:
        request:

    Returns:

    """
    try:
        id_query = request.GET.get('id_query', None)

        if id_query is not None:
            # Get query from id
            query = api_query.get_by_id(id_query)
            instance_list = instance_api.get_all()

            item_list = []
            for instance_item in instance_list:
                checked = False

                # Generate url from instance information
                url_instance = _get_url_with_federated_rest_extension(instance_item)

                # compare instance with existing data source in query
                # in order to know if they have to be checked
                for data_source_item in query.data_sources:
                    if data_source_item.name == instance_item.name\
                       and data_source_item.url_query == url_instance:
                        checked = True
                        break

                # update the result item list for the context
                item_list.extend([{'instance_id': instance_item.id,
                                   'instance_name': instance_item.name,
                                   'is_checked': checked}])

            # Here, data sources are instances
            context_params = dict()
            context_params['instances'] = item_list

            # return context
            context = {}
            context.update(request)
            context.update(context_params)
            return render(request, 'core_explore_federated_search_app/user/data_sources/list-content.html', context)
        else:
            return HttpResponseBadRequest("Error during loading data sources from federated search.")
    except Exception as e:
        return HttpResponseBadRequest("Error during loading data sources from federated search.")


def update_data_source_list_federated(request):
    """ Ajax method to update query data sources in bdd.

    Args:
        request:

    Returns:

    """
    try:
        id_query = request.GET.get('id_query', None)
        id_instance = request.GET.get('id_instance', None)
        added = request.GET.get('to_be_added', None)
        to_be_added = json.loads(added) if added is not None else False

        # Get query from id
        if id_query is not None:
            query = api_query.get_by_id(id_query)

            # Get instance from id
            if id_instance is not None:
                instance = instance_api.get_by_id(id_instance)

                # Generate url from instance information
                url = _get_url_with_federated_rest_extension(instance)

            if to_be_added:
                # Instance have to be added in the query as a datasource
                authentication = Authentication(type='oauth2', params={'access_token': instance.access_token})
                data_source = DataSource(name=instance.name, url_query=url, authentication=authentication)
                data_source.query_options = {'instance_name': instance.name}
                api_query.add_data_source(query, data_source)
            else:
                # Data source have to be remove from the query
                data_source = api_query.get_data_source_by_name_and_url_query(query, instance.name, url)
                api_query.remove_data_source(query, data_source)

            return HttpResponse()
        else:
            return HttpResponseBadRequest("Error during data source selection.")
    except Exception as e:
        return HttpResponseBadRequest("Error during data source selection.")


def _get_url_with_federated_rest_extension(instance):
    """ Generate an url from instance object with federated rest extension.

    Args:
        instance:

    Returns:

    """
    return urljoin(instance.endpoint,
                   reverse("core_explore_federated_search_app_rest_execute_query"))
