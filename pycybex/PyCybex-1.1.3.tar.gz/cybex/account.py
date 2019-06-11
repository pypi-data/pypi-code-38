from bitshares.account import Account as BitsharesAccount
from bitshares.proposal import Proposal
from .address import all_addresses
from .balance import Balance

class Account(BitsharesAccount):
    def __init__(
        self,
        account,
        full=False,
        lazy=False,
        cybex_instance=None
    ):
        super(Account, self).__init__(account = account, full = full,
            lazy = lazy, bitshares_instance = cybex_instance)

    @property
    def vesting_balances(self):
        """ List of vesting balances
        """
        pubkeys = [x[0] for x in self['active']['key_auths']]
        pubkeys.extend([x[0] for x in self['owner']['key_auths']])
        all_addr = []
        for k in pubkeys:
            all_addr.extend(all_addresses(k))
        return [Balance(b) 
                for b in self.bitshares.rpc.get_balance_objects(all_addr)
               ]

    @property
    def proposals(self):
        """ List of account related proposals
        """
        proposals = self.bitshares.rpc.get_proposed_transactions(self["id"])

        return [Proposal(x, bitshares_instance=self.bitshares)
                for x in proposals]
