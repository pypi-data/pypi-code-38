from akeyless.crypto import CryptoAlgorithm
from akeyless.crypto.aes.gcm import GCMHandler
from akeyless.crypto.utils import AkeylessCiphertext


def encrypt(alg, key, key_version, derivations_data, plaintext, associated_data=b""):
    # type: (CryptoAlgorithm, bytes, int, list, bytes, bytes) -> AkeylessCiphertext
    switcher = {
        CryptoAlgorithm.AES_128_GCM: encrypt_gcm,
        CryptoAlgorithm.AES_256_GCM: encrypt_gcm,
    }
    encryptor = switcher.get(alg, lambda: "Unsupported algorithm")
    return encryptor(alg, key, key_version, derivations_data, plaintext, associated_data)


def decrypt(alg, key, cipher, associated_data=b""):
    # type: (CryptoAlgorithm, bytes, AkeylessCiphertext, bytes) -> bytes
    switcher = {
        CryptoAlgorithm.AES_128_GCM: decrypt_gcm,
        CryptoAlgorithm.AES_256_GCM: decrypt_gcm,
    }
    decryptor = switcher.get(alg, lambda: "Unsupported algorithm")
    return decryptor(key, cipher, associated_data)


def encrypt_gcm(alg, key, key_version, derivations_data, plaintext, associated_data=b""):
    # type: (CryptoAlgorithm, bytes, int, list, bytes, bytes) -> AkeylessCiphertext
    gcm_handler = GCMHandler(key)
    cipher = gcm_handler.encrypt(plaintext, associated_data)
    return AkeylessCiphertext().serialize(alg, key_version, derivations_data, cipher)


def decrypt_gcm(key, cipher, associated_data=b""):
    # type: (bytes, AkeylessCiphertext, bytes) -> bytes
    gcm_handler = GCMHandler(key)
    return gcm_handler.decrypt(cipher.encrypted_data, associated_data)
