import hashlib
from functools import partial

from six import BytesIO


def hash_file(file, block_size=65536):
    hash_ = hashlib.md5()
    for buf in iter(partial(file.read, block_size), b''):
        hash_.update(buf)

    return hash_.hexdigest()


def accept_file(self, file_):
    if isinstance(file_, str):
        if '://' in file_:
            # URL supplied
            response = self.requests.get(url=file_)
            file_io = BytesIO(response.content)
        else:
            file_io = open(file_, 'rb')
    else:
        file_io = file_
        assert hasattr(file_io, 'read'), 'Non file like object was supplied'

    return file_io
