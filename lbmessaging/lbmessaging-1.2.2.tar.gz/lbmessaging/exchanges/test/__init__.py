from lbmessaging.exchanges.Common import get_connection


def get_test_connection():
    return get_connection(vhost='/lhcb-test')
