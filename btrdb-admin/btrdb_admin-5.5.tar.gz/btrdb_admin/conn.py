# btrdb_admin.conn
# Module providing connection objects for BTrDB
#
# Author:   Allen Leis <allen@pingthings.io>
# Created:  Wed Mar 27 18:03:19 2019 -0400
#
# For license information, see LICENSE.txt
# ID: conn.py [] allen@pingthings.io $


"""
Module providing connection objects for BTrDB
"""

##########################################################################
## Imports
##########################################################################

import os
import base64
import grpc

from btrdb_admin.acl import ACLMixin
from btrdb_admin.grpcinterface import admin_pb2_grpc


##########################################################################
## Helpers
##########################################################################

def _create_auth_callback(username, password):
    auth_base = f"{username}:{password}".encode("utf-8")
    auth_encoded = base64.b64encode(auth_base).decode("ascii")
    auth_header = f"basic {auth_encoded}"
    return lambda ctx, callback: callback([('authorization', auth_header)], None)

def _root_certs():
    # grpc bundles its own CA certs which will work for all normal SSL
    # certificates but will fail for custom CA certs. Allow the user
    # to specify a CA bundle via env var to overcome this
    ca_bundle = os.getenv("BTRDB_CA_BUNDLE","")
    if ca_bundle != "":
        with open(ca_bundle, "rb") as f:
            return f.read()
    return None


##########################################################################
## Classes
##########################################################################

class Connection(ACLMixin):
    "Represents a connection to the BTrDB server"

    def __init__(self, endpoint, username, password):
        """
        Connects to the admin API of a BTrDB server

        Parameters
        ----------
        endpoint: str
            The address:port of the cluster to connect to, e.g 123.123.123:4411
        username: str
            Username of account with admin capability
        password: str
            Password of account with admin capability

        Returns
        -------
        Connection
            A Connection class object.

        """
        if len(endpoint.split(":")) != 2:
            raise ValueError("expecting address:port")

        certs = _root_certs()
        callback = _create_auth_callback(username, password)

        self._channel = grpc.secure_channel(
            endpoint,
            grpc.composite_channel_credentials(
                grpc.ssl_channel_credentials(certs),
                grpc.metadata_call_credentials(callback)
            )
        )

        self.client = admin_pb2_grpc.AdminAPIStub(self._channel)
