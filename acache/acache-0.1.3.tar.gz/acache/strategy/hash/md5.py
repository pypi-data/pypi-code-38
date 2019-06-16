import hashlib


class MD5:

    cache = None

    def set(self, value, *args, **kwargs):
        hashstr = _hashargs(*args, **kwargs)
        self.cache[hashstr] = value
        return hashstr

    def get(self, *args, **kwargs):
        hashstr = _hashargs(*args, **kwargs)
        if hashstr in self.cache:
            return hashstr, self.cache[hashstr]
        raise KeyError('Could not find cache for key: {}'.format(hashstr))


def _hashargs(*args, **kwargs):
    arghash = ''.join(map(str, args))
    kwghash = ''.join('{}{}'.format(*x) for x in kwargs.items())
    hashstr = hashlib.md5(bytes(arghash + kwghash, 'utf-8')).hexdigest()
    return hashstr
