import sys
import numbers
import struct

try:
    basestring
except NameError:
    basestring = str

if isinstance(chr(123), bytes):
    _ord = ord
else:
    _ord = lambda x: x

class Float(object):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return self.value == other.value

    def __repr__(self):
        return 'Float(' + repr(self.value) + ')'

    def __preserve_on__(self, encoder):
        encoder.leadbyte(0, 0, 2)
        encoder.buffer.extend(struct.pack('>f', self.value))

class Symbol(object):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return '#' + self.name

    def __preserve_on__(self, encoder):
        bs = self.name.encode('utf-8')
        encoder.header(1, 3, len(bs))
        encoder.buffer.extend(bs)

class Record(object):
    def __init__(self, key, fields):
        self.key = key
        self.fields = tuple(fields)
        self.__hash = None

    def __eq__(self, other):
        return isinstance(other, Record) and (self.key, self.fields) == (other.key, other.fields)

    def __hash__(self):
        if self.__hash is None:
            self.__hash = hash((self.key, self.fields))
        return self.__hash

    def __repr__(self):
        return str(self.key) + '(' + ', '.join((repr(f) for f in self.fields)) + ')'

    def __preserve_on__(self, encoder):
        try:
            index = encoder.shortForms.index(self.key)
        except ValueError:
            index = None
        if index is None:
            encoder.header(2, 3, len(self.fields) + 1)
            encoder.append(self.key)
        else:
            encoder.header(2, index, len(self.fields))
        for f in self.fields:
            encoder.append(f)

    def __getitem__(self, index):
        return self.fields[index]

    @staticmethod
    def makeConstructor(labelSymbolText, fieldNames):
        return Record.makeBasicConstructor(Symbol(labelSymbolText), fieldNames)

    @staticmethod
    def makeBasicConstructor(label, fieldNames):
        if type(fieldNames) == str:
            fieldNames = fieldNames.split()
        arity = len(fieldNames)
        def ctor(*fields):
            if len(fields) != arity:
                raise Exception("Record: cannot instantiate %r expecting %d fields with %d fields"%(
                    label,
                    arity,
                    len(fields)))
            return Record(label, fields)
        ctor.constructorInfo = RecordConstructorInfo(label, arity)
        ctor.isClassOf = lambda v: \
                         isinstance(v, Record) and v.key == label and len(v.fields) == arity
        def ensureClassOf(v):
            if not ctor.isClassOf(v):
                raise TypeError("Record: expected %r/%d, got %r" % (label, arity, v))
            return v
        ctor.ensureClassOf = ensureClassOf
        for fieldIndex in range(len(fieldNames)):
            fieldName = fieldNames[fieldIndex]
            # Stupid python scoping bites again
            def getter(fieldIndex):
                return lambda v: ensureClassOf(v)[fieldIndex]
            setattr(ctor, '_' + fieldName, getter(fieldIndex))
        return ctor

class RecordConstructorInfo(object):
    def __init__(self, key, arity):
        self.key = key
        self.arity = arity

    def __eq__(self, other):
        return isinstance(other, RecordConstructorInfo) and \
            (self.key, self.arity) == (other.key, other.arity)

    def __hash__(self):
        if self.__hash is None:
            self.__hash = hash((self.key, self.arity))
        return self.__hash

    def __repr__(self):
        return str(self.key) + '/' + str(self.arity)

# Blub blub blub
class ImmutableDict(dict):
    def __init__(self, *args, **kwargs):
        if hasattr(self, '__hash'): raise TypeError('Immutable')
        super(ImmutableDict, self).__init__(*args, **kwargs)
        self.__hash = None

    def __delitem__(self, key): raise TypeError('Immutable')
    def __setitem__(self, key, val): raise TypeError('Immutable')
    def clear(self): raise TypeError('Immutable')
    def pop(self, k, d=None): raise TypeError('Immutable')
    def popitem(self): raise TypeError('Immutable')
    def setdefault(self, k, d=None): raise TypeError('Immutable')
    def update(self, e, **f): raise TypeError('Immutable')

    def __hash__(self):
        if self.__hash is None:
            h = 0
            for k in self:
                h = ((h << 5) ^ (hash(k) << 2) ^ hash(self[k])) & sys.maxsize
            self.__hash = h
        return self.__hash

    @staticmethod
    def from_kvs(kvs):
        i = iter(kvs)
        result = ImmutableDict()
        result_proxy = super(ImmutableDict, result)
        try:
            while True:
                k = next(i)
                v = next(i)
                result_proxy.__setitem__(k, v)
        except StopIteration:
            pass
        return result

