"""根据 keystore 和 password 得到私钥"""
import json

import prs_utility


keystore = {
    "address": "758ea2601697fbd3ba6eb6774ed70b6c4cdb0ef9",
    "crypto": {
        "cipher": "aes-128-ctr",
        "ciphertext": "92af6f6710eba271eae5ac7fec72c70d9f49215e7880a0c45d4c53e56bd7ea59",
        "cipherparams": {
            "iv": "13ddf95d970e924c97e4dcd29ba96520"
        },
        "mac": "b9d81d78f067334ee922fb2863e32c14cbc46e479eeb0acc11fb31e39256004e",
        "kdf": "pbkdf2",
        "kdfparams": {
            "c": 262144,
            "dklen": 32,
            "prf": "hmac-sha256",
            "salt": "79f90bb603491573e40a79fe356b88d0c7869852e43c2bbaabed44578a82bbfa"
        }
    },
    "id": "93028e51-a2a4-4514-bc1a-94b089445f35",
    "version": 3
}
password = '123123'


private_key = prs_utility.recover_private_key(
    json.dumps(keystore), password
)
print('private_key:', private_key)
