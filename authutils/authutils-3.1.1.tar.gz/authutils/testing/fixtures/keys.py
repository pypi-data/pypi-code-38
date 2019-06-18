from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import pytest


def _new_hazmat_rsa_private_key():
    """
    Return:
        cryptography.hazmat.backends.openssl.rsa._RSAPrivateKey
    """
    return rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )


@pytest.fixture(scope="session")
def _hazmat_rsa_private_key():
    """
    Return:
        cryptography.hazmat.backends.openssl.rsa._RSAPrivateKey
    """
    return _new_hazmat_rsa_private_key()


@pytest.fixture(scope="session")
def _hazmat_rsa_private_key_2():
    """
    Make a different private key than the first one.

    Return:
        cryptography.hazmat.backends.openssl.rsa._RSAPrivateKey
    """
    return _new_hazmat_rsa_private_key()


@pytest.fixture(scope="session")
def rsa_private_key(_hazmat_rsa_private_key):
    """
    Return a string of an RSA private key in PEM format.

    Args:
        _hazmat_rsa_private_key: fixture

    Return:
        str: RSA private key

    Example:

        .. code-block:: python

            \"\"\"
            -----BEGIN RSA PRIVATE KEY-----
            VbX7OiPS...
            ...
            ...ZHxIKy2+
            -----END RSA PRIVATE KEY-----
            \"\"\"
    """
    return _hazmat_rsa_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )


@pytest.fixture(scope="session")
def rsa_private_key_2(_hazmat_rsa_private_key_2):
    """
    Return a (second, different) string of an RSA private key in PEM format.

    Args:
        _hazmat_rsa_private_key: fixture

    Return:
        str: RSA private key

    Example:

        .. code-block:: python

            \"\"\"
            -----BEGIN RSA PRIVATE KEY-----
            VbX7OiPS...
            ...
            ...ZHxIKy2+
            -----END RSA PRIVATE KEY-----
            \"\"\"
    """
    return _hazmat_rsa_private_key_2.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )


@pytest.fixture(scope="session")
def rsa_public_key(_hazmat_rsa_private_key):
    """
    Return a string of an RSA public key in PEM format. The key returned from
    this function matches the private key returned by ``rsa_private_key``.

    Args:
        _hazmat_rsa_private_key: fixture

    Return:
        str: RSA public key (including line breaks)

    Example:

        .. code-block:: python

            \"\"\"
            -----BEGIN PUBLIC KEY-----
            MIIBIjAN...
            ...
            ...BCgKCAQE
            -----END PUBLIC KEY-----
            \"\"\"
    """
    return _hazmat_rsa_private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


@pytest.fixture(scope="session")
def rsa_public_key_2(_hazmat_rsa_private_key_2):
    """
    Return a string of a (second, different) RSA public key in PEM format. The
    key returned from this function matches the private key returned by
    ``rsa_private_key_2``.

    Args:
        _hazmat_rsa_private_key: fixture

    Return:
        str: RSA public key (including line breaks)

    Example:

        .. code-block:: python

            \"\"\"
            -----BEGIN PUBLIC KEY-----
            MIIBIjAN...
            ...
            ...BCgKCAQE
            -----END PUBLIC KEY-----
            \"\"\"
    """
    return _hazmat_rsa_private_key_2.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
