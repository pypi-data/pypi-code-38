from bitshares.blockchainobject import BlockchainObject
from bitshares.amount import Amount
from bitshares.price import Price
from .exceptions import *
from .account import Account
from .asset import Asset
from . import cybex_operations

class Exchange(BlockchainObject):

    permission_flags = {
        "allow_quote_to_base": 0x01,
        "allow_base_to_quote": 0x02,
        "allow_deposit_base": 0x04,
        "allow_withdraw_base": 0x08,
        "allow_deposit_quote": 0x10,
        "allow_withdraw_quote": 0x20,
        "allow_charge_market_fee": 0x40,
        "allow_modify_rate": 0x80,
        "allow_only_whitelist": 0x100
    }

    def __init__(
        self,
        exchange_id,
        full = False,
        lazy = False,
        cybex_instance = None
    ):
        super().__init__(
            exchange_id,
            lazy = lazy,
            full = full,
            bitshares_instance = cybex_instance
        ) 

    def refresh(self):
        exchange = None
        import re
        if re.match("^1\.20\.[0-9]*$", self.identifier):
            exchange = self.bitshares.rpc.get_objects([self.identifier])[0]
        else:
            exchange = self.bitshares.rpc.list_exchange_objects_by_name(self.identifier, 1)[0]

        if not exchange or exchange['name'] != self.identifier:
            raise ExchangeDoesNotExistsException(self.identifier)

        super().__init__(exchange)

    def display(self):
        name = self['name']
        owner = Account(self['owner'], cybex_instance = self.bitshares)['name']
        rate = Price(self['options']['rate'])
        def translate_permissions(perm):
            _perm = { val:perm for perm, val in self.permission_flags.items() }
            flag = 1
            while flag <= max(_perm.keys()):
                perm_name = _perm[flag]
                yield '{}:\t{}'.format(perm_name, 'Y' if perm & flag else 'N')
                flag <<= 1

        print("=======================")
        print("Display for exchange {}".format(self.identifier))
        print("Name: {}".format(name))
        print("Owner: {}".format(owner))
        print("Price: {}".format(rate))
        print("Owner Permissions:")
        for l in translate_permissions(self['options']['owner_permissions']):
            print(" " + l )
        print("Flags:")
        for l in translate_permissions(self['options']['flags']):
            print(" " + l )
        print("Whitelist:")
        for a in self['options']['whitelist_authorities']:
            print(" " + Account(a, cybex_instance = self.bitshares)['name'])
        print("Blacklist:")
        for a in self['options']['blacklist_authorities']:
            print(" " + Account(a, cybex_instance = self.bitshares)['name'])
        print("Extensions:")
        for ext in self['options']['extensions']:
            if ext[0] == 0:
                print(" Check amount: {}-{}".format(
                    Amount({'asset_id': ext[1]['asset_id'], 'amount': ext[1]['floor']}),
                    Amount({'asset_id': ext[1]['asset_id'], 'amount': ext[1]['ceil']})
                ))
            if ext[0] == 1:
                print(" Check once amount: {}-{}".format(
                    Amount({'asset_id': ext[1]['asset_id'], 'amount': ext[1]['min']}),
                    Amount({'asset_id': ext[1]['asset_id'], 'amount': ext[1]['max']})
                ))
            if ext[0] == 2:
                print(" Check divisible: {}".format(
                    Amount(ext[1]['divisor'])
                ))
            if ext[0] == 3:
                print(" Vesting policy: {}".format(json.dumps(ext['policy'])))
        print("Pool balances:")
        print(" Base: {}".format(self.base_amount))
        print(" Quote: {}".format(self.quote_amount))
        print("=======================")

    def __disable_flag(self, flag, flag_name):
        return flag & ~self.permission_flags[flag_name]

    def __enable_flag(self, flag, flag_name):
        return flag | self.permission_flags[flag_name]

    def _disable_flag(self, flag_name, **kwargs):
        options = self['options']
        options['flags'] = self.__disable_flag(options['flags'], flag_name) 
        
        op = cybex_operations.Update_exchange(**{
            "fee": {"amount":0, "asset_id": "1.3.0"},
            "owner": self["owner"],
            "exchange_to_update": self["id"],
            "new_owner": None,
            "new_options": options
        })
        self.bitshares.finalizeOp(op, self['owner'], "active", **kwargs)

    def _enable_flag(self, flag_name, **kwargs):
        options = self['options']
        options['flags'] = self.__enable_flag(options['flags'], flag_name)
        
        op = cybex_operations.Update_exchange(**{
            "fee": {"amount":0, "asset_id": "1.3.0"},
            "owner": self["owner"],
            "exchange_to_update": self["id"],
            "new_owner": None,
            "new_options": options
        })
        self.bitshares.finalizeOp(op, self['owner'], "active", **kwargs)
    
    def disable_quote(self, **kwargs):
        self._disable_flag("allow_quote_to_base", **kwargs)

    def disable_base(self, **kwargs):
        self._disable_flag("allow_base_to_quote", **kwargs)
    
    def enable_quote(self, **kwargs):
        self._enable_flag("allow_quote_to_base", **kwargs)

    def enable_base(self, **kwargs):
        self._enable_flag("allow_base_to_quote", **kwargs)

    def change_rate(self, rate, **kwargs):
        """ update change ratio of exchange object
            :param dict rate: {'base': {'symbol': 'JADE.ETH', 'amount': 1}, 'quote': {'symbol': 'JADE.USDT', 'amount': 200}}
        """
        options = self['options']
        base_asset = Asset(rate['base']['symbol'], cybex_instance = self.bitshares)
        quote_asset = Asset(rate['quote']['symbol'], cybex_instance = self.bitshares)

        if (base_asset['id'] != options['rate']['base']['asset_id'] or
            quote_asset['id'] != options['rate']['quote']['asset_id']):
            raise ExchangeOptionInvalieException("can not change exchange rate asset")

        rate = {'base': {'asset_id': base_asset['id'], 'amount': rate['base']['amount'] * 10 ** base_asset.precision},
                'quote': {'asset_id': quote_asset['id'], 'amount': rate['quote']['amount'] * 10 ** quote_asset.precision}}
        options['rate'] = rate
        op = cybex_operations.Update_exchange(**{
            "fee": {"amount":0, "asset_id": "1.3.0"},
            "owner": self["owner"],
            "exchange_to_update": self["id"],
            "new_owner": None,
            "new_options": options
        })
        self.bitshares.finalizeOp(op, self['owner'], "active", **kwargs)

    def whitelist(self, account, **kwargs):
        """ set some accounts to exchange white list
            Notice: origin whitelist account will be removed 
        """
        if isinstance(account, str):
            account = [account]

        assert isinstance(account, list)

        options = self['options']
        options['whitelist_authorities'] = [
            Account(acc, cybex_instance = self.bitshares)['id']
            for acc in account]

        op = cybex_operations.Update_exchange(**{
            "fee": {"amount":0, "asset_id": "1.3.0"},
            "owner": self["owner"],
            "exchange_to_update": self["id"],
            "new_owner": None,
            "new_options": options
        })
        self.bitshares.finalizeOp(op, self['owner'], "active", **kwargs)

    def blacklist(self, account, **kwargs):
        """ set some accounts to exchange black list
            Notice: origin whitelist account will be removed 
        """
        if isinstance(account, str):
            account = [account]

        assert isinstance(account, list)

        options = self['options']
        options['blacklist_authorities'] = [
            Account(acc, cybex_instance = self.bitshares)['id']
            for acc in account]

        op = cybex_operations.Update_exchange(**{
            "fee": {"amount":0, "asset_id": "1.3.0"},
            "owner": self["owner"],
            "exchange_to_update": self["id"],
            "new_owner": None,
            "new_options": options
        })
        self.bitshares.finalizeOp(op, self['owner'], "active", **kwargs)

    def deliver_owner(self, new_owner, **kwargs):
        """ deliver owner of exchange to a new one
        """
        new_account = Account(new_owner, cybex_instance = self.bitshares)
        op = cybex_operations.Update_exchange(**{
            "fee": {"amount":0, "asset_id": "1.3.0"},
            "owner": self["owner"],
            "exchange_to_update": self["id"],
            "new_owner": new_account['id'],
        })
        self.bitshares.finalizeOp(op, self['owner'], "active", **kwargs)

    @property
    def base_amount(self):
        pool = self.bitshares.rpc.get_objects([self['dynamic_exchange_data_id']])[0]
        return Amount(
                {"asset_id": self['options']['rate']['base']['asset_id'],
                 "amount": pool['base_balance']
                }, bitshares_instance = self.bitshares)

    @property
    def quote_amount(self):
        pool = self.bitshares.rpc.get_objects([self['dynamic_exchange_data_id']])[0]
        return Amount(
                {"asset_id": self['options']['rate']['quote']['asset_id'],
                 "amount": pool['quote_balance']
                }, bitshares_instance = self.bitshares)
