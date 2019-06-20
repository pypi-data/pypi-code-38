from string import ascii_letters, digits
from cryptography.fernet import Fernet

alphabet_list = ascii_letters + digits


def caesar_code(text: str, shift: int):
    shift_text = ''

    for c in text:
        if c not in alphabet_list:
            shift_text += c
            continue

        i = (alphabet_list.index(c) + shift) % len(alphabet_list)
        shift_text += alphabet_list[i]

    return shift_text


def encode_password(text: str):
    for offcet in range(1, 10):
        text = caesar_code(text, shift=offcet)
    return text


def decode_password(text: str):
    for offcet in range(9, 0, -1):
        text = caesar_code(text, shift=-offcet)
    return text
    

def get_key():
    return Fernet.generate_key()


def get_cipher(cipher_key: object):
    return Fernet(cipher_key)


def encrypt_str(text: object, cipher: object, get_str: bool = True):
    if isinstance(text, str):
        text = text.encode('utf-8')
    text_enc = cipher.encrypt(text)
    if get_str:
        text_enc = text_enc.decode('utf-8')
    return text_enc


def decrypt_str(text: object, cipher: object, get_str: bool = True):
    if isinstance(text, str):
        text = text.encode('utf-8')
    text_dec = cipher.decrypt(text)
    if get_str:
        text_dec = text_dec.decode('utf-8')
    return text_dec


def write_key(file_name: str, cipher_key: bytes):
    with open(file_name, 'wb') as f:
        f.write(cipher_key)


def read_key(file_name: str):
    try:
        with open(file_name, 'rb') as f:
            cipher_key = f.read()
    except:
        cipher_key = None
    return cipher_key


if __name__ == '__main__':
    # TEST
    cipher_key = get_key()
    cipher = get_cipher(cipher_key)
    text = 'qwerty1234!!'
    text_enc = encrypt_str(text, cipher)
    write_key('cipher_key', cipher_key)
    new_cipher_key = read_key('cipher_key')
    new_cipher = get_cipher(new_cipher_key)
    text_dec = decrypt_str(text_enc, new_cipher)
    print(text)
    print(text_dec)
