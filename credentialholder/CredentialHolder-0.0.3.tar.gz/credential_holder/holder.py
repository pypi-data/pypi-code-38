from hashlib import sha256 as KeyHasher
from hashlib import sha512 as PassphraseHasher
from secrets import token_bytes

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

STRING_ENCODING = "utf-8"
AES_MODE = AES.MODE_CBC


class CredentialHolder(object):
    def __init__(self, passphrase, credential):
        self.iv = token_bytes(16)

        passphrase_hasher = PassphraseHasher()
        passphrase_hasher.update(passphrase.encode(STRING_ENCODING))
        self.passphrase_hash = passphrase_hasher.digest()

        key_hasher = KeyHasher()
        key_hasher.update(passphrase.encode(STRING_ENCODING))
        key = key_hasher.digest()

        cipher = AES.new(key, AES_MODE, iv=self.iv)
        self.encrypted_credential = cipher.encrypt(
            pad(credential.encode(STRING_ENCODING), AES.block_size)
        )

    def get_credential(self, supplied_passphrase):
        passphrase_hasher = PassphraseHasher()
        passphrase_hasher.update(supplied_passphrase.encode(STRING_ENCODING))
        supplied_passphrase_hash = passphrase_hasher.digest()

        if supplied_passphrase_hash != self.passphrase_hash:
            raise MismatchedPassphrasesException(
                "The supplied passphrase was not verifiable"
            )

        key_hasher = KeyHasher()
        key_hasher.update(supplied_passphrase.encode(STRING_ENCODING))
        key = key_hasher.digest()

        cipher = AES.new(key, AES_MODE, iv=self.iv)

        return unpad(cipher.decrypt(self.encrypted_credential), AES.block_size).decode(
            STRING_ENCODING
        )


class RebuiltCredentialHolder(CredentialHolder):
    def __init__(self, iv, passphrase_hash, encrypted_credential):
        object.__init__(self)

        self.iv = iv
        self.passphrase_hash = passphrase_hash
        self.encrypted_credential = encrypted_credential


class MismatchedPassphrasesException(Exception):

    pass
