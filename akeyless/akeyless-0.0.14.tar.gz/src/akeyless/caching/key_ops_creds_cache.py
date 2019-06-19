from akeyless_uam_api import DerivationCredsReplyObj, RSADecryptCredsReplyObj
from cachetools import TTLCache

from akeyless.api.base import AkeylessApiI
from akeyless.auth import CredsRenewal


class CacheKey(object):
    def __init__(self, key_name, key_version=0, restriction=""):
        # type: (str, int, str) -> None
        self.key_name = key_name
        self.key_version = key_version
        self.restriction = restriction

    def __repr__(self):
        return "{name}-{version}-{restriction}".format(name=self.key_name,
                                                       version=self.key_version,
                                                       restriction=self.restriction)

    def __hash__(self):
        return hash((self.key_name, self.key_version, self.restriction))

    def __eq__(self, other):
        return (self.key_name, self.key_version, self.restriction) == \
               (other.key_name, other.key_version, other.restriction)

    def __ne__(self, other):
        return not (self == other)


class KeyOperationsCredsCache(object):
    CREDS_EXP_TIME = 58 * 60  # seconds

    def __init__(self, api, creds_renewal, maxsize=1000):
        # type: (AkeylessApiI, CredsRenewal, int) -> None
        self.api = api
        self.creds_renewal = creds_renewal
        self.derivation_creds_cache = DerivationCredsCache(api, creds_renewal, maxsize, self.CREDS_EXP_TIME)
        self.rsa_decrypt_creds_cache = RSADecryptCredsCache(api, creds_renewal, maxsize, self.CREDS_EXP_TIME)

    def get_key_derivation_creds(self, key_name, key_version=0, restriction=""):
        # type: (str, int, str) -> DerivationCredsReplyObj
        k = CacheKey(key_name, key_version, restriction)
        return self.derivation_creds_cache[k]

    def get_rsa_key_decrypt_creds(self, key_name, key_version=0, restriction=""):
        # type: (str, int, str) -> RSADecryptCredsReplyObj
        k = CacheKey(key_name, key_version, restriction)
        return self.rsa_decrypt_creds_cache[k]


class DerivationCredsCache(TTLCache):

    def __init__(self, api, creds_renewal, maxsize, ttl):
        # type: (AkeylessApiI, CredsRenewal, int, int) -> None
        super(DerivationCredsCache, self).__init__(maxsize=maxsize, ttl=ttl)
        self.api = api
        self.creds_renewal = creds_renewal

    def __missing__(self, k):
        ops_creds = self.api.get_item_derivation_creds(self.creds_renewal.get_uam_creds(),
                                                       k.key_name, item_version=k.key_version,
                                                       restricted_derivation_data=k.restriction)
        self[k] = ops_creds
        return ops_creds


class RSADecryptCredsCache(TTLCache):

    def __init__(self, api, creds_renewal, maxsize, ttl):
        # type: (AkeylessApiI, CredsRenewal, int, int) -> None
        super(RSADecryptCredsCache, self).__init__(maxsize=maxsize, ttl=ttl)
        self.api = api
        self.creds_renewal = creds_renewal

    def __missing__(self, k):
        ops_creds = self.api.get_rsa_key_decrypt_creds(self.creds_renewal.get_uam_creds(),
                                                       k.key_name, item_version=k.key_version,
                                                       restricted_cipher=k.key_name)
        self[k] = ops_creds
        return ops_creds
