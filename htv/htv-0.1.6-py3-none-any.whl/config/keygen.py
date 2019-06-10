# System imports
import base64
import os
# Encryption utilities imports
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
#Utilities imports
from htvalidator.os_utility.miscellanea import printout
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

home = os.environ['HOME']


def keygen():
    # It gets the private encryption key in the form of a string
    encryption_key = "parmigianaalforno"
    # Convert to type bytes
    key = encryption_key.encode()
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    # Can only use kdf once
    e_key = base64.urlsafe_b64encode(kdf.derive(key))

    # It saves the encryption key for the auth_config file
    file = open('{}/htv/key.key'.format(home), 'wb')
    file.write(e_key)
    file.close()
    return e_key

