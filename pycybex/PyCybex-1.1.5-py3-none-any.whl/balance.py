from bitshares.blockchainobject import BlockchainObject
from bitshares.asset import Asset
from bitshares.amount import Amount
from bitshares.account import Account

class Balance(BlockchainObject):
    def __init__(
        self,
        *args,
        lazy = None,
        full = None,
        cybex_instance = None
    ):
        self.bitshares = cybex_instance
        if not (len(args) == 1 and isinstance(args[0], dict)):
            raise ValueError('Balance can only be inited individually using dict')

        super().__init__(args[0], bitishares_instance = self.bitshares)
        self['asset'] = Asset(self["balance"]["asset_id"], bitshares_instance=self.bitshares)
        self['symbol'] = self['asset']['symbol']
        self['balance'] = Amount(self['balance'], bitshares_instance = self.bitshares)
        # uncomment this after new bitshares-core comes up
        #self['sender'] = Account(args[0]['sender'], bitishares_instance = self.bitshares)

    @property
    def is_vesting(self):
        return True if 'vesting_policy' in self and self['vesting_policy'] else False
