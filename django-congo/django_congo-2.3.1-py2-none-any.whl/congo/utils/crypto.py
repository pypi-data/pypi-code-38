from Crypto.Cipher import AES
from congo.conf import settings
import base64
import hashlib

def get_sha1(*args, **kwargs):
    text = kwargs.get('sha1_salt', settings.SECRET_KEY)
    for a in args:
        text += str(a)
    lenght = kwargs.get('lenght', 8)
    upper = kwargs.get('upper', True)
    result = hashlib.sha1(text).hexdigest()[:lenght]
    return result.upper() if upper else result.lower()

def get_md5(*args, **kwargs):
    text = kwargs.get('md5_salt', settings.SECRET_KEY)
    for a in args:
        text += str(a)
    lenght = kwargs.get('lenght', 12)
    upper = kwargs.get('upper', True)
    result = hashlib.md5(text).hexdigest()[:lenght]
    return result.upper() if upper else result.lower()

def encrypt(clear_text):
    aes = AES.new(settings.SECRET_KEY[:32])
    tag_string = (str(clear_text) + (AES.block_size - len(str(clear_text)) % AES.block_size) * "\0")
    cipher_text = base64.b64encode(aes.encrypt(tag_string))
    return cipher_text

def decrypt(cipher_text):
    aes = AES.new(settings.SECRET_KEY[:32])
    raw_decrypted = aes.decrypt(base64.b64decode(cipher_text))
    clear_text = raw_decrypted.rstrip("\0")
    return clear_text
