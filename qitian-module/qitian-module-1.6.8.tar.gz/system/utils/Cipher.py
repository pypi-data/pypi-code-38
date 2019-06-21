import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import hashlib


class QTCipher(object):

    def __init__(self, key):
        self.byte_size = 16
        self.key = key.encode('utf8')

    def encrypt(self, data):
        if not isinstance(data, str):
            data = str(data)
        chiper = AES.new(self.key, AES.MODE_ECB)
        pad_data = pad(data.encode(), self.byte_size)
        chiper_data = chiper.encrypt(pad_data)
        return base64.urlsafe_b64encode(chiper_data).decode('utf8')

    def decrypt(self, data):
        data += '===='[:len(data) % 4]
        try:
            de64_data = base64.urlsafe_b64decode(data)
            chiper = AES.new(self.key, AES.MODE_ECB)
            real_data = chiper.decrypt(de64_data)
        except Exception as e:
            return 0
        try:
            decoded = unpad(real_data, self.byte_size).decode('utf8')
        except Exception as e:
            decoded = real_data.decode('utf8')
        return decoded

    @staticmethod
    def md5(data):
        obj = hashlib.md5()
        obj.update(data.encode('utf8'))
        return obj.hexdigest()
