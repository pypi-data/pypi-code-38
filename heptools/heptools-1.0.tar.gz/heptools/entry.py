# -*- coding: utf-8 -*-
import argparse
from fastecdsa import curve, ecdsa, keys

def generate_secp256r1_key_pairs(save_path):
    """Generate the key pairs of secp256r1
    
    :param str save_path: The save file path of private key
    :rtype:tuple
    :return: The hex string of public key
    """
    private_key, public_key = keys.gen_keypair(curve.P256)
    keys.export_key(private_key, curve.P256, filepath=save_path)
    x = str(hex(public_key.x))[2:]
    y = str(hex(public_key.y))[2:]
    if len(x) < 64:
        x = '0' * (64 - len(x)) + x
    if len(y) < 64:
        y = '0' * (64 - len(y)) + y
    public_key =  '0x' + x + y
    return public_key

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-path', type=str)
    args = parser.parse_args()
    if not args.path:
        print("Please the file path what you want to save to.")
        exit(0)
    public_key = generate_secp256r1_key_pairs(args.path)
    print("Private key is saved to %s" % args.path)
    print("Public key is %s" % public_key)
