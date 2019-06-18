import hashlib
import json

class InputHash(object):
    def __init__(self):
        self._hash = hashlib.sha256()

    def update_with_file(self, fileobj):
        fileobj.seek(0)
        CHUNK_SIZE = 4096
        for chunk in iter(lambda: fileobj.read(CHUNK_SIZE), b""):
            self._hash.update(chunk)
        fileobj.seek(0)

    def update_with_args(self, kwargs):
        arg_str = json.dumps(kwargs, sort_keys=True)
        self._hash.update(arg_str.encode('utf-8'))

    def get_hex_digest(self):
        return self._hash.hexdigest()
