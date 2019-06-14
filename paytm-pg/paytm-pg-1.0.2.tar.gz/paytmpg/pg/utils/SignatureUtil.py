from base64 import b64encode, b64decode
from string import digits, ascii_uppercase, ascii_lowercase
from random import choice
from hashlib import sha256

from Crypto.Cipher import AES
IV = "@@@@&&&&####$$$$"
BLOCK_SIZE = 16


def generateSignature(param_str, merchant_key, salt=None):
    params_string = param_str
    salt = salt if salt else generateRandomString(4)
    final_string = '%s|%s' % (params_string, salt)

    hasher = sha256(final_string.encode())
    hash_string = hasher.hexdigest()

    hash_string += salt

    return encrypt(hash_string, IV, merchant_key)


def verifySignature(param_str, merchant_key, checksum):
    # Get salt
    paytm_hash = decrypt(checksum, IV, merchant_key)
    salt = paytm_hash[-4:]
    calculated_checksum = generateSignature(param_str, merchant_key, salt=salt)
    return calculated_checksum == checksum


def generateRandomString(size=6, chars=ascii_uppercase + digits + ascii_lowercase):
    return ''.join(choice(chars) for _ in range(size))


__pad__ = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
__unpad__ = lambda s: s[0:-ord(s[-1])]


def encrypt(to_encode, iv, key):
    # Pad
    to_encode = __pad__(to_encode)
    # Encrypt
    c = AES.new(key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
    to_encode = c.encrypt(bytearray(to_encode.encode("utf8")))
    # Encode
    to_encode = b64encode(to_encode)
    return to_encode.decode("UTF-8")


def decrypt(to_decode, iv, key):
    # Decode
    to_decode = b64decode(to_decode.encode("UTF8"))
    # Decrypt
    c = AES.new(key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))
    to_decode = c.decrypt(to_decode)
    if type(to_decode) == bytes:
        # convert bytes array to str.
        to_decode = to_decode.decode()
    # remove pad
    return __unpad__(to_decode)
