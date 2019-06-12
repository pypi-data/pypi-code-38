from inmation_api_client.options import Options
from inmation_api_client.inclient import Client

OPTIONS = Options({
    'auth': {
        'username': 'username',
        'password': 'password'
    }
})
OPTIONS.tim = 10
ITEMS_PATH = '/System/Core/PythonApiTests/'

ITEM1 = ITEMS_PATH + 'Item01'  # Holder Item
ITEM2 = ITEMS_PATH + 'Item02'  # Holder Item
ITEM3 = ITEMS_PATH + 'Item03'  # Holder Item
ITEM4 = ITEMS_PATH + 'Item04'  # Generic Item
ITEM5 = ITEMS_PATH + 'Item05'  # Generic Item


def create_api_client(ioloop=None):
    client = Client(ioloop)
    client.Connect(options=OPTIONS)
    # client.EnableDebug()

    def connection_changed(conn_info):
        print('Connection state: {}, {}, authenticated: {}'.format(
            conn_info.state, conn_info.state_string, conn_info.authenticated))

    client.OnConnectionChanged(connection_changed)

    def on_error(err):
        if err:
            print("Error: {}".format(err))

    client.OnError(on_error)

    return client


def print_info(func):
    def wrapper(*args, **kwargs):
        print('\n*** START {}\n'.format(func.__name__))
        func(*args, **kwargs)
        print('\n*** END {}\n'.format(func.__name__))
    return wrapper
