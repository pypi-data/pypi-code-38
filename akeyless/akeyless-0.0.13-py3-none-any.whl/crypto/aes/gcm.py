from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, modes, algorithms

from akeyless.crypto.random import token_bytes


class GCMHandler(object):
    GCM_IV_LENGTH = 12
    GCM_TAG_SIZE = 16

    def __init__(self, key):
        # type: (bytes) -> None
        self.key = key

    def encrypt(self, plaintext, associated_data=b""):
        # type: (bytes, bytes) -> bytes
        # Generate a random 96-bit IV.
        iv = token_bytes(self.GCM_IV_LENGTH)

        # Construct an AES-GCM Cipher object with the given key and a
        # randomly generated IV.
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()

        if associated_data is not None:
            # associated_data will be authenticated but not encrypted,
            # it must also be passed in on decryption.
            encryptor.authenticate_additional_data(associated_data)

        # Encrypt the plaintext and get the associated ciphertext.
        # GCM does not require padding.
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return iv + ciphertext + encryptor.tag

    def decrypt(self, ciphertext, associated_data):
        # type: (bytes, bytes) -> bytes

        if len(ciphertext) < self.GCM_IV_LENGTH + self.GCM_TAG_SIZE:
            raise ValueError("Invalid ciphertext")

        iv = ciphertext[:self.GCM_IV_LENGTH]
        tag = ciphertext[len(ciphertext) - self.GCM_TAG_SIZE:]
        cipher = ciphertext[self.GCM_IV_LENGTH: len(ciphertext) - self.GCM_TAG_SIZE:]
        # Construct a Cipher object, with the key, iv, and additionally the
        # GCM tag used for authenticating the message.
        decryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv, tag),
            backend=default_backend()
        ).decryptor()

        # We put associated_data back in or the tag will fail to verify
        # when we finalize the decryptor.
        decryptor.authenticate_additional_data(associated_data)

        # Decryption gets us the authenticated plaintext.
        # If the tag does not match an InvalidTag exception will be raised.
        return decryptor.update(cipher) + decryptor.finalize()
