"""
    prs_lib

    lib for press.one Dapp developer.

    :copyright: © 2019 by the press.one team.
    :license: MIT, see LICENSE for more details.
"""

from .user import User
from .keystore import Keystore
from .config import PRSConfig
from .subscription import Subscription
from .finance import Finance
from .file import File
from .block import Block
from .draft import Draft
from .contract import Contract
from .order import Order
from .dapp import Dapp
from . import sign_utility
from . import request

__version__ = '0.0.2'
__all__ = [
    'PRS',
]


class Util:
    def __init__(self):
        self.hash_request = request.hash_request
        self.sign_request = request.sign_request
        self.get_auth_header = request.get_auth_header
        self.sign_by_token = sign_utility.sign_by_token
        self.hash_by_password = sign_utility.hash_by_password
        self.hash_by_filename = sign_utility.hash_by_filename
        self.hash_by_readable_stream = sign_utility.hash_by_readable_stream


class PRS:
    def __init__(self, options):
        """
        :param options: dict
            {
                'env': str,
                'debug': bool,
                'private_key': str,
                'token': str,
                'address': str
            }
        """
        self.config = PRSConfig(options)
        self.keystore = Keystore(self.config)
        self.user = User(self.config)
        self.subscription = Subscription(self.config)
        self.finance = Finance(self.config)
        self.file = File(self.config)
        self.block = Block(self.config)
        self.draft = Draft(self.config)
        self.contract = Contract(self.config)
        self.order = Order(self.config)
        self.dapp = Dapp(self.config)
        self.util = Util()
