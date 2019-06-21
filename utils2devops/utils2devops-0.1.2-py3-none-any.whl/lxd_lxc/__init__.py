from pylxd import Client

__version__ = '0.1.0'


class BaseLXD:
    """ missing feature for command line """
    def __init__(self, verbose: int = 0, endpoint: str = None,
                 cert: tuple = None):
        """
        :param verbose: int 0=none, 1=Little, 2=more, 3=full
        :param endpoint: str like "https://192.83.9.23:8367"
        :param cert: tuple of (cert, key) like
                    ('/path/to/client.crt', '/path/to/client.key')
        """
        self.VERBOSE = verbose
        self.client = Client(endpoint=endpoint, cert=cert)
