"""
:module: pynetworking.Cryptography
:synopsis: Access to Cryptography
:author: Julian Sobott

public classes
---------------

.. autoclass:: Cryptographer
   :members:
   :undoc-members:
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend as crypto_default_backend


class Cryptographer:
    """Functions for encryption. Supports symmetric and asymmetric keys.

    :ivar is_encrypted_communication: Signals whether the messages are plain or encrypted.
    :ivar _communication_key: All messages are encrypted with this key.
    :ivar _public_key: Needed to exchange the communication key.
    :ivar _private_key: Needed to exchange the communication key.
    :ivar _fernet: Decrypts and encrypts messages.
    """
    def __init__(self):
        self._communication_key = None
        self._public_key = None
        self._private_key = None
        self._fernet = None
        self.is_encrypted_communication = False

    @property
    def communication_key(self):
        return self._communication_key

    @communication_key.setter
    def communication_key(self, key):
        """Sets the communication key, is_encrypted_communication and fernet"""
        if self.communication_key is None:
            self.is_encrypted_communication = True
            self._fernet = Fernet(key)
            self._communication_key = key

    def encrypt(self, byte_string: bytes) -> bytes:
        if not self.is_encrypted_communication:
            return byte_string
        return self._fernet.encrypt(byte_string)

    def decrypt(self, byte_string: bytes) -> bytes:
        if not self.is_encrypted_communication:
            return byte_string
        return self._fernet.decrypt(byte_string)

    def generate_pgp_key_pair(self) -> tuple:
        self._private_key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=65537,
            key_size=2048
        )
        self._public_key = self._private_key.public_key()
        return self._private_key, self._public_key

    @staticmethod
    def generate_communication_key():
        """Generates a symmetric key"""
        return Fernet.generate_key()

    def get_serialized_public_key(self) -> bytes:
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def public_key_from_serialized_key(self, serialized_key: bytes):
        """Set the public key, by deserialize the serialized public key."""
        self._public_key = serialization.load_pem_public_key(
            serialized_key,
            backend=crypto_default_backend()
        )
        return self._public_key

    def encrypt_pgp_msg(self, message: bytes) -> bytes:
        return self._public_key.encrypt(
            message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def decrypt_pgp_msg(self, ciphertext: bytes) -> bytes:
        return self._private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
