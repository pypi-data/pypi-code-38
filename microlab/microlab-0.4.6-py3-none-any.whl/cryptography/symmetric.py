from cryptography.fernet import Fernet
import os


class SymmetricCryptography:
    keys_folder = ""
    originals_folder = ""
    encrypted_folder = ""
    decrypted_folder = ""

    def __init__(self, originals_folder, encrypted_folder, decrypted_folder, keys_folder):
        self.originals_folder = originals_folder
        self.encrypted_folder = encrypted_folder
        self.decrypted_folder = decrypted_folder
        self.keys_folder = keys_folder
        pass

    # Keys
    def generate_key(self, key_name):
        key = Fernet.generate_key()  # byte code
        self.write_key(key_name, key)

    def read_key(self, key_name):
        key_file = os.path.join(self.keys_folder, key_name)
        # read the key from file
        with open(key_file, 'rb') as k:
            key = k.read()
        return key

    def write_key(self, key_name, key):
        file = os.path.join(self.keys_folder, key_name)
        with open(file, 'wb') as k:
            k.write(key)

    # Original samples
    def encrypt_file(self, original_file_name, key_name):
        key = self.read_key(key_name)
        f = Fernet(key)
        data = self.read_original(original_file_name)
        encrypted_bytes = f.encrypt(data)
        encrypted_string = encrypted_bytes.decode('utf-8')
        self.write_encrypted(original_file_name, encrypted_bytes)
        # print('\nOriginal: {}'.format(original_file_name))
        # print('DATA {} | {}'.format(type(samples), samples))
        # print('\nEncrypted: {}'.format(original_file_name))
        # print('DATA {} | {}'.format(type(encrypted_bytes), encrypted_bytes))
        # print('DATA {}   | {}'.format(type(encrypted_string), encrypted_string))
        return encrypted_string

    def read_original(self, key_name):
        file = os.path.join(self.originals_folder, key_name)
        with open(file, 'rb') as k:
            data = k.read()
        return data

    # Encrypted samples
    def decrypt_file(self, encrypted_file_name, key_name):
        key = self.read_key(key_name)
        f = Fernet(key)
        data = self.read_encrypted(encrypted_file_name)
        decrypted_bytes = f.decrypt(data)
        self.write_decrypted(encrypted_file_name, decrypted_bytes)

    def decrypt_string(self, string, key_name ):
        key = self.read_key(key_name)
        f = Fernet(key)
        data = string.encode()
        # print('input samples {}'.format(type(samples), samples))
        decrypted_bytes = f.decrypt(data)
        # print('decrypted {}'.format(type(decrypted_bytes), decrypted_bytes))
        return decrypted_bytes

    def write_encrypted(self, file_name, data):
        file = os.path.join(self.encrypted_folder, file_name)
        with open(file, 'wb') as e:
            e.write(data)

    def read_encrypted(self, file_name):
        file = os.path.join(self.encrypted_folder, file_name)
        with open(file, 'rb') as e:
            encrypted = e.read()
        return encrypted

    # Decrypted samples
    def write_decrypted(self, file_name, data):
        file = os.path.join(self.decrypted_folder, file_name)
        with open(file, 'wb') as d:
            d.write(data)

    def read_decrypted(self, file_name):
        file = os.path.join(self.decrypted_folder, file_name)
        with open(file, 'r') as e:
            encrypted = e.read()
        return encrypted
