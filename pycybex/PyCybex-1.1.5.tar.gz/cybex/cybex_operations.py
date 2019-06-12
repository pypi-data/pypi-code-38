from collections import OrderedDict
import json
from binascii import hexlify
from graphenebase.types import (
    Uint8, Int16, Uint16, Uint32, Uint64,
    Varint32, Int64, String, Bytes, Void,
    Array, PointInTime, Signature, Bool,
    Set, Fixed_array, Optional, Static_variant,
    Map, Id, VoteId
)
from graphenebase.objects import GrapheneObject, isArgsThisClass
from bitsharesbase.account import PublicKey
from bitsharesbase.objects import (
    Operation,
    Asset,
    Memo,
    Price,
    PriceFeed,
    Permission,
    AccountOptions,
    BitAssetOptions,
    AssetOptions,
    ObjectId,
    Worker_initializer,
    SpecialAuthority,
    AccountCreateExtensions
)

from .cybex_objects import (
    TransferExtensions,
    AssetIssueExtensions,
    LimitOrderCreateExtensions,
    LimitOrderCancelExtensions,
    AssertPredications,
    ExchangeOptions
)

default_prefix = 'CYB'


class Transfer(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.get("prefix", default_prefix)
            if "memo" in kwargs and kwargs["memo"]:
                if isinstance(kwargs["memo"], dict):
                    kwargs["memo"]["prefix"] = prefix
                    memo = Optional(Memo(**kwargs["memo"]))
                else:
                    memo = Optional(Memo(kwargs["memo"]))
            else:
                memo = Optional(None)

            if 'extensions' not in kwargs or not kwargs['extensions']:
                kwargs['extensions'] = []
            elif not isinstance(kwargs['extensions'], list):
                raise TypeError(
                    'You need to provide a list as extension param')

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('from', ObjectId(kwargs["from"], "account")),
                ('to', ObjectId(kwargs["to"], "account")),
                ('amount', Asset(kwargs["amount"])),
                ('memo', memo),
                ('extensions', TransferExtensions(kwargs['extensions'])),
            ]))

class Override_transfer(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.get("prefix", default_prefix)
            if "memo" in kwargs and kwargs["memo"]:
                if isinstance(kwargs["memo"], dict):
                    kwargs["memo"]["prefix"] = prefix
                    memo = Optional(Memo(**kwargs["memo"]))
                else:
                    memo = Optional(Memo(kwargs["memo"]))
            else:
                memo = Optional(None)

            kwargs['extensions'] = []

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('issuer', ObjectId(kwargs["issuer"], "account")),
                ('from', ObjectId(kwargs["from"], "account")),
                ('to', ObjectId(kwargs["to"], "account")),
                ('amount', Asset(kwargs["amount"])),
                ('memo', memo),
                ('extensions', Set([])),
            ]))


class Asset_issue(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.get('prefix', default_prefix)
            if 'memo' in kwargs and kwargs['memo']:
                kwargs['memo']['prefix'] = prefix
                memo = Optional(Memo(**kwargs['memo']))
            else:
                memo = Optional(None)

            if 'extensions' not in kwargs or not kwargs['extensions']:
                kwargs['extensions'] = []
            elif not isinstance(kwargs['extensions'], list):
                raise TypeError(
                    'You need to provide a list as extension param')

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('issuer', ObjectId(kwargs["issuer"], "account")),
                ('asset_to_issue', Asset(kwargs["asset_to_issue"])),
                ('issue_to_account', ObjectId(
                    kwargs["issue_to_account"], "account")),
                ('memo', memo),
                ('extensions', AssetIssueExtensions(kwargs['extensions'])),
            ]))


class Cancel_vesting(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('sender', ObjectId(kwargs["sender"], "account")),
                ('balance_object', ObjectId(kwargs["balance_object"])),
            ]))


class Balance_claim(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('deposit_to_account', ObjectId(
                    kwargs["deposit_to_account"], "account")),
                ('balance_to_claim', ObjectId(
                    kwargs["balance_to_claim"], "balance")),
                ('balance_owner_key', PublicKey(
                    kwargs['balance_owner_key'], prefix='CYB')),
                ('total_claimed', Asset(kwargs["total_claimed"]))
            ]))


class Custom(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('payer', ObjectId(kwargs["payer"], "account")),
                ('required_auths', Array(
                    [ObjectId(x, "account") for x in kwargs["required_auths"]])),
                ('id', Uint16(kwargs["id"])),
                ('data', Bytes(kwargs["data"]))
            ]))


class Account_whitelist(GrapheneObject):
    no_listing = 0              # < No opinion is specified about this account
    white_listed = 1            # < This account is whitelisted, but not blacklisted
    black_listed = 2            # < This account is blacklisted, but not whitelisted
    white_and_black_listed = 3  # < This account is both whitelisted and blacklisted

    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('authorizing_account', ObjectId(
                    kwargs["authorizing_account"], "account")),
                ('account_to_list', ObjectId(
                    kwargs["account_to_list"], "account")),
                ('new_listing', Uint8(kwargs["new_listing"])),
                ('extensions', Set([])),
            ]))

class Limit_order_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            if 'extensions' not in kwargs or not kwargs['extensions']:
                kwargs['extensions'] = []
            elif not isinstance(kwargs['extensions'], list):
                raise TypeError(
                    'You need to provide a list as extension param')

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('seller', ObjectId(kwargs["seller"], "account")),
                ('amount_to_sell', Asset(kwargs["amount_to_sell"])),
                ('min_to_receive', Asset(kwargs["min_to_receive"])),
                ('expiration', PointInTime(kwargs["expiration"])),
                ('fill_or_kill', Bool(kwargs["fill_or_kill"])),
                ('extensions', LimitOrderCreateExtensions(kwargs['extensions']))
            ]))


