# System imports
import base64
import os
# Encryption utilities imports
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
#Utilities imports
from os_utility.miscellanea import printout
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# It gets the private encryption key in the form of a string
printout("Enter a pass phrase for the encryption, you don't need to remember it in the future: \n", CYAN)
encryption_key = input()
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
file = open('./config/key.key', 'wb')
file.write(e_key)
file.close()