def dict_kvs(d):
    for k in d:
        yield k
        yield d[k]

class DecodeError(ValueError): pass
class EncodeError(ValueError): pass
class ShortPacket(DecodeError): pass

class Codec(object):
    def __init__(self):
        self.shortForms = [Symbol(u'discard'), Symbol(u'capture'), Symbol(u'observe')]

    def set_shortform(self, index, v):
        if index >= 0 and index < 3:
            self.shortForms[index] = v
        else:
            raise ValueError('Invalid short form index %r' % (index,))

class Stream(object):
    def __init__(self, iterator):
        self._iterator = iterator

    def __preserve_on__(self, encoder):
        arg = (self.major << 2) | self.minor
        encoder.leadbyte(0, 2, arg)
        self._emit(encoder)
        encoder.leadbyte(0, 3, arg)

    def _emit(self, encoder):
        raise NotImplementedError('Should be implemented in subclasses')

class ValueStream(Stream):
    major = 3
    def _emit(self, encoder):
        for v in self._iterator:
            encoder.append(v)

class SequenceStream(ValueStream):
    minor = 0

class SetStream(ValueStream):
    minor = 1

class DictStream(ValueStream):
    minor = 2
    def _emit(self, encoder):
        for (k, v) in self._iterator:
            encoder.append(k)
            encoder.append(v)

class BinaryStream(Stream):
    major = 1
    minor = 2
    def _emit(self, encoder):
        for chunk in self._iterator:
            if not isinstance(chunk, bytes):
                raise EncodeError('Illegal chunk in BinaryStream %r' % (chunk,))
            encoder.append(chunk)

class StringStream(BinaryStream):
    minor = 1

class SymbolStream(BinaryStream):
    minor = 3

class Decoder(Codec):
    def __init__(self, packet=b''):
        super(Decoder, self).__init__()
        self.packet = packet
        self.index = 0

    def extend(self, data):
        self.packet = self.packet[self.index:] + data
        self.index = 0

    def nextbyte(self):
        if self.index >= len(self.packet):
            raise ShortPacket('Short packet')
        self.index = self.index + 1
        return _ord(self.packet[self.index - 1])

    def nextbytes(self, n):
        start = self.index
        end = start + n
        if end > len(self.packet):
            raise ShortPacket('Short packet')
        self.index = end
        return self.packet[start : end]

    def wirelength(self, arg):
        if arg < 15:
            return arg
        return self.varint()

    def varint(self):
        v = self.nextbyte()
        if v < 128:
            return v
        else:
            return self.varint() * 128 + (v - 128)

    def nextvalues(self, n):
        result = []
        for i in range(n):
            result.append(self.next())
        return result

    def nextop(self):
        b = self.nextbyte()
        major = b >> 6
        minor = (b >> 4) & 3
        arg = b & 15
        return (major, minor, arg)

    def peekend(self, arg):
        matched = (self.nextop() == (0, 3, arg))
        if not matched:
            self.index = self.index - 1
        return matched

    def binarystream(self, arg, minor):
        result = []
        while not self.peekend(arg):
            chunk = self.next()
            if isinstance(chunk, bytes):
                result.append(chunk)
            else:
                raise DecodeError('Unexpected non-binary chunk')
        return self.decodebinary(minor, b''.join(result))

    def valuestream(self, arg, minor, decoder):
        result = []
        while not self.peekend(arg):
            result.append(self.next())
        return decoder(minor, result)

    def decodeint(self, bs):
        if len(bs) == 0: return 0
        acc = _ord(bs[0])
        if acc & 0x80: acc = acc - 256
        for b in bs[1:]:
            acc = (acc << 8) | _ord(b)
        return acc

    def decodebinary(self, minor, bs):
        if minor == 0: return self.decodeint(bs)
        if minor == 1: return bs.decode('utf-8')
        if minor == 2: return bs
        if minor == 3: return Symbol(bs.decode('utf-8'))

    def decoderecord(self, minor, vs):
        if minor == 3:
            if not vs: raise DecodeError('Too few elements in encoded record')
            return Record(vs[0], vs[1:])
        else:
            return Record(self.shortForms[minor], vs)

    def decodecollection(self, minor, vs):
        if minor == 0: return tuple(vs)
        if minor == 1: return frozenset(vs)
        if minor == 2: return ImmutableDict.from_kvs(vs)
        if minor == 3: raise DecodeError('Invalid collection type')

    def next(self):
        (major, minor, arg) = self.nextop()
        if major == 0:
            if minor == 0:
                if arg == 0: return False
                if arg == 1: return True
                if arg == 2: return Float(struct.unpack('>f', self.nextbytes(4))[0])
                if arg == 3: return struct.unpack('>d', self.nextbytes(8))[0]
                raise DecodeError('Invalid format A encoding')
            elif minor == 1:
                return arg - 16 if arg > 12 else arg
            elif minor == 2:
                t = arg >> 2
                n = arg & 3
                if t == 0: raise DecodeError('Invalid format C start byte')
                if t == 1: return self.binarystream(arg, n)
                if t == 2: return self.valuestream(arg, n, self.decoderecord)
                if t == 3: return self.valuestream(arg, n, self.decodecollection)
            else: # minor == 3
                raise DecodeError('Unexpected format C end byte')
        elif major == 1:
            return self.decodebinary(minor, self.nextbytes(self.wirelength(arg)))
        elif major == 2:
            return self.decoderecord(minor, self.nextvalues(self.wirelength(arg)))
        else: # major == 3
            return self.decodecollection(minor, self.nextvalues(self.wirelength(arg)))

    def try_next(self):
        start = self.index
        try:
            return self.next()
        except ShortPacket:
            self.index = start
            return None

