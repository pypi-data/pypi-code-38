from graphenebase.types import (
    Uint8, Int16, Uint16, Uint32, Uint64,
    Varint32, Int64, String, Bytes, Void,
    Array, PointInTime, Signature, Bool,
    Set, Fixed_array, Optional, Static_variant,
    Map, Id, VoteId,
    ObjectId as GPHObjectId
)
from .cybex_types import (
    Ripemd160
)

from collections import OrderedDict
from graphenebase.objects import GrapheneObject, isArgsThisClass
from bitsharesbase.account import PublicKey
from bitsharesbase.objects import (
    ObjectId,
    Price,
    Asset
)

class TransferExtensions(Set):
    def __init__(self, *args, **kwargs):
        # Extensions #############################
        class Vesting_ext(GrapheneObject):
            def __init__(self, kwargs): 
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(OrderedDict([
                        ('vesting_period', Uint64(kwargs['vesting_period'])),
                        ('public_key', PublicKey(kwargs['public_key'], prefix = 'CYB'))
                    ]))

        class Xfer_to_name_ext(GrapheneObject):
            def __init__(self, kwargs):
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(OrderedDict([
                        ('name', String(kwargs['name'])),
                        ('asset_sym', String(kwargs['asset_sym'])),
                        ('fee_asset_sym', String(kwargs['fee_asset_sym'])),
                        ('hw_cookie1', Uint8(kwargs['hw_cookie1'])),
                        ('hw_cookie2', Uint8(kwargs['hw_cookie2']))
                    ]))
        # End of Extensions definition ###########

        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

        a = []

        sorting = sorted(kwargs, key=lambda x: x[0])
        for ext in sorting:
            if ext[0] == 1:
                a.append(Static_variant(
                    Vesting_ext(ext[1]),
                    ext[0])
                )
            elif ext[0] == 4:
                a.append(Static_variant(
                    Xfer_to_name_ext(ext[1]),
                    ext[0])
                )
            else:
                raise NotImplementedError("Extension {} is unknown".format(ext[0]))

        super().__init__(a)

class AssetIssueExtensions(Set):
    def __init__(self, *args, **kwargs):
        # Extensions #############################
        class Vesting_ext(GrapheneObject):
            def __init__(self, kwargs): 
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(OrderedDict([
                        ('vesting_period', Uint64(kwargs['vesting_period'])),
                        ('public_key', PublicKey(kwargs['public_key'], prefix = 'CYB'))
                    ]))
        # End of Extensions definition ###########

        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

        a = []

        sorting = sorted(kwargs, key=lambda x: x[0])
        for ext in sorting:
            if ext[0] == 1:
                a.append(Static_variant(
                    Vesting_ext(ext[1]),
                    ext[0])
                )
            else:
                raise NotImplementedError("Extension {} is unknown".format(ext[0]))

        super().__init__(a)

class LimitOrderCreateExtensions(Set):
    def __init__(self, *args, **kwargs):
        # Extensions ############################
        class Order_side_ext(GrapheneObject):
            def __init__(self, kwargs):
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(OrderedDict([
                        ('is_buy', Bool(kwargs['is_buy']))
                    ]))
        # End of Extensions definition ##########
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

        if len(kwargs) == 0:           
            return super().__init__([])

        a = []
        ext = kwargs[0]
        assert ext[0] == 7
        a.append(Static_variant(
            Order_side_ext(ext[1]),
            ext[0]
        ))
        super().__init__(a)

class LimitOrderCancelExtensions(Set):
    def __init__(self, *args, **kwargs):
        # Extensions ############################
        class Cancel_trx_id_ext(GrapheneObject):
            def __init__(self, kwargs):
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(OrderedDict([
                        ('trx_id', Ripemd160(kwargs['trx_id']))
                    ]))
        # End of Extensions definition ##########
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

        if len(kwargs) == 0:           
            return super().__init__([])

        a = []
        ext = kwargs[0]
        assert ext[0] == 6
        a.append(Static_variant(
            Cancel_trx_id_ext(ext[1]),
            ext[0]
        ))
        super().__init__(a)

class AssertPredications(Array):
    def __init__(self, *args, **kwargs):
        class Account_name_eq_lit_predicate(GrapheneObject):
            def __init__(self, kwargs):
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(OrderedDict([
                        ('account_id', ObjectId(kwargs['account_id'], 'account')),
                        ('name', String(kwargs['name']))
                    ]))

        class Asset_symbol_eq_lit_predicate(GrapheneObject):
            def __init__(self, kwargs):
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(OrderedDict([
                        ('asset_id', ObjectId(kwargs['asset_id'], 'asset')),
                        ('symbol', String(kwargs['symbol']))
                    ]))

        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
        a = []

        sorting = sorted(kwargs, key = lambda x: x[0])
        for ext in sorting:
            if ext[0] == 0:
                a.append(Static_variant(
                    Account_name_eq_lit_predicate(ext[1]),
                    ext[0]
                ))
            elif ext[0] == 1:
                a.append(Static_variant(
                    Asset_symbol_eq_lit_predicate(ext[1]),
                    ext[0]
                ))
            else:
                raise NotImplementedError("Extension {} is unknown".format(ext[0]))

        super().__init__(a)