class Limit_order_cancel(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            if 'extensions' not in kwargs or not kwargs['extensions']:
                kwargs['extensions'] = []
            elif not isinstance(kwargs['extensions'], list):
                raise TypeError(
                    'You need to provide a list as extension param')

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('fee_paying_account', ObjectId(
                    kwargs["fee_paying_account"], "account")),
                ('order', ObjectId(kwargs["order"], "limit_order")),
                ('extensions', LimitOrderCancelExtensions(
                    kwargs['extensions'])),
            ]))


class Cancel_all(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('seller', ObjectId(kwargs["seller"], "account")),
                ('sell_asset_id', ObjectId(kwargs["sell_asset_id"], "asset")),
                ('receive_asset_id', ObjectId(
                    kwargs["receive_asset_id"], "asset")),
                ('extensions', Set([]))
            ]))


class Proposal_delete(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('fee_paying_account', ObjectId(
                    kwargs["fee_paying_account"], "account")),
                ('using_owner_authority', Bool(
                    kwargs['using_owner_authority'])),
                ('proposal', ObjectId(kwargs["proposal"], "proposal")),
                ('extensions', Set([]))
            ]))


class Initiate_dice_bet(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('owner', ObjectId(kwargs["owner"], "account")),
                ('asset_to_bet', ObjectId(kwargs["asset_to_bet"], "asset")),
                ('initial_balance', Int64(kwargs["initial_balance"])),
                ('clearing_threshold', Int64(kwargs["clearing_threshold"])),
                ('min_amount', Int64(kwargs["min_amount"])),
                ('max_amount', Int64(kwargs["max_amount"])),
                ('pay_discount_percent', Uint16(
                    kwargs['pay_discount_percent'])),
                ('max_dice', Uint16(kwargs['max_dice'])),
                ('extensions', Set([]))
            ]))


class Deposit_dice_bet(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('owner', ObjectId(kwargs["owner"], "account")),
                ('dice_bet', ObjectId(kwargs["dice_bet"])),
                ('amount', Int64(kwargs["amount"])),
                ('extensions', Set([]))
            ]))


class Withdraw_dice_bet(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('owner', ObjectId(kwargs["owner"], "account")),
                ('dice_bet', ObjectId(kwargs["dice_bet"])),
                ('amount', Int64(kwargs["amount"])),
                ('extensions', Set([]))
            ]))


class Participate_dice_bet(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('dice_bet', ObjectId(kwargs["dice_bet"])),
                ('payer', ObjectId(kwargs["payer"], "account")),
                ('amount', Int64(kwargs["amount"])),
                ('choice', Uint16(kwargs["choice"])),
                ('extensions', Set([]))
            ]))


class Assert(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs['fee'])),
                ('fee_paying_account', ObjectId(
                    kwargs['fee_paying_account'], 'account')),
                ('predicates', AssertPredications(kwargs['predicates'])),
                ('required_auths', Set([
                    ObjectId(x, 'account') for x in kwargs['required_auths']])),
                ('extensions', Set([]))
            ]))


class Create_exchange(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs['fee'])),
                ('name', String(kwargs['name'])),
                ('owner', ObjectId(kwargs['owner'], 'account')),
                ('options', ExchangeOptions(kwargs['options'])),
                ('extensions', Set([]))
            ]))


class Update_exchange(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            if "new_owner" in kwargs and kwargs['new_owner']:
                new_owner = Optional(ObjectId(kwargs["new_owner"], 'account'))
            else:
                new_owner = Optional(None)

            if "new_options" in kwargs and kwargs['new_options']:
                new_options = Optional(ExchangeOptions(kwargs['new_options']))
            else:
                new_options = Optional(None)

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs['fee'])),
                ('owner', ObjectId(kwargs['owner'], 'account')),
                ('exchange_to_update', ObjectId(kwargs['exchange_to_update'])),
                ('new_owner', new_owner),
                ('new_options', new_options),
                ('extensions', Set([]))
            ]))


class Deposit_exchange(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs['fee'])),
                ('owner', ObjectId(kwargs['owner'], 'account')),
                ('exchange_to_deposit', ObjectId(
                    kwargs['exchange_to_deposit'])),
                ('amount', Asset(kwargs['amount'])),
                ('extensions', Set([]))
            ]))


class Withdraw_exchange(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs['fee'])),
                ('owner', ObjectId(kwargs['owner'], 'account')),
                ('exchange_to_withdraw', ObjectId(
                    kwargs['exchange_to_withdraw'])),
                ('amount', Asset(kwargs['amount'])),
                ('extensions', Set([]))
            ]))


class Remove_exchange(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs['fee'])),
                ('owner', ObjectId(kwargs['owner'], 'account')),
                ('exchange_to_remove', ObjectId(kwargs['exchange_to_remove'])),
                ('extensions', Set([]))
            ]))


class Participate_exchange(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs['fee'])),
                ('payer', ObjectId(kwargs['payer'], 'account')),
                ('exchange_to_pay', ObjectId(kwargs['exchange_to_pay'])),
                ('amount', Asset(kwargs['amount'])),
                ('extensions', Set([]))
            ]))
