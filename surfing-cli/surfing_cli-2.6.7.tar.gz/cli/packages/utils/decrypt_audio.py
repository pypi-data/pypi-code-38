import os
import sys
from Crypto.Cipher import AES

# 密钥
key = "MZCtLr2tQ37v9x8rCeeprs8V5RpPxd5K"


def decrypt_file(encrypt_audio_file):
    """
    解密被加密的文件,解密的文件是取消解密文件后缀.enc后的文件
    :param encrypt_audio_file: 被加密的音频文件
    :return:
    """
    with open(encrypt_audio_file, 'rb') as inputFile:
        with open(encrypt_audio_file[:encrypt_audio_file.rfind(".")], 'wb') as outputFile:
            cipher = AES.new(key, AES.MODE_ECB)
            cipher_text = inputFile.read()
            de_text = cipher.decrypt(cipher_text)
            de_text = de_text.rstrip(b'\x04')
            outputFile.write(de_text)
    try:
        os.remove(encrypt_audio_file)
    except Exception as e:
        print("Exception: ", e)


def decrypt_folder(src):
    """
    给包列表目录，挨个包进行处理
    :param src:
    :return:
    """
    for package in os.listdir(src):
        src_package_path = os.path.join(src, package)
        if os.path.isdir(src_package_path):
            dst_package_path = os.path.join(src, package)
            for f in os.listdir(src_package_path):
                if f.endswith('.wav.enc'):
                    enc_path = os.path.join(src_package_path, f)
                    wav_path = os.path.join(dst_package_path, f[:-4])
                    decrypt_file(enc_path, wav_path, key)
