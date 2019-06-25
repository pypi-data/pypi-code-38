# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

""" credentials.py, methods for interacting with the AzureML credential service."""

from __future__ import print_function

import requests


def set_credentials(project_context, key, value):
    address = project_context.get_history_service_uri()
    address += "/credential/v1.0" + project_context.get_workspace_uri_path() + "/secrets"

    headers = project_context.get_auth().get_authentication_header()

    body = {"Name": key, "Value": value}
    response = requests.put(address, json=body, headers=headers)
    response.raise_for_status()


def get_credentials(project_context, credential_name):

    import six.moves.urllib as urllib
    address = project_context.get_history_service_uri()
    encoded_credential = urllib.parse.quote_plus(credential_name)
    address += "/credential/v1.0" + project_context.get_workspace_uri_path() + "/secrets/" + encoded_credential

    headers = project_context.get_auth().get_authentication_header()
    response = requests.get(address, headers=headers)
    response.raise_for_status()
    return response.json()["value"]


def remove_credentials(project_context, key):
    # TODO Implement this once the service supports deletion.
    pass
