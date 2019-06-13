import base64
import binascii
from Cryptodome import Random
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Util import Counter
from cryptography.hazmat.primitives.padding import PKCS7

unpad = lambda s: s[:-ord(s[len(s) - 1:])]


class Aes:
    options_key = [128, 192, 256]

    def __init__(self, key_size=0, passphrase=''):
        self.key_size = key_size
        self.passphrase = passphrase

    def generate_key(self):
        salt = Random.new().read(8)
        kdf = PBKDF2(self.passphrase, salt, 64, 1000)
        key = kdf[:AES.block_size]

        return key

    @staticmethod
    def encrypt(key, mode, text_file_path):
        with open(text_file_path, 'rb') as file:
            plaintext = file.read()
            padder = PKCS7(128).padder()
            raw = padder.update(plaintext) + padder.finalize()
            iv = Random.new().read(AES.block_size)

            if mode == 'CBC':
                cipher = AES.new(base64.b64decode(key),
                                 AES.MODE_CBC,
                                 iv)
            else:
                cipher = AES.new(base64.b64decode(key),
                                 AES.MODE_CTR,
                                 counter=Counter.new(AES.block_size * 8,
                                                     initial_value=int(binascii.hexlify(iv), 16))
                                 )

            return base64.b64encode(iv + cipher.encrypt(plaintext=raw))

    def encrypt_file(self, key, mode, text_file_path):
        encrypted = self.encrypt(key=key,
                                 mode=mode,
                                 text_file_path=text_file_path)

        open(text_file_path.split('.')[0] + '.aes', 'w').write(encrypted.decode('utf-8'))

    @staticmethod
    def decrypt(key, mode, text_file_path):
        with open(text_file_path, 'rb') as cipher_file:
            ciphered = cipher_file.read()  # bytes
            enc = base64.b64decode(ciphered)
            iv = enc[:AES.block_size]

            if mode == 'CBC':
                cipher = AES.new(base64.b64decode(key),
                                 AES.MODE_CBC,
                                 iv)
                decrypted = unpad(cipher.decrypt(enc[AES.block_size:]))

            else:
                cipher = AES.new(base64.b64decode(key),
                                 AES.MODE_CTR,
                                 counter=Counter.new(AES.block_size * 8, initial_value=int(binascii.hexlify(iv), 16))
                                 )
                decrypted = cipher.decrypt(enc[AES.block_size:])

            return bytes.decode(decrypted)

    def decrypt_file(self, key, mode, text_file_path):
        decrypted = self.decrypt(key=key,
                                 mode=mode,
                                 text_file_path=text_file_path)
        open(text_file_path.split('.')[0] + '-decrypted.txt', 'w+').write(decrypted)
