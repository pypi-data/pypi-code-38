#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
# Author: yuyongpeng@hotmail.com
# Description: 加密解密的操作
#  

"""

import rsa
import base64
import shlex, subprocess
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5


def encrypt(msg, pub_key, encode='utf-8'):
    """
    使用公钥对字符串加密
    :param msg: 需要加密的字符串
    :param pub_key: 公钥
    :param encode: 编码
    :return: 加密后的字符串
    """
    pubkey = rsa.PublicKey.load_pkcs1(pub_key.encode(encode))
    crypto = rsa.encrypt(msg.encode(encode), pubkey)
    return crypto


def decrypt(crypto, pri_key, encode='utf-8'):
    """
    使用私钥界面字符串
    :param crypto: 加密的字符串
    :param pri_key: 私钥
    :param encode: 编码
    :return: 加密后的字符串
    """
    privkey = rsa.PrivateKey.load_pkcs1(pri_key.encode(encode))
    msg = rsa.decrypt(crypto, privkey)
    return msg


rsa_private_key = b'-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAz4C8rDjl6NAAvdUxLl7p8eA+xxc4Sa20puq2gFPk+8B5W30o+8xAaktLoji9wEsf7WTEllxZcIXw7d4K9b1M34ZDQT1iR4ZreB3GkxEXDeQIV3f/W7C3NL1bF5ePn7DRGZYKTEry8pp/lK/1ESP9Z+giaN29xm+jsmvNAOJlLjndn8nYcmA1sdDzuX8JSlZOiijAwyKUkwrBd+FqlhbAfF9ebcEgQcRISZsBMpcsZ66HQ0nvEnhmLzkfXxLUu2w7ccwLc/W7a4V1SNFEMZifRyiI7IhYYpRFw7egQN2RgzVWW/O6HKzk2Mxaz/6Y+HEehuDfRDn5MjMCkhnfbpRKKwIDAQABAoIBAD7xpkn32IYO0qrDCPAwCnc8ts5d1M1EzA/2EvZKfKOBd06xYMVA6ClWPdMvsx+pqj2w25Fg4iCoALWnLVvt2GvVpoEbxbw8ok0Fez8RaBTmn0EpPWTq7igpaIB3kTG3yTYhtW3/LkM5aooH9icE69GhMQ7udKrFIrr0yHMEOf0TNKBUNlwwHWJrpUuodXxIbERonkNdri1AnsWsnh4ePkKFlgaIdOZ24W4kHjfQAQkz3bPTjRzU5Q0LpkCpuYxk+TeOvR5tNPHXtzTWYek7JbCbnIKr1SiJx+ncwWM7QEnuvbzCU2VeTwb6Rq94WIg3RpfqSKJPr5w5e/df4jmi58ECgYEA74ty4UiChdp27/xvy2sJMilgkcL5Z0A+McPrjM82CqfPvr1+ZMBkTwuQGxFWlNtdE7DLpneVCWmzAexUJ02dFndSJMqsN81335VYfLc94qk5HXwmc9UBK7+qL2Ugyz76KoRGogqkKYw0ZR2kdpcNoXjQfeVgqrumt+jnZChpAl8CgYEA3cHPuDbdqqhcslz4+Zz8B0zWKN8Kj5CgG9ReEmJGpE6w5D7bds5iPcmp5xwFctuumAtroA/+bpGX/2oXc1nXucf/dI3AWoaBQrZ9iL6xfe7+ZPiRYuZjz3ygZ+Vcgp6xixbTT86jaIHwsD1wYtzOiiYOUBt4jDk89xookjpBg7UCgYEAtCriQOdUpHBoPKBVRV5AEGZmp7tJ8oqzPKLrK4E+WE1XR1MnGYhK6dj8jh9AS72iCAlVYuNWSToi1TN3KAiMOjWMpvd5CI+VtaiSYVtBRJWay75w/XYb51fFHNinDbdUWV4b8gym5Ej7r4HYDQoXyncf+VDooAF7p5+ZSg/Ky2kCgYAlVsv+Dab3ZE/vbH4zsX4yUHrC+QNTNxvuc6y/VbLlWaapV/gmIgwisUEde/di5qCYU1v04JyLy5IXXKrELn2Hd6iI3JFl7L35GLc8fjdup/5HzB7W00o9FpP/ynvwNn5YmChOiNG0+CQp2L6CtwFD+7JvRKDgo4ajaNEqBgsf/QKBgE6kbfW6FSpFdOs+2qpIXTEWnTqUC3WD1h1qB8G8J3Tn/o/bSm8C5lHmjmg9vRJtHisaoLyc2ikH7UZwPGU32340s22igkDZml730CKrYtnnBZAG+tIiERtI4Zj432X7qzBYgTgwO7wRAvds+WDCwwV5FMGNCzbPEXos8HmS0812\n-----END RSA PRIVATE KEY-----\n'
rsa_public_key = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz4C8rDjl6NAAvdUxLl7p8eA+xxc4Sa20puq2gFPk+8B5W30o+8xAaktLoji9wEsf7WTEllxZcIXw7d4K9b1M34ZDQT1iR4ZreB3GkxEXDeQIV3f/W7C3NL1bF5ePn7DRGZYKTEry8pp/lK/1ESP9Z+giaN29xm+jsmvNAOJlLjndn8nYcmA1sdDzuX8JSlZOiijAwyKUkwrBd+FqlhbAfF9ebcEgQcRISZsBMpcsZ66HQ0nvEnhmLzkfXxLUu2w7ccwLc/W7a4V1SNFEMZifRyiI7IhYYpRFw7egQN2RgzVWW/O6HKzk2Mxaz/6Y+HEehuDfRDn5MjMCkhnfbpRKKwIDAQAB\n-----END PUBLIC KEY-----\n'


def encrypt2(message, pub_key, encode='utf8'):
    rsakey = RSA.importKey(pub_key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(message))
    return cipher_text


def decrypt2(crypto, pri_key, encode='utf8'):
    rsakey = RSA.importKey(pri_key)
    cipher = Cipher_pkcs1_v1_5.new(rsakey)
    text = cipher.decrypt(base64.b64decode(crypto), None)
    return text.decode(encode)


#################################################################################################################################
# cryptography
#################################################################################################################################
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from oracle.database.dbs import get_soldier


def read_private_key(file, password=None):
    """
    加载私钥文件为对象
    :param file:
    :param password:
    :return:
    """
    with open(file, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=password,
            backend=default_backend()
        )
    return private_key


def read_public_key(file):
    """
    加载公钥文件为对象
    :param file:
    :return:
    """
    with open(file, 'rb') as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key


def generate_private_key(public_exponent=65537, key_size=2048, password=None):
    """
    生成私钥字符串或者序列化对象
    :param public_exponent:
    :param key_size:
    :param password: 是否需要对序列化的输出加密
    :return:
    """
    private_key_obj = rsa.generate_private_key(
        public_exponent=public_exponent,
        key_size=key_size,
        backend=default_backend()
    )
    if password is None or len(password) == 0:
        encryption = serialization.NoEncryption()
    else:
        encryption = serialization.BestAvailableEncryption(password)
    private_key_str = private_key_obj.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption
        # encryption_algorithm=serialization.BestAvailableEncryption(password)
    )
    return private_key_obj, private_key_str


def generate_public_key(private_key_obj):
    """
    根据私钥对象生成公钥串
    :param private_key_obj: cryptography类库的私钥对象
    :return:
    """
    public_key_obj = private_key_obj.public_key()
    public_key_str = public_key_obj.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    return public_key_obj, public_key_str


def encrypt_rsa(message, public_key_obj, encode='utf8'):
    """
    使用公钥加密字符串
    :param message: 需要加密的字符串
    :param public_key_obj: cryptography类库的公钥对象
    :param encode: message字符串的编码格式
    :return: base64编码的字符串
    """
    cipher_text = public_key_obj.encrypt(
        # message,
        message.encode(encode),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # print('加密数据： ', cipher_text)
    return base64.b64encode(cipher_text)
    # return cipher_text


def decrypt_rsa(crypto_message_base64, private_key_obj, encode='utf8'):
    """
    对加密的字符串使用私钥解密
    :param crypto_message_base64 加密后的字符串 (进行了base64编码)
    :param private_key_obj: cryptography类库的私钥对象
    :param encode:
    :return: bytes
    """
    plain_text = private_key_obj.decrypt(
        # 加密的信息
        # crypto_message,
        base64.b64decode(crypto_message_base64),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # print('解密数据: ', plain_text)
    return plain_text


def encrypt_ecies(public_key, original_text, iv=None):
    """
    使用命令行调用楚学文的ECIES库
    crypto-tx -h
    Usage:
      crypto-tx -G [-json]
      crypto-tx -E [-k privateKey] -p publicKeyTo -d originaltext [-iv value] [-json]
      crypto-tx -D -k privateKey -p ephemPublicKey -d ciphertext [-iv value]
    Options:
      -E   cmd encryptECIES [no]
      -D   cmd decryptECIES [no]
      -G   cmd gen private and public keys [no]
      -k   privateKey hex
      -p   publicKey hex
      -d   encrypt or decrypt data
      -iv  IV 16 bytes hex
      -json convert json [no]
    :param public_key: 公钥
    :param original_text: 需要加密的字符串
    :param iv: 向量，可以缺省
    :return: (ciphertext, ephemPublicKey, iv, mac)
    """
    cmd = 'crypto-tx -E -p {public_key} -d {original_text} -json'.format(public_key=public_key, original_text=original_text)
    if iv is not None:
        cmd = ''.join([cmd, ' -iv {}'.format(iv)])
    args = shlex.split(cmd)
    return_json = subprocess.check_output(args, shell=False)
    return return_json


def decrypt_ecies(private_key, ephemPublicKey, ciphertext, iv=None):
    """
    ECIES 方式 解码
    crypto-tx -h
    Usage:
      crypto-tx -G [-json]
      crypto-tx -E [-k privateKey] -p publicKeyTo -d originaltext [-iv value] [-json]
      crypto-tx -D -k privateKey -p ephemPublicKey -d ciphertext [-iv value]
    Options:
      -E   cmd encryptECIES [no]
      -D   cmd decryptECIES [no]
      -G   cmd gen private and public keys [no]
      -k   privateKey hex
      -p   publicKey hex
      -d   encrypt or decrypt data
      -iv  IV 16 bytes hex
      -json convert json [no]
    :param private_key: 解密者的私钥
    :param ephemPublicKey: 加密者的公钥
    :param ciphertext: 密文
    :param iv: 加密向量
    :return: 解密后的数据
    """
    cmd = 'crypto-tx -D -k {private_key} -p {ephemPublicKey} -d {ciphertext} -iv {iv} '.format(private_key=private_key,
                                                                                             ephemPublicKey=ephemPublicKey,
                                                                                             ciphertext=ciphertext,
                                                                                             iv=iv)
    print(cmd)
    args = shlex.split(cmd)
    original_text = subprocess.check_output(args, shell=False)
    # TODO: 通过获得命令返回的状态来判断是否成功，目前crypto-tx不支持
    # original_text, tf = subprocess.getstatusoutput(cmd)
    return original_text.strip()


def check_ecies(private_key, ephem_public_key, ciphertext, verified_text, iv=None):
    """
    验证解码后的字符串是否相等
    :param private_key: 解密人的私钥
    :param ephem_public_key: 加密这个字符串的人的公钥 （使用私钥加密，必须把他私钥对应的公钥也传递过来）
    :param ciphertext: 加密后的字符串
    :param verified_text: 需要验证的字符串
    :param iv: 向量
    :return:
    """
    obj = decrypt_ecies(private_key=private_key, ephemPublicKey=ephem_public_key, ciphertext=ciphertext, iv=iv).strip()
    no_0x_bytes = obj.decode().lstrip('0x')
    return_str = bytes.fromhex(no_0x_bytes).decode()
    if return_str == verified_text:
        return True
    else:
        return False


def check_ecies_in_database(private_key, ephem_public_key, ciphertext, iv=None):
    """
    在数据库中匹配是否有这个加密的数据库
    :param private_key: 解密人的私钥
    :param ephem_public_key: 加密这个字符串的人的公钥 （使用私钥加密，必须把他私钥对应的公钥也传递过来）
    :param ciphertext: 加密后的字符串
    :param iv: 向量
    :return:
    """
    original = decrypt_ecies(private_key=private_key, ephemPublicKey=ephem_public_key, ciphertext=ciphertext, iv=iv).strip()
    no_0x_bytes = original.lstrip(b'0x').decode()
    # return_str = bytes.fromhex(no_0x_bytes).decode('utf8')
    # 在数据库中查询
    soldier = get_soldier(no_0x_bytes)
    if soldier is None:
        return False, None
    else:
        return True, soldier


def get_iv(value: str) -> str:
    """
    获得value对应的iv值
    :param value:
    :return:
    """
    from pycontractsdk import keys
    value_bytes = keys.keccak(text=value)
    keccak = value_bytes.hex()[0:32]
    return ''.join(['0x',keccak])
