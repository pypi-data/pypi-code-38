from binascii import hexlify
import os, sys
from graphenebase.base58 import Base58
import bitsharesbase.operations as operations
import bitsharesbase.operationids as operationids
import graphenebase.ecdsa

cybex_ops = [
    "transfer", # replaced by cybex to support vesting transfer
    "limit_order_create",
    "limit_order_cancel", # replaced by cybex to support rte cancel
    "call_order_update",
    "fill_order",
    "account_create",
    "account_update",
    "account_whitelist",
    "account_upgrade",
    "account_transfer",
    "asset_create",
    "asset_update",
    "asset_update_bitasset",
    "asset_update_feed_producers",
    "asset_issue",
    "asset_reserve",
    "asset_fund_fee_pool",
    "asset_settle",
    "asset_global_settle",
    "asset_publish_feed",
    "witness_create",
    "witness_update",
    "proposal_create",
    "proposal_update",
    "proposal_delete",
    "withdraw_permission_create",
    "withdraw_permission_update",
    "withdraw_permission_claim",
    "withdraw_permission_delete",
    "committee_member_create",
    "committee_member_update",
    "committee_member_update_global_parameters",
    "vesting_balance_create",
    "vesting_balance_withdraw",
    "worker_create",
    "custom",
    "assert",
    "balance_claim",
    "override_transfer",
    "transfer_to_blind",
    "blind_transfer",
    "transfer_from_blind",
    "asset_settle_cancel",
    "asset_claim_fees",
    "fba_distribute",

# cybex added operations ################
    "initiate_crowdfund",
    "participate_crowdfund",
    "withdraw_crowdfund",
    "cancel_vesting",
    "fill_crowdfund",
# end cybex added operations ###########

    "bid_collateral",
    "execute_bid",

# rte operation
    "cancel_all",

    "initiate_dice_bet",
    "deposit_dice_bet",
    "withdraw_dice_bet",
    "participate_dice_bet",
    "dice_bet_clearing",

# exchange operation
    "create_exchange",
    "update_exchange",
    "withdraw_exchange",
    "deposit_exchange",
    "remove_exchange",
    "participate_exchange",
    "exchange_fill"
]

cybex_operations = {o: cybex_ops.index(o) for o in cybex_ops}

operations.default_prefix = 'CYB'

operationids.ops = cybex_ops

operationids.operations = cybex_operations

from bitsharesbase.objects import Operation

__CYBEX_OPERATIONS = ['Transfer', 'Limit_order_create', 'Limit_order_cancel', 'Override_transfer',
                      'Assert',
                      'Cancel_vesting', 'Balance_claim', 'Asset_issue',
                      'Custom', 'Account_whitelist', 'Cancel_all', 'Proposal_delete', 
                      'Initiate_dice_bet', 'Deposit_dice_bet', 'Withdraw_dice_bet', 'Participate_dice_bet',
                      'Create_exchange' , 'Update_exchange', 'Deposit_exchange', 'Withdraw_exchange', 'Remove_exchange', 'Participate_exchange' ]

def new_getklass(p1, name):
    if name not in __CYBEX_OPERATIONS:
        module = __import__("bitsharesbase.operations", fromlist=["operations"])
        class_ = getattr(module, name)
        return class_
    else:
        module = __import__("cybex.cybex_operations", fromlist=["operations"])
        class_ = getattr(module, name)
        return class_

Operation._getklass = new_getklass

class QuickPrivateKey(object):
    def __init__(self, wif = None, prefix = "GPH"):
        if wif is None:
            import os
            self._wif = Base58(hexlify(os.urandom(32)).decode('ascii'))
        elif isinstance(wif, Base58):
            self._wif = wif
        else:
            self._wif = Base58(wif)
    def __repr__(self):
        return repr(self._wif)
    def __bytes__(self):
        if sys.version > '3':
            return bytes(self._wif)
        else:
            return self._wif.__bytes__()

# replace ecdsa.PrivateKey to provide quick signing
# graphenebase.ecdsa.PrivateKey = QuickPrivateKey

import hashlib
from coincurve._libsecp256k1 import ffi as CCffi, lib as CClib
from coincurve.context import GLOBAL_CONTEXT as CCGLOBAL_CONTEXT
import coincurve.utils as CCutils
from graphenebase.ecdsa import _is_canonical


def quick_sign_message(message, wif, hashfn = hashlib.sha256):
    if not isinstance(message, bytes):
        message = bytes(message, "utf-8")

    digest = hashfn(message).digest()
    priv_key = QuickPrivateKey(wif)
    if sys.version > '3':
        p = bytes(priv_key)
    else:
        p = bytes(priv_key.__bytes__())

    ndata = CCffi.new("const int *ndata")
    ndata[0] = 0
    while True:
        ndata[0] += 1
        signature = CCffi.new('secp256k1_ecdsa_recoverable_signature *')
        signed = CClib.secp256k1_ecdsa_sign_recoverable(
            CCGLOBAL_CONTEXT.ctx,
            signature,
            digest, p, CCffi.NULL, ndata
        )

        if not signed:
            raise AssertionError()

        output = CCffi.new('unsigned char[%d]' % 64)
        recid = CCffi.new('int *')

        CClib.secp256k1_ecdsa_recoverable_signature_serialize_compact(
            CCGLOBAL_CONTEXT.ctx,
            output,
            recid,
            signature)

        output_sig = CCffi.buffer(output, 64)
        
        if _is_canonical(output_sig):
            return bytes(
                 CCutils.int_to_bytes(31 + recid[0]) + 
                 output_sig)

graphenebase.signedtransactions.sign_message = quick_sign_message
