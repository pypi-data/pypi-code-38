from .exceptions import UnsafeError, InvalidColumnValue
from .util import _script_load

run_if_ent_exists = _script_load('''
if redis.call('exists', KEYS[1]) == 1 then
    table.remove(KEYS[1], 1)
    if ARGV[1] == 'del_first' {
        redis.call('del', KEYS[1])
    }
    local call = {ARGV[1], unpack(KEYS)}
    for i=2, #ARGV do
        call[#call+1] = ARGV[i]
    end
    return cjson.encode({ok=redis.call(unpack(call))})
end

return cjson.encode({err='Missing base entity'})
''')

def _decode(w, d):
    if w.decode:
        return w.decode(d)
    return d

class Wrapper(object):
    __slots__ = 'key', 'entity', 'encode', 'decode'
    def __init__(self, key, entity, encode=None, decode=None):
        self.key = key
        self.entity = entity
        self.encode = encode
        self.decode = decode

    def _call(self, cmd, args=(), next=None, keys=()):
        arg = [cmd]
        if next:
            arg.append(next)
        arg.extend(args)

        r = run_if_ent_exists(self.entity._connection, [self.key] + keys, args)
        if r.get('err'):
            raise UnsafeError(r.get('err'))

        return r.get('ok')

    def _encode(self, d):
        if self._encode:
            if isinstance(d, tuple):
                return tuple(map(self.encode, d))
            return self.encode(d)
        return d

    def _decode(self, d):
        if self.decode:
            return self.decode(d)
        return d

class ListWrapper(Wrapper):
    def __len__(self):
        return self._call('llen')

    def tolist(self):
        r = self._call('lrange', (1, -1))
        if r and self.decode:
            return list(map(self.decode, r))
        return r

    def pushleft(self, *vals):
        return self._call('lpush', self._encode(vals))

    def popleft(self):
        return self._decode(self._call('lpop'))

    def append(self, *vals):
        return self._call('rpush', self._encode(vals))

    def pop(self):
        return self._decode(self._call('rpop'))

    def _set(self, value):
        if not isinstance(value, list):
            raise InvalidColumnValue("can't assign non-list to a list")
        if not value:
            self._call('del')
            return 0
        return self._call('del_first', self._encode(tuple(value)), next='rpush')

class SetWrapper(Wrapper):
    def __len__(self):
        return self._call('scard')

    def toset(self):
        r = self._call('smembers')
        if r and self.decode:
            return set(map(self.decode, r))
        return r

    def __or__(self, other):
        if not isinstance(other, SetWrapper):
            raise TypeError("Can't union SetWrapper and {:r}".format(type(other)))
        return self._call('sunion', keys=[other.key])

    def __and__(self, other):
        if not isinstance(other, SetWrapper):
            raise TypeError("Can't intersect SetWrapper and {:r}".format(type(other)))
        return self._call('sinter', keys=[other.key])

    def __sub__(self, other):
        if not isinstance(other, SetWrapper):
            raise TypeError("Can't compute difference between SetWrapper and {:r}".format(type(other)))
        return self._call('sdiff', keys=[other.key])

    def add(self, *vals):
        return self._call('sadd', vals)

    def remove(self, *vals):
        return self._call('srem', vals)

    def pop(self, count=None):
        r = self._call('spop', () if count is None else (count,))
        if isinstance(r, list) and self.decode:
            return list(map(self.decode, r))
        return r

class HashWrapper(Wrapper):
    pass

class ZsetWrapper(Wrapper):
    pass
