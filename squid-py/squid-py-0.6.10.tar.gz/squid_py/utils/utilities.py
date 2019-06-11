"""Utilities class"""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import uuid
from collections import namedtuple

from eth_keys import KeyAPI
from eth_utils import big_endian_to_int
from web3.utils.encoding import to_bytes

from squid_py.keeper.utils import generate_multi_value_hash

Signature = namedtuple('Signature', ('v', 'r', 's'))


def generate_new_id():
    """
    Generate a new id without prefix.

    :return: Id, str
    """
    return uuid.uuid4().hex + uuid.uuid4().hex


def generate_prefixed_id():
    """
    Generate a new id prefixed with 0x that is used as identifier for the service agreements ids.

    :return: Id, str
    """
    return f'0x{generate_new_id()}'


def prepare_prefixed_hash(msg_hash):
    """

    :param msg_hash:
    :return:
    """
    return generate_multi_value_hash(
        ['string', 'bytes32'],
        ["\x19Ethereum Signed Message:\n32", msg_hash]
    )


def get_public_key_from_address(web3, account):
    """

    :param web3:
    :param account:
    :return:
    """
    _hash = web3.sha3(text='verify signature.')
    signature = web3.personal.sign(_hash, account.address, account.password)
    signature = split_signature(web3, to_bytes(hexstr=signature))
    signature_vrs = Signature(signature.v % 27,
                              big_endian_to_int(signature.r),
                              big_endian_to_int(signature.s))
    prefixed_hash = prepare_prefixed_hash(_hash)
    pub_key = KeyAPI.PublicKey.recover_from_msg_hash(prefixed_hash,
                                                     KeyAPI.Signature(vrs=signature_vrs))
    assert pub_key.to_checksum_address() == account.address, \
        'recovered address does not match signing address.'
    return pub_key


def to_32byte_hex(web3, val):
    """

    :param web3:
    :param val:
    :return:
    """
    return web3.toBytes(val).rjust(32, b'\0')


def convert_to_bytes(web3, data):
    """

    :param web3:
    :param data:
    :return:
    """
    return web3.toBytes(text=data)


def convert_to_string(web3, data):
    """

    :param web3:
    :param data:
    :return:
    """
    return web3.toHex(data)


def convert_to_text(web3, data):
    """

    :param web3:
    :param data:
    :return:
    """
    return web3.toText(data)


def split_signature(web3, signature):
    """

    :param web3:
    :param signature: signed agreement hash, hex str
    :return:
    """
    assert len(signature) == 65, f'invalid signature, ' \
        f'expecting bytes of length 65, got {len(signature)}'
    v = web3.toInt(signature[-1])
    r = to_32byte_hex(web3, int.from_bytes(signature[:32], 'big'))
    s = to_32byte_hex(web3, int.from_bytes(signature[32:64], 'big'))
    if v != 27 and v != 28:
        v = 27 + v % 2

    return Signature(v, r, s)
