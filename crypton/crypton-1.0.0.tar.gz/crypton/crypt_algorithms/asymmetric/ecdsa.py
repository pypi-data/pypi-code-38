import os
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

current_file_path = os.getcwd()


class ECDSA:
    options_key = [224, 256, 384, 521]

    def __init__(self, key_size=0):
        self.curve = self.get_curve(key_size=key_size)

    @staticmethod
    def get_curve(key_size):
        if key_size == 224:
            return ec.SECP224R1
        if key_size == 256:
            return ec.SECP256R1
        if key_size == 384:
            return ec.SECP384R1
        if key_size == 521:
            return ec.SECP521R1

    def generate_key_pair(self):

        private_key = ec.generate_private_key(curve=self.curve, backend=default_backend())

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

    @staticmethod
    def sign(text_file_path, private_key_path):

        with open(private_key_path, 'rb') as private_key_file:
            pem_data = private_key_file.read()

        private_key = load_pem_private_key(pem_data, password=None, backend=default_backend())

        with open(text_file_path, 'rb') as file_to_sign:
            data = file_to_sign.read()
            signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))

        return signature

    def file_sign(self, text_file_path, private_key_path):
        signature = self.sign(text_file_path=text_file_path, private_key_path=private_key_path)

        open(os.path.dirname(text_file_path) + '/signature.bin', 'wb').write(signature)

    @staticmethod
    def verify(text_file_path, public_key_path, signature_path):
        # Verification requires the public key,
        # the signature itself, the signed data

        with open(public_key_path, 'rb') as public_key_file:
            pem_data = public_key_file.read()

        public_key = load_pem_public_key(pem_data, backend=default_backend())

        with open(signature_path, 'rb') as signature_file:
            signature = signature_file.read()

        with open(text_file_path, 'rb') as file_to_sign:
            data = file_to_sign.read()

        try:
            public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False
