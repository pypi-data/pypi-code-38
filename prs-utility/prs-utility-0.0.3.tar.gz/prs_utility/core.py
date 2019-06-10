import json
import os

from eth_keyfile import decode_keyfile_json
from eth_utils import (
    keccak,
    to_bytes
)
import eth_keys

from . import util


__all__ = [
    'keccak', 'recover_private_key', 'private_key_to_address',
    'create_key_pair', 'sign_hash', 'sig_to_address',
]


def recover_private_key(keystore, password, dump=True):
    """recover private key with keystore and password

    :param keystore: str, keystore -> json.dumps(keystore)
    :param password: str
    :param dump: bool, True: return `bytes.hex`, False: return bytes

    :return: str (bytes.hex) or bytes
    """
    keystore = json.loads(keystore)
    password = to_bytes(text=password)
    private_key = decode_keyfile_json(keystore, password)
    return util.dump_buf(private_key, dump)


def get_private_key(obj):
    """get private key from obj

    :param obj: str or bytes or eth_keys.datatypes.PrivateKey,
        raise exception if can not get private key

    :return: eth_keys.datatypes.PrivateKey
    """
    if isinstance(obj, eth_keys.datatypes.PrivateKey):
        return obj

    if isinstance(obj, str):
        obj = to_bytes(hexstr=obj)

    if isinstance(obj, bytes):
        private_key = eth_keys.keys.PrivateKey(obj)
        return private_key

    raise ValueError('can not get private key from %r' % obj)


def private_key_to_address(private_key):
    """return the address of public key

    :param private_key: str (hex str) or bytes or eth_keys.datatypes.PrivateKey

    :return: str, hex str, remove '0x' prefix
    """
    private_key = get_private_key(private_key)
    address = private_key.public_key.to_address()
    return util.remove_prefix_0x(address)


def keccak256(message):
    """message digest with keccak

    :param message: str
    :return: hex str
    """
    _hash = keccak(text=message)
    return _hash.hex()


def create_key_pair(dump=True):
    """create key pair

    :param dump: bool, True: return `bytes.hex`, False: return bytes

    :return: dict, {
            'privateKey': private_key, 'publicKey': public_key,
            'address': address
        }
    """
    # generate private key
    private_key = eth_keys.keys.PrivateKey(os.urandom(32))
    public_key = eth_keys.keys.PublicKey.from_private(private_key)
    address = private_key_to_address(private_key)

    return {
        'privateKey': util.dump_buf(private_key.to_bytes(), dump),
        'publicKey': util.dump_buf(public_key.to_bytes(), dump),
        'address': address,
    }


def sign_hash(_hash, private_key):
    """sign hash with private_key

    :param _hash: message hash (digest message with keccak256)
    :param private_key: hex str, private key's hex str

    :return: dict, {'hash': _hash, 'signature': sign_hex}
    """
    # get signature
    private_key = get_private_key(private_key)
    sign = private_key.sign_msg_hash(util.hex_to_buf(_hash))
    sign_hex = util.remove_prefix_0x(sign.to_hex())
    return {
        'hash': _hash,
        'signature': sign_hex,
    }


def sig_to_address(msg_hash, sig):
    """get public key's address with msg_hash and sign hex str

    :param msg_hash: hex str of message hash
    :param sig: hex str of signature

    :return: hex str, public key's address
    """
    signature = eth_keys.keys.Signature(
        signature_bytes=util.hex_to_buf(sig)
    )
    public_key = signature.recover_public_key_from_msg_hash(
        util.hex_to_buf(msg_hash)
    )
    address = public_key.to_address()
    return util.remove_prefix_0x(address)


def hash_text(message):
    """get the hash of text data

    :param message: str

    :return: hex str, digest message (keccak256)
    """
    return keccak256(message)


def hash_block_data(data):
    """get the hash of block data

    :param data: dict

    :return: hex str, digest message (keccak256)
    """
    sorted_data = util.get_sorted_qs(data)
    return keccak256(sorted_data)


def sign_block_data(data, private_key):
    """sign block data

    :param data: dict
    :param private_key: hex str (private key)

    :return: dict, {'hash': _hash, 'signature': sign_hex}
    """
    return sign_hash(hash_block_data(data), private_key)


def sign_text(message, private_key):
    """sign text data

    :param message: str
    :param private_key: hex str, private key

    :return: dict
    """
    return sign_hash(hash_text(message), private_key)


def sig_to_address_from_block(data, sig):
    """get public key's address with block data and sign hex str

    :param data: dict, block data
    :param sig: hex str of signature

    :return: hex str, public key's address
    """
    return sig_to_address(hash_block_data(data), sig)
