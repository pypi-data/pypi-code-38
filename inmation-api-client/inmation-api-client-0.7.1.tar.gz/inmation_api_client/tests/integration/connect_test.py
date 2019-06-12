import asyncio
import time

from inmation_api_client.inclient import Client
from .environment import OPTIONS, print_info

client = Client()


def connection_changed(conn_info):
    """ closure """
    print('Connection state: {}, {}, authenticated: {}'.format(
        conn_info.state, conn_info.state_string, conn_info.authenticated))

client.OnConnectionChanged(connection_changed)


def on_error(err):
    if err:
        print("Error {}".format(err.message))

client.OnError(on_error)


@print_info
def connect_test():
    num_conn = 3
    for i in range(num_conn):
        print("\n({}) Connect.".format(i + 1))
        client.Connect(options=OPTIONS)
        print('({}) Disconnect.'.format(i + 1))
        client.Disconnect()

        time.sleep(1)
