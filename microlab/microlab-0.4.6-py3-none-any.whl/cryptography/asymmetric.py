from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from microlab.io.folders import create_folder

import os


class AsymmetricCryptography:

    # Directories
    private_keys_folder = ''
    public_keys_folder = ''

    # Data
    originals_folder = ''
    encrypted_folder = ''
    decrypted_folder = ''

    # temp
    private_key = ''
    public_key = ''
    encrypted = ''
    decrypted = ''
    original = ''

    def __init__(self, private_keys_folder, public_keys_folder, originals_folder, encrypted_folder, decrypted_folder):
        self.private_keys_folder = private_keys_folder
        self.public_keys_folder = public_keys_folder
        self.originals_folder = originals_folder
        self.encrypted_folder = encrypted_folder
        self.decrypted_folder = decrypted_folder

        # create folders if not exist
        create_folder(path=private_keys_folder, verbose=False)
        create_folder(path=public_keys_folder, verbose=False)
        create_folder(path=originals_folder, verbose=False)
        create_folder(path=encrypted_folder, verbose=False)
        create_folder(path=decrypted_folder, verbose=False)

    # Genetrate
    def generate_pair_of_keys(self, key_size=2048, verbose=False):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend())
        self.public_key = self.private_key.public_key()
        if verbose:
            print('[ Keys ]  generated new keys with size {} '.format(key_size))

    # Export
    def export_private_key(self, key_name, verbose=False):
        private_key_path = os.path.join(self.private_keys_folder, key_name)
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption())
        with open(private_key_path, 'wb') as f:
            f.write(pem)
        if verbose:
            print('[ Keys ]  exported private key to {}'.format(private_key_path))

    def export_public_key(self, key_name, verbose=False):
        public_key_path = os.path.join(self.public_keys_folder, key_name)
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)
        with open(public_key_path, 'wb') as f:
            f.write(pem)
        if verbose:
            print('[ Keys ]  exported public key to {}'.format(public_key_path))

    # Load
    def load_private_key(self, key_name, password=None, verbose=False):
        private_key_path = os.path.join(self.private_keys_folder, key_name)
        with open(private_key_path, "rb") as key_file:
            self.private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=password,
                backend=default_backend()
            )
        if verbose:
            print('[ Keys ]  imported private keyfrom {}'.format(private_key_path))

    def load_public_key(self, key_name, verbose=False):
        public_key_path = os.path.join(self.public_keys_folder, key_name)
        with open(public_key_path, "rb") as key_file:
            self.public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        if verbose:
            print('[ Keys ]  imported public key from {}'.format(public_key_path))

    # Encrypt
    def encrypt(self, file_name, verbose=False):
        original_path = os.path.join(self.originals_folder, file_name)
        encrypted_path = os.path.join(self.encrypted_folder, file_name)

        with open(original_path, 'rb') as f:
            message = f.read()

        self.encrypted = self.public_key.encrypt(
                        message,
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None))
        with open(encrypted_path, 'wb') as f:
            f.write(self.encrypted)
        if verbose:
            print('[ Encrypt ]  encrypted saved to {}'.format(encrypted_path))

    # Decrypt
    def decrypt(self, file_name, verbose=False):
        encrypted_path = os.path.join(self.encrypted_folder, file_name)
        with open(encrypted_path, "rb") as f:
            self.encrypted = f.read()

        self.decrypted = self.private_key.decrypt(
                        self.encrypted,
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None))

        decrypted_path = os.path.join(self.decrypted_folder, file_name)
        with open(decrypted_path, "wb") as f:
            f.write(self.decrypted)
        if verbose:
            print('[ Decrypt ]  decrypted saved to {}'.format(decrypted_path))



