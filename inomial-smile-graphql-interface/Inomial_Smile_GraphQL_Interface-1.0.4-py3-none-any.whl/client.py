from smileql import transport
from smileql.introspection import Builder
import logging
from smileql.payments import Payments
from smileql.accounts import Accounts


class Client:
    """
    Interfaces with the inomial smile graphql interface and using introspection dynamically
    builds the relevant objects that can be passed to perform queries and mutations
    """

    def __init__(self, host, username, password, debug=False):
        self._api = transport.Transport(host, auth=(username, password), debug=debug)
        self._logging(debug)
        # Builder(self, self._api)
        self.payments = Payments(self._api)
        self.accounts = Accounts(self._api)

    def _logging(self, debug_flag):
        if debug_flag:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
