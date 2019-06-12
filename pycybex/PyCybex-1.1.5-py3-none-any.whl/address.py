from bitsharesbase.account import PublicKey
from binascii import hexlify, unhexlify
from graphenebase.base58 import base58decode,base58encode,doublesha256,ripemd160, Base58
import hashlib

def pts_address(pubkey, compressed = False, ver = 56, prefix = 'CYB'):
    if compressed:
       pubkeybin = PublicKey(pubkey,**{"prefix":prefix}).__bytes__()
    else:
       pubkeybin = unhexlify(PublicKey(pubkey,**{"prefix":prefix}).unCompressed())

    bin= '%02x' % (ver) + hexlify(ripemd160(hexlify(hashlib.sha256(pubkeybin).digest()).decode('ascii'))).decode("ascii")
    checksum = doublesha256(bin)

    hex = bin+hexlify(checksum[:4]).decode('ascii')
    hash = hexlify(ripemd160(hex)).decode('ascii')
    checksum2 = ripemd160(hash)
    b58 = prefix+base58encode(hash + hexlify(checksum2[:4]).decode('ascii'))

    return b58

def all_addresses(pubkey):
    return [
            str(PublicKey(pubkey, prefix = 'CYB').address),
            pts_address(pubkey, compressed = False),
            pts_address(pubkey, compressed = True),
            pts_address(pubkey, compressed = False, ver = 0),
            pts_address(pubkey, compressed = True, ver = 0)
           ]

if __name__ == '__main__':
    print(pts_address('CYB6fUC5LDyARpzLqtebVDqV5Xb7PfPuxcPN6GpGUaXJ8VEztDQ85'))
    print(pts_address('CYB6fUC5LDyARpzLqtebVDqV5Xb7PfPuxcPN6GpGUaXJ8VEztDQ85', compressed = True))
    print(pts_address('CYB6fUC5LDyARpzLqtebVDqV5Xb7PfPuxcPN6GpGUaXJ8VEztDQ85', compressed = False, ver = 0))
    print(pts_address('CYB6fUC5LDyARpzLqtebVDqV5Xb7PfPuxcPN6GpGUaXJ8VEztDQ85', compressed = True, ver = 0))