class ExchangeOptionExtensions(Set):
    def __init__(self, *args, **kwargs):
        # Extensions #############################
        class Check_once_amount(GrapheneObject):
            def __init__(self, kwargs): 
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(OrderedDict([
                        ('asset_id', ObjectId(kwargs['asset_id'], "asset")),
                        ('min', Int64(kwargs['min'])),
                        ('max', Int64(kwargs['max']))
                    ]))

        class Check_divisible(GrapheneObject):
            def __init__(self, kwargs): 
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(OrderedDict([
                        ('divisor', Asset(kwargs['divisor']))
                    ]))

        class Check_exchange_amount(GrapheneObject):
            def __init__(self, kwargs): 
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(OrderedDict([
                        ('asset_id', ObjectId(kwargs['asset_id'], "asset")),
                        ('floor', Int64(kwargs['floor'])),
                        ('ceil', Int64(kwargs['ceil']))
                    ]))

        class Vesting_policy_initializer(GrapheneObject):
            # Vesting policy initializer definitions ###############
            # End of Vesting policy initializer definitions ########
                
            def __init__(self, kwargs): 
                class Vesting_policy(Static_variant):
                    def __init__(self, kwargs): 
                        class Linear_vesting_policy_initializer(GrapheneObject):
                            def __init__(self, kwargs): 
                                if isArgsThisClass(self, args):
                                    self.data = args[0].data
                                else:
                                    if len(args) == 1 and len(kwargs) == 0:
                                        kwargs = args[0]
                                    super().__init__(OrderedDict([
                                        ('begin_timestamp', PointInTime(kwargs['begin_timestamp'])),
                                        ('vesting_cliff_seconds', Uint32(kwargs['vesting_cliff_seconds'])),
                                        ('vesting_duration_seconds', Uint32(kwargs['vesting_duration_seconds']))
                                    ]))
                        class Cdd_vesting_policy_initializer(GrapheneObject):
                            def __init__(self, kwargs): 
                                if isArgsThisClass(self, args):
                                    self.data = args[0].data
                                else:
                                    if len(args) == 1 and len(kwargs) == 0:
                                        kwargs = args[0]
                                    super().__init__(OrderedDict([
                                        ('start_claim', PointInTime(kwargs['start_claim'])),
                                        ('vesting_seconds', Uint32(kwargs['vesting_seconds']))
                                    ]))
                        if isArgsThisClass(self, args):
                            self.data = args[0].data
                        else:
                            if len(args) == 1 and len(kwargs) == 0:
                                kwargs = args[0]
                            if kwargs[0] == 0:
                                super().__init__(Linear_vesting_policy_initializer(kwargs[1]), 0)
                            elif kwargs[0] == 1:
                                super().__init__(Cdd_vesting_policy_initializer(kwargs[1]), 1)
                            else:
                                raise NotImplementedError("Vesting policy {} is unknown".format(ext[0]))
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(OrderedDict([("policy", Vesting_policy(kwargs["policy"]))]))

        # End of Extensions definition ###########

        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

        a = []

        sorting = sorted(kwargs, key=lambda x: x[0])
        for ext in sorting:
            if ext[0] == 0:
                a.append(Static_variant(Check_exchange_amount(ext[1]), 0))
            elif ext[0] == 1:
                a.append(Static_variant(Check_once_amount(ext[1]), 1))
            elif ext[0] == 2:
                a.append(Static_variant(Check_divisible(ext[1]), 2))
            elif ext[0] == 3:
                a.append(Static_variant(Vesting_policy_initializer(ext[1]), 3))
            else:
                raise NotImplementedError("Extension {} is unknown".format(ext[0]))

        super().__init__(a)

class ExchangeOptions(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('rate', Price(kwargs["rate"])),
                ('owner_permissions', Uint32(kwargs["owner_permissions"])),
                ('flags', Uint32(kwargs["flags"])),
                ('whitelist_authorities',
                    Array([ObjectId(x, "account") for x in kwargs["whitelist_authorities"]])),
                ('blacklist_authorities',
                    Array([ObjectId(x, "account") for x in kwargs["blacklist_authorities"]])),
                ('extensions', ExchangeOptionExtensions(kwargs['extensions'])),
                ('description', String(kwargs["description"]))
            ]))
    
