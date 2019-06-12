# encoding: utf-8

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fdutil.path_tools import ensure_path_exists
from .config import get_file_path
from .constants import (DEFAULT_BITS,
                        DEFAULT_PASSPHRASE,
                        SSL_DATA_DIR,
                        SSLConstant)


def write_private_key_file(key,
                           filename,
                           filepath=SSL_DATA_DIR,
                           passphrase=DEFAULT_PASSPHRASE):

    """ Write the key to the specified file. """

    ensure_path_exists(filepath)

    pth = get_file_path(fn=filename,
                        ext=SSLConstant.private_key,
                        pth=filepath)

    with open(pth, 'wb') as key_f:
        key_f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
                if passphrase is None
                else serialization.BestAvailableEncryption(passphrase),
            )
        )

    return pth


def write_public_key_file(key,
                          filename,
                          filepath=SSL_DATA_DIR):

    """ Write the key to the specified file. """

    ensure_path_exists(filepath)

    pth = get_file_path(fn=filename,
                        ext=SSLConstant.public_key,
                        pth=filepath)

    with open(pth, 'wb') as key_f:
        key_f.write(
            key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    return pth


def generate_key(filename,
                 filepath=SSL_DATA_DIR,
                 bits=DEFAULT_BITS,
                 passphrase=DEFAULT_PASSPHRASE):

    """ Generate RSA Private Key.

    :param filename:    Filename for the key files.
    :param filepath:    Path to save the key files, default=SSL_DATA_DIR.
    :param bits:        Key length in bits, default is 2048.
    :param passphrase:  The pass phrase to use to secure the private key when writing to file.
    :return:            Private key object.
    """

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits,
        backend=default_backend()
    )

    private_key_path = write_private_key_file(key=key,
                                              passphrase=passphrase,
                                              filepath=filepath,
                                              filename=filename)

    public_key_path = write_public_key_file(key=key,
                                            filepath=filepath,
                                            filename=filename)

    return key, private_key_path, public_key_path
