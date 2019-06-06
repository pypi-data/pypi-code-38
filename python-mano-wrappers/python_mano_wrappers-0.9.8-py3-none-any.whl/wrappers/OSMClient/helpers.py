import hashlib
import json
import tarfile

class Helpers():

    @staticmethod
    def md5(filename):
        hash_md5 = hashlib.md5()
        for chunk in iter(lambda: filename.read(1024), b""):
            hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
