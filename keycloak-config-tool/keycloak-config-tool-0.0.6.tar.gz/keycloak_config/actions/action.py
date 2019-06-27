"""
Action superclass.
~~~~~~~~~~~~~~~~~~
"""

import requests
import urllib


class InvalidActionConfigurationException(Exception):
    pass


class ActionExecutionException(Exception):
    pass


class Action(object):

    def __init__(self, name, *args, **kwargs):
        self.name = name

    @staticmethod
    def get_client_by_client_id(realm_name, client_id, keycloak_client):
        client_id_query_path = '/admin/realms/{0}/clients'.format(urllib.parse.quote(realm_name))
        client_id_query_params = {'client_id': client_id}
        query_response = keycloak_client.get(client_id_query_path, client_id_query_params)

        if query_response.status_code == requests.codes.ok:
            for client_data in query_response.json():
                if client_data['clientId'] == client_id:
                    return client_data
        else:
            raise ActionExecutionException('Unexpected response from client lookup request ({0})'.format(query_response.status_code))

        return None
