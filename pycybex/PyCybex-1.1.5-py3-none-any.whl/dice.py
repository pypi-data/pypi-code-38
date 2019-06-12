from bitshares.blockchainobject import BlockchainObject
from bitshares.amount import Amount
from .account import Account
from .asset import Asset
from .exceptions import DicebetDoesNotExistsException

class Dicebet(BlockchainObject):
    def __init__(
        self,
        dice_bet_id,
        full = False,
        lazy = False,
        cybex_instance = None
    ):
        # cache asset and owner
        self._asset = None
        self._owner = None

        super().__init__(
            dice_bet_id,
            lazy = lazy,
            full = full,
            bitshares_instance = cybex_instance
        ) 

    def refresh(self):
        dice_bet = None
        import re
        if re.match("^1\.18\.[0-9]*$", self.identifier):
            dice_bet = self.bitshares.rpc.get_objects([self.identifier])[0]
        if not dice_bet:
            raise DicebetDoesNotExistsException(self.identifier)

        if not self._asset:
            self._asset = Asset(dice_bet['asset_to_bet'], cybex_instance = self.bitshares)
        if not self._owner:
            self._owner = Account(dice_bet['owner'], cybex_instance= self.bitshares)
        super(Dicebet, self).__init__({
            'id': dice_bet['id'],
            'asset_to_bet': self._asset,
            'owner': self._owner,
            'pool_balance': int(dice_bet['pool_balance']) / 10 ** self._asset['precision'],
            'pay_discount_percent': dice_bet['pay_discount_percent'] / 10000,
            'clearing_threshold': int(dice_bet['clearing_threshold']) / 10 ** self._asset['precision'],
            'max_amount': int(dice_bet['max_amount']) / 10 ** self._asset['precision'],
            'min_amount': int(dice_bet['min_amount']) / 10 ** self._asset['precision'],
            'max_dice': dice_bet['max_dice'],
            'pending_balance': int(dice_bet['pending_balance']) / 10 ** self._asset['precision']
        })

    @property
    def owner(self):
        return self['owner']

    @property
    def pool_balance(self):
        self.refresh()
        return self['pool_balance']

    @property
    def asset_to_bet(self):
        return self['asset_to_bet']

    @property
    def pending_balance(self):
        self.refresh()
        return self['pending_balance']

    @property
    def max_dice(self):
        return self['max_dice']

    @property
    def max_amount(self):
        return self['max_amount']

    @property
    def min_amount(self):
        return self['min_amount']
