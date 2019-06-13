import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

from crypton.crypt_algorithms.hash.sha2 import SHA2

current_file_path = os.getcwd()


class SHA3(SHA2):
    options = SHA2.options

    def __init__(self, bits=224):
        super().__init__(bits=bits)

    def get_algorithm(self):
        if self.bits == 224:
            return hashes.SHA3_224()
        elif self.bits == 256:
            return hashes.SHA3_256()
        elif self.bits == 384:
            return hashes.SHA3_384()
        elif self.bits == 521:
            return hashes.SHA3_512()

    def _digest(self, data):
        hash_algorithm = self.get_algorithm()
        digest = hashes.Hash(hash_algorithm,
                             backend=default_backend())
        digest.update(data)

        return digest.finalize()

    def file_digest(self, file_path=''):
        with open(file_path, 'rb') as file_to_digest:
            data = file_to_digest.read()

        digest = self._digest(data=data)

        if file_path:
            open(file_path.split('.')[0] + '.hash', 'wb').write(digest)
        else:
            open(current_file_path.split('.')[0] + '.hash', 'wb').write(digest)