class Encoder(Codec):
    def __init__(self):
        super(Encoder, self).__init__()
        self.buffer = bytearray()

    def contents(self):
        return bytes(self.buffer)

    def varint(self, v):
        if v < 128:
            self.buffer.append(v)
        else:
            self.buffer.append((v % 128) + 128)
            self.varint(v // 128)

    def leadbyte(self, major, minor, arg):
        self.buffer.append(((major & 3) << 6) | ((minor & 3) << 4) | (arg & 15))

    def header(self, major, minor, wirelength):
        if wirelength < 15:
            self.leadbyte(major, minor, wirelength)
        else:
            self.leadbyte(major, minor, 15)
            self.varint(wirelength)

    def encodeint(self, v):
        bitcount = (~v if v < 0 else v).bit_length() + 1
        bytecount = (bitcount + 7) // 8
        self.header(1, 0, bytecount)
        def enc(n,x):
            if n > 0:
                enc(n-1, x >> 8)
                self.buffer.append(x & 255)
        enc(bytecount, v)

    def encodecollection(self, minor, items):
        self.header(3, minor, len(items))
        for i in items: self.append(i)

    def encodestream(self, t, n, items):
        tn = ((t & 3) << 2) | (n & 3)
        self.header(0, 2, tn)
        for i in items: self.append(i)
        self.header(0, 3, tn)

    def append(self, v):
        if hasattr(v, '__preserve_on__'):
            v.__preserve_on__(self)
        elif v is False:
            self.leadbyte(0, 0, 0)
        elif v is True:
            self.leadbyte(0, 0, 1)
        elif isinstance(v, float):
            self.leadbyte(0, 0, 3)
            self.buffer.extend(struct.pack('>d', v))
        elif isinstance(v, numbers.Number):
            if v >= -3 and v <= 12:
                self.leadbyte(0, 1, v if v >= 0 else v + 16)
            else:
                self.encodeint(v)
        elif isinstance(v, bytes):
            self.header(1, 2, len(v))
            self.buffer.extend(v)
        elif isinstance(v, basestring):
            bs = v.encode('utf-8')
            self.header(1, 1, len(bs))
            self.buffer.extend(bs)
        elif isinstance(v, list):
            self.encodecollection(0, v)
        elif isinstance(v, tuple):
            self.encodecollection(0, v)
        elif isinstance(v, set):
            self.encodecollection(1, v)
        elif isinstance(v, frozenset):
            self.encodecollection(1, v)
        elif isinstance(v, dict):
            self.encodecollection(2, list(dict_kvs(v)))
        else:
            try:
                i = iter(v)
            except TypeError:
                raise EncodeError('Cannot encode %r' % (v,))
            self.encodestream(3, 0, i)
