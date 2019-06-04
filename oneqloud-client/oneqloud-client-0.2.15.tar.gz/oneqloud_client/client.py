import grpc
import json
import time
import requests
from . import qbit_pb2_grpc
from future.utils import raise_from
import pkg_resources

from google.protobuf.json_format import MessageToDict


def create_get_auth(access_token):

    def get_auth_token(context, callback):
        callback([('authorization', access_token)], None)

    return get_auth_token

# Client class takes care of authentication process in order to use our services
#
# Example -
# from oneqloud_client import client
# qbit_client = client('./oneqloud_client/license.json')
# qbit_client.stub has all the grpc functions 1qbit has
class qloud_grpc_client(object):

    def __init__(self,
                 auth_url,
                 host,
                 root_certs=None,
                 client_id=None,
                 client_secret=None):
        if not root_certs:
            root_certs = pkg_resources.resource_string('oneqloud_client', 'ca.pem')

        channel_creds = grpc.ssl_channel_credentials(
            root_certificates=root_certs)

        # we still want user to create stub without authentication token
        if client_id and client_secret:
            req_dict = {
                "client_id": client_id,
                "client_secret": client_secret
            }

            try:
                response = requests.post(auth_url, json=req_dict)
                if response.ok:
                    response_data = response.json()
                    token = response_data["token"]
                else:
                    raise Exception(response.reason
                        + " ("
                        + str(response.status_code)
                        + ")")
            except Exception as e:
                raise_from(type(e)("Authentication Request Failed", e), e)

            auth_creds = grpc.metadata_call_credentials(create_get_auth(token))
            channel_creds = grpc.composite_channel_credentials(
                channel_creds, auth_creds)

        self.channel = grpc.secure_channel(host, channel_creds)
        self.stub = qbit_pb2_grpc.QbitStub(self.channel)

class insecure_qloud_grpc_client(object):

    def __init__(self, host):
        self.channel = grpc.insecure_channel(host)
        self.stub = qbit_pb2_grpc.QbitStub(self.channel)

def client(root_certs=None,
           auth_url="https://portal-api.1qbit.com/v1/get_project_token",
           host='grpc.1qb.it',
           client_id=None,
           client_secret=None,
           insecure=False):
    if insecure:
        return insecure_qloud_grpc_client(host).stub
    else:
        return qloud_grpc_client(auth_url, host, root_certs, client_id, client_secret).stub
