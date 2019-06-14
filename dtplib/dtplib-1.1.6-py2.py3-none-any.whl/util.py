import pickle
import json
import compressdir
from cryptography.fernet import Fernet
import rsa
import os
import binascii

LENSIZE = 5
LENTYPE = 1

TYPEOBJ = 0
TYPEFILE = 1

MAXSIZE = 256 ** LENSIZE - 1

def _decToAscii(dec):
    hexstr = hex(dec)[2:]
    if len(hexstr) % 2 == 1:
        hexstr = "0" + hexstr
    ascii = binascii.unhexlify(hexstr.encode())
    return ascii

def _asciiToDec(ascii):
    hexstr = binascii.hexlify(ascii)
    dec = int(hexstr, base=16)
    return dec

def _buildMessage(data, messageType=TYPEOBJ, key=None, jsonEncode=False):
    if messageType == TYPEOBJ:
        if not jsonEncode:
            data = pickle.dumps(data)
        else:
            data = json.dumps(data).encode()
    elif messageType == TYPEFILE:
        data = compressdir.compressed(data)
    if key is not None:
        data = _encrypt(key, data)
    if len(data) > MAXSIZE:
        raise RuntimeError("maximum data packet size exceeded")
    size = _decToAscii(len(data))
    size = b"\x00" * (LENSIZE - len(size)) + size
    type = str(messageType).encode("utf-8")
    return size + type + data

def _unpackMessage(data, messageType=TYPEOBJ, key=None, recvDir=None, jsonEncode=False):
    if recvDir is None:
        recvDir = os.getcwd()
    if key is not None:
        data = _decrypt(key, data)
    if messageType == TYPEOBJ:
        if not jsonEncode:
            data = pickle.loads(data)
        else:
            data = json.loads(data)
        return data
    elif messageType == TYPEFILE:
        os.makedirs(recvDir, exist_ok=True)
        path = compressdir.decompressed(data, newpath=recvDir)
        return path

def _newKeys(size=512):
    pubkey, privkey = rsa.newkeys(size)
    return pubkey, privkey

def _asymmetricEncrypt(pubkey, plaintext):
    ciphertext = rsa.encrypt(plaintext, pubkey)
    return ciphertext

def _asymmetricDecrypt(privkey, ciphertext):
    plaintext = rsa.decrypt(ciphertext, privkey)
    return plaintext

def _newKey():
    key = Fernet.generate_key()
    return key

def _encrypt(key, data):
    f = Fernet(key)
    token = f.encrypt(data)
    return token

def _decrypt(key, token):
    f = Fernet(key)
    data = f.decrypt(token)
    return data
