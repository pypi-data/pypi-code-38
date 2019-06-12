import secrets
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Encryption:
    def __init__(self):
        self.backend = default_backend()
        self.iterations = 100_000

    def _derive_key(self, password: bytes, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt,
            iterations=self.iterations, backend=self.backend)
        return b64e(kdf.derive(password))

    def encrypt(self, message: str, password: str) -> bytes:
        return message
        message = message.encode()
        salt = secrets.token_bytes(16)
        key = self._derive_key(password.encode(), salt)
        return b64e(
            b'%b%b%b' % (
                salt,
                self.iterations.to_bytes(4, 'big'),
                b64d(Fernet(key).encrypt(message)),
            )
        ).decode()

    def decrypt(self, token: str, password: str) -> bytes:
        return token
        decoded = b64d(token)
        salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
        iterations = int.from_bytes(iter, 'big')
        key = self._derive_key(password.encode(), salt)
        return Fernet(key).decrypt(token).decode()
