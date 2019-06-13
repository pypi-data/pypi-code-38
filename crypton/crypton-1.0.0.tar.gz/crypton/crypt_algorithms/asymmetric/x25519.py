import os
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives import serialization as crypto_serialization

current_file_path = os.getcwd()


class X25519:
    options_key = [256]

    def __init__(self, key_size=256):
        self.key_size = key_size

    @staticmethod
    def generate_key_pair():
        private_key = X25519PrivateKey.generate()

        return private_key, private_key.public_key()

    def file_key_pair(self, file_path=''):
        private_key, public_key = self.generate_key_pair()

        private_key_bytes = private_key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption())

        public_key_bytes = private_key.public_key().public_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PublicFormat.SubjectPublicKeyInfo
        )

        if file_path:
            open(file_path + '/private.pem', 'w+').write(private_key_bytes.decode('utf-8'))
            open(file_path + '/public.pem', 'w+').write(public_key_bytes.decode('utf-8'))
        else:
            open(current_file_path + '/private.pem', 'w+').write(private_key_bytes.decode('utf-8'))
            open(current_file_path + '/public.pem', 'w+').write(public_key_bytes.decode('utf-8'))
