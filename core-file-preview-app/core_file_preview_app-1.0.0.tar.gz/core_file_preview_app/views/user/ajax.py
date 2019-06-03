""" Ajax User File preview
"""
import json
from urlparse import urlparse

from django.http.response import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from rest_framework import status

import core_main_app.utils.requests_utils.requests_utils as requests_utils
from core_main_app.settings import INSTALLED_APPS, SERVER_URI

if 'core_federated_search_app' in INSTALLED_APPS:
    import core_federated_search_app.components.instance.api as instance_api


def get_blob_preview(request):
    """ Get the blob preview

    Parameters:

        {
            "url_blob": url
        }

    Args:

        request: HTTP request

    Returns:

        - code: 200
          content: HttpResponse
        - code: 400
          content: Bad Request / unknown endpoit
        - code: 401
          content: Unauthorized
        - code: 500
          content: Internal server error
    """
    try:
        url = request.GET.get('url_blob', None)
        if url is not None:
            # extract the url base
            parsed_uri = urlparse(url)
            url_base = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            if url_base in SERVER_URI:
                # call the local instance giving sessionid through the call
                response = requests_utils.send_get_request(url, cookies={"sessionid": request.session.session_key})
            else:
                # so it can be from a federated instance
                if 'core_federated_search_app' in INSTALLED_APPS:
                    instance = instance_api.get_by_endpoint_starting_with(url_base)
                    if instance.endpoint in url:
                        # here we are sure that our given url
                        # is one of our known instances
                        headers = {'Authorization': 'Bearer ' + instance.access_token}
                        # FIXME: there is a oauth request util in core_explore_common_app
                        # should maybe move this util into the core_main_app and use it here
                        response = requests_utils.send_get_request(url, headers=headers)
            if response is not None:
                if response.status_code == status.HTTP_200_OK:
                    # we re-build the response from the response received
                    return_value = HttpResponse(response, content_type=response.headers["Content-type"])
                    return return_value
                else:
                    content = {'message': json.loads(response.text)['detail']}
                    return HttpResponseBadRequest(content, status=response.status_code)
            else:
                # at this point there is no known endpoint in our system
                content = {'message': "The endpoint is unknown"}
                return HttpResponseBadRequest(content)
        else:
            # handle missing parameters
            content = {'message': "Url blob not provided"}
            return HttpResponseBadRequest(content)
    except Exception as e:
        # if something went wrong, return an internal server error
        content = {'message': e.message}
        return HttpResponseServerError(content)
