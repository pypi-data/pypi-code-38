import btcpy
from btcpy.structs.hd import ExtendedPrivateKey, ExtendedPublicKey


def setup_btcpy(network):
    btcpy.setup.MAINNET = None
    btcpy.setup.NETWORK = None
    btcpy.setup.setup(network)


class XPrv(object):
    def __init__(self, key, compressed=True):
        setup_btcpy('mainnet')
        self.compressed = compressed
        self.key = ExtendedPrivateKey.decode(key)

    def derive(self, path):
        setup_btcpy('mainnet')
        return self.__class__(self.key.derive(path).encode(), compressed=self.compressed)

    def prv(self):
        setup_btcpy('mainnet')
        return self.key.key.hexlify()

    def pub(self):
        setup_btcpy('mainnet')
        return self.key.key.pub(compressed=self.compressed).hexlify()

    def pkh(self):
        setup_btcpy('mainnet')
        return self.pkh_hasher(self.key.key.pub(compressed=self.compressed).serialize())

    def pkh_hasher(self, public_key):
        raise NotImplemented()


class XPub(object):
    def __init__(self, key, compressed=True):
        setup_btcpy('mainnet')
        self.compressed = compressed
        self.key = ExtendedPublicKey.decode(key)

    def derive(self, path):
        setup_btcpy('mainnet')
        return self.__class__(self.key.derive(path).encode(), compressed=self.compressed)

    def pub(self):
        setup_btcpy('mainnet')
        return self.key.key.uncompressed.hexlify()

    def pkh(self):
        setup_btcpy('mainnet')
        if self.compressed:
            return self.pkh_hasher(self.key.key.uncompressed.serialize())
        else:
            return self.pkh_hasher(self.key.key.uncompressed.serialize())

    def pkh_hasher(self, public_key):
        raise NotImplemented()
