import base64
import os
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization as crypto_serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend, default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding

from crypton.crypt_algorithms.symmetric.aes import Aes

current_file_path = os.getcwd()


class RSA:
    options_key = [1024, 2048, 4096]

    def __init__(self, key_size=2048):
        self.public_exponent = 65537
        self.key_size = key_size

    def generate_key_pair(self):
        private_key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=self.public_exponent,
            key_size=self.key_size
        )

        return private_key, private_key.public_key()

    def file_key_pair(self, ssh=False, file_path='', ):
        private_key, public_key = self.generate_key_pair()

        private_key_bytes = private_key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.PKCS8,
            crypto_serialization.NoEncryption())

        if ssh:
            public_key_bytes = private_key.public_key().public_bytes(
                crypto_serialization.Encoding.OpenSSH,
                crypto_serialization.PublicFormat.OpenSSH
            )
            private_name = '/id_rsa'
            public_name = '/id_rsa.pub'
        else:
            public_key_bytes = private_key.public_key().public_bytes(
                crypto_serialization.Encoding.PEM,
                crypto_serialization.PublicFormat.PKCS1
            )
            private_name = '/private.pem'
            public_name = '/public.pem'

        if file_path:
            open(file_path + private_name, 'w+').write(private_key_bytes.decode('utf-8'))
            open(file_path + public_name, 'w+').write(public_key_bytes.decode('utf-8'))
        else:
            open(current_file_path + private_name, 'w+').write(private_key_bytes.decode('utf-8'))
            open(current_file_path + public_name, 'w+').write(public_key_bytes.decode('utf-8'))

    @staticmethod
    def sign(text_file_path, private_key_path):
        with open(private_key_path, 'rb') as private_key_file:
            pem_data = private_key_file.read()

        private_key = load_pem_private_key(pem_data, password=None, backend=default_backend())

        with open(text_file_path, 'rb') as file_to_sign:
            data = file_to_sign.read()
            signature = private_key.sign(data,
                                         padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                                     salt_length=padding.PSS.MAX_LENGTH),
                                         hashes.SHA256())

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
            public_key.verify(signature,
                              data,
                              padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                          salt_length=padding.PSS.MAX_LENGTH),
                              hashes.SHA256())
            return True
        except InvalidSignature:
            return False

    @staticmethod
    def encrypt(text_file_path, public_key_path):
        # In order to use RSA encryption with larger values, typically you generate a symmetric key for use with
        # another algorithm, such as AES. Then you encrypt the data using the AES symmetric key (there is no
        # limitation on size using a symmetric encryption algorithm) and then you RSA-encrypt just the symmetric key
        # and transmit that. AES keys are 16-32 bytes in size so they can easily fit within the RSA-encryption
        # limitations.

        with open(public_key_path, 'rb') as public_key_file:
            pem_data = public_key_file.read()

        public_key = load_pem_public_key(pem_data, backend=default_backend())

        aes_key = Aes(key_size=256).generate_key()
        encrypted_file = Aes().encrypt(key=base64.b64encode(aes_key),
                                       mode='CBC',
                                       text_file_path=text_file_path).decode('utf-8')

        encrypted_aes_key = public_key.encrypt(aes_key,
                                               padding.OAEP(
                                                   mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                   algorithm=hashes.SHA256(),
                                                   label=None))
        return encrypted_file, encrypted_aes_key

    def file_encrypt(self, text_file_path, public_key_path):
        encrypted_file, encrypted_aes_key = self.encrypt(text_file_path=text_file_path, public_key_path=public_key_path)

        open(os.path.abspath(text_file_path).split('.')[0] + '_encrypted.txt', 'w+').write(encrypted_file)
        open(os.path.dirname(text_file_path) + '/aes.key', 'wb').write(encrypted_aes_key)

    @staticmethod
    def decrypt(aes_key_path, private_key_path, encrypted_file_path):
        # Then the recipient decrypts the symmetric key using their private RSA key and then
        # they decrypt the encrypted data using the decrypted symmetric key.

        with open(private_key_path, 'rb') as private_key_file:
            pem_data = private_key_file.read()

        private_key = load_pem_private_key(pem_data, password=None, backend=default_backend())

        with open(aes_key_path, 'rb') as aes_key_file:
            aes_key_encrypted = aes_key_file.read()

        aes_key = private_key.decrypt(aes_key_encrypted,
                                      padding.OAEP(
                                          mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                          algorithm=hashes.SHA256(),
                                          label=None))

        return Aes().decrypt(key=base64.b64encode(aes_key),
                             mode='CBC',
                             text_file_path=encrypted_file_path)

    def file_decrypt(self, aes_key_path, private_key_path, encrypted_file_path):
        decrypted = self.decrypt(aes_key_path=aes_key_path,
                                 private_key_path=private_key_path,
                                 encrypted_file_path=encrypted_file_path)

        open(os.path.abspath(encrypted_file_path).split('_encrypted')[0] + '_decrypted.txt', 'w+').write(decrypted)
