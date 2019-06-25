import urllib.parse
import requests
import zalando_kubectl.utils

from zalando_kubectl.utils import auth_headers


def emergency_service_url(config):
    # emergency-access service URL isn't stored anywhere in the cluster metadata,
    # so we need to build it manually by taking the API server URL and replace the first
    # component with emergency-access.
    api_server_host = urllib.parse.urlparse(zalando_kubectl.utils.get_api_server_url(config)).hostname
    _, cluster_domain = api_server_host.split(".", 1)
    return "https://emergency-access-service.{}".format(cluster_domain)


def create(config, access_type, reference_url, user, reason):
    response = requests.post('{}/access-requests'.format(emergency_service_url(config)),
                             json={'access_type': access_type,
                                   'reference_url': reference_url,
                                   'user': user,
                                   'reason': reason},
                             headers=auth_headers(), timeout=20)
    _handle_http_error(response)


def approve(config, username):
    service_url = emergency_service_url(config)
    response = requests.post('{}/access-requests/{}'.format(service_url, urllib.parse.quote_plus(username)),
                             headers=auth_headers(), timeout=20)
    _handle_http_error(response)
    return response.json()["reason"]


def _handle_http_error(response):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        # Try to see if we can extract a nice error message
        error_obj = response.json()
        title = error_obj.get("title")
        detail = error_obj.get("detail")
        message = "\n".join(filter(None, [title, detail]))
        raise Exception("[{code}] {message}".format(code=response.status_code, message=message))


def get_all(config):
    """Get all current access requests from the Emergency Access Service"""
    response = requests.get('{}/access-requests'.format(emergency_service_url(config)),
                            headers=auth_headers(), timeout=20)
    _handle_http_error(response)
    access_requests = response.json()
    return combine_request_approved(access_requests['items'])


def combine_request_approved(access_requests):
    """Combine pending and approved requests for the same user.

       Emergency Access Service returns both requests and approved access.
       If a request is already approved we don't want to show the request, so
       we merge the requests by user."""
    # TODO: move to server side.
    current_access = {}
    for request in access_requests:
        req = current_access.get(request['user'], request)
        if not req.get('approved', False):
            req['approved'] = request.get('approved', False)
            req['expiry_time'] = request['expiry_time']

        if req.get('reason', "") == "":
            req['reason'] = request['reason']

        current_access[request['user']] = req
    return current_access
