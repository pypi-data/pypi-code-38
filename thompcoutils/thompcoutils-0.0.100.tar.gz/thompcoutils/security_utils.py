import base64
from Crypto.Cipher import AES
from Crypto import Random
import argparse
import hashlib


class Security:
    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encode(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decode(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[16:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


def main():
    parser = argparse.ArgumentParser(description="Encrypts/Decrypts a string",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--key",
                        required=True,
                        help="AES key to use for encryption")
    parser.add_argument("--value",
                        required=True,
                        help="value to encrypt or decrypt")
    parser.add_argument("--dir",
                        default="encrypt",
                        choices=["encrypt", "decrypt"],
                        help="Direction of encryption")
    args = parser.parse_args()
    sec = Security(args.key)
    if args.dir == "encrypt":
        print(sec.encode(args.value))
    else:
        print(sec.decode(args.value))


if __name__ == '__main__':
    main()
