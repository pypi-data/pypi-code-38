import binascii

from akeyless.crypto.random import token_hex, token_bytes
from akeyless.crypto.utils.algorithms import CryptoAlgorithm
from akeyless.crypto.akeyless_crypto import encrypt, decrypt

DERIVATION_DATA_LEN = 8


def gen_derivation_data():
    return binascii.hexlify(token_bytes(DERIVATION_DATA_LEN))
