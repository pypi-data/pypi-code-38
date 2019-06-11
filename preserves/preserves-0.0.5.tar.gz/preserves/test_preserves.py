from .preserves import *
import unittest

if isinstance(chr(123), bytes):
    def _byte(x):
        return chr(x)
    def _hex(x):
        return x.encode('hex')
else:
    def _byte(x):
        return bytes([x])
    def _hex(x):
        return x.hex()

def _buf(*args):
    result = []
    for chunk in args:
        if isinstance(chunk, bytes):
            result.append(chunk)
        elif isinstance(chunk, basestring):
            result.append(chunk.encode('utf-8'))
        elif isinstance(chunk, numbers.Number):
            result.append(_byte(chunk))
        else:
            raise Exception('Invalid chunk in _buf %r' % (chunk,))
    result = b''.join(result)
    return result

def _varint(v):
    e = Encoder()
    e.varint(v)
    return e.contents()

def _d(bs):
    d = Decoder(bs)
    return d.next()

_all_encoded = set()

def tearDownModule():
    print()
    for bs in sorted(_all_encoded):
        print(_hex(bs))

def _e(v):
    e = Encoder()
    e.append(v)
    bs = e.contents()
    _all_encoded.add(bs)
    return bs

def _R(k, *args):
    return Record(Symbol(k), args)

class CodecTests(unittest.TestCase):
    def _roundtrip(self, forward, expected, back=None, nondeterministic=False):
        if back is None: back = forward
        self.assertEqual(_d(_e(forward)), back)
        self.assertEqual(_d(_e(back)), back)
        self.assertEqual(_d(expected), back)
        if not nondeterministic:
            actual = _e(forward)
            self.assertEqual(actual, expected, '%s != %s' % (_hex(actual), _hex(expected)))

    def test_decode_varint(self):
        with self.assertRaises(DecodeError):
            Decoder(_buf()).varint()
        self.assertEqual(Decoder(_buf(0)).varint(), 0)
        self.assertEqual(Decoder(_buf(10)).varint(), 10)
        self.assertEqual(Decoder(_buf(100)).varint(), 100)
        self.assertEqual(Decoder(_buf(200, 1)).varint(), 200)
        self.assertEqual(Decoder(_buf(0b10101100, 0b00000010)).varint(), 300)
        self.assertEqual(Decoder(_buf(128, 148, 235, 220, 3)).varint(), 1000000000)

    def test_encode_varint(self):
        self.assertEqual(_varint(0), _buf(0))
        self.assertEqual(_varint(10), _buf(10))
        self.assertEqual(_varint(100), _buf(100))
        self.assertEqual(_varint(200), _buf(200, 1))
        self.assertEqual(_varint(300), _buf(0b10101100, 0b00000010))
        self.assertEqual(_varint(1000000000), _buf(128, 148, 235, 220, 3))

    def test_shorts(self):
        self._roundtrip(_R('capture', _R('discard')), _buf(0x91, 0x80))
        self._roundtrip(_R('observe', _R('speak', _R('discard'), _R('capture', _R('discard')))),
                        _buf(0xA1, 0xB3, 0x75, "speak", 0x80, 0x91, 0x80))

    def test_simple_seq(self):
        self._roundtrip([1,2,3,4], _buf(0xC4, 0x11, 0x12, 0x13, 0x14), back=(1,2,3,4))
        self._roundtrip(SequenceStream([1,2,3,4]), _buf(0x2C, 0x11, 0x12, 0x13, 0x14, 0x3C),
                        back=(1,2,3,4))
        self._roundtrip((-2,-1,0,1), _buf(0xC4, 0x1E, 0x1F, 0x10, 0x11))

    def test_str(self):
        self._roundtrip(u'hello', _buf(0x55, 'hello'))
        self._roundtrip(StringStream([b'he', b'llo']), _buf(0x25, 0x62, 'he', 0x63, 'llo', 0x35),
                        back=u'hello')
        self._roundtrip(StringStream([b'he', b'll', b'', b'',  b'o']),
                        _buf(0x25, 0x62, 'he', 0x62, 'll', 0x60, 0x60, 0x61, 'o', 0x35),
                        back=u'hello')
        self._roundtrip(BinaryStream([b'he', b'll', b'', b'',  b'o']),
                        _buf(0x26, 0x62, 'he', 0x62, 'll', 0x60, 0x60, 0x61, 'o', 0x36),
                        back=b'hello')
        self._roundtrip(SymbolStream([b'he', b'll', b'', b'',  b'o']),
                        _buf(0x27, 0x62, 'he', 0x62, 'll', 0x60, 0x60, 0x61, 'o', 0x37),
                        back=Symbol(u'hello'))

    def test_mixed1(self):
        self._roundtrip((u'hello', Symbol(u'there'), b'world', (), set(), True, False),
                        _buf(0xc7, 0x55, 'hello', 0x75, 'there', 0x65, 'world', 0xc0, 0xd0, 1, 0))

    def test_signedinteger(self):
        self._roundtrip(-257, _buf(0x42, 0xFE, 0xFF))
        self._roundtrip(-256, _buf(0x42, 0xFF, 0x00))
        self._roundtrip(-255, _buf(0x42, 0xFF, 0x01))
        self._roundtrip(-254, _buf(0x42, 0xFF, 0x02))
        self._roundtrip(-129, _buf(0x42, 0xFF, 0x7F))
        self._roundtrip(-128, _buf(0x41, 0x80))
        self._roundtrip(-127, _buf(0x41, 0x81))
        self._roundtrip(-4, _buf(0x41, 0xFC))
        self._roundtrip(-3, _buf(0x1D))
        self._roundtrip(-2, _buf(0x1E))
        self._roundtrip(-1, _buf(0x1F))
        self._roundtrip(0, _buf(0x10))
        self._roundtrip(1, _buf(0x11))
        self._roundtrip(12, _buf(0x1C))
        self._roundtrip(13, _buf(0x41, 0x0D))
        self._roundtrip(127, _buf(0x41, 0x7F))
        self._roundtrip(128, _buf(0x42, 0x00, 0x80))
        self._roundtrip(255, _buf(0x42, 0x00, 0xFF))
        self._roundtrip(256, _buf(0x42, 0x01, 0x00))
        self._roundtrip(32767, _buf(0x42, 0x7F, 0xFF))
        self._roundtrip(32768, _buf(0x43, 0x00, 0x80, 0x00))
        self._roundtrip(65535, _buf(0x43, 0x00, 0xFF, 0xFF))
        self._roundtrip(65536, _buf(0x43, 0x01, 0x00, 0x00))
        self._roundtrip(131072, _buf(0x43, 0x02, 0x00, 0x00))

    def test_floats(self):
        self._roundtrip(Float(1.0), _buf(2, 0x3f, 0x80, 0, 0))
        self._roundtrip(1.0, _buf(3, 0x3f, 0xf0, 0, 0, 0, 0, 0, 0))
        self._roundtrip(-1.202e300, _buf(3, 0xfe, 0x3c, 0xb7, 0xb7, 0x59, 0xbf, 0x04, 0x26))

    def test_badchunks(self):
        self.assertEqual(_d(_buf(0x25, 0x61, 'a', 0x35)), u'a')
        self.assertEqual(_d(_buf(0x26, 0x61, 'a', 0x36)), b'a')
        self.assertEqual(_d(_buf(0x27, 0x61, 'a', 0x37)), Symbol(u'a'))
        for a in [0x25, 0x26, 0x27]:
            for b in [0x51, 0x71]:
                with self.assertRaises(DecodeError, msg='Unexpected non-binary chunk') as cm:
                    _d(_buf(a, b, 'a', 0x10+a))

    def test_person(self):
        self._roundtrip(Record((Symbol(u'titled'), Symbol(u'person'), 2, Symbol(u'thing'), 1),
                               [
                                   101,
                                   u'Blackwell',
                                   _R(u'date', 1821, 2, 3),
                                   u'Dr'
                               ]),
                        _buf(0xB5, 0xC5, 0x76, 0x74, 0x69, 0x74, 0x6C, 0x65,
                             0x64, 0x76, 0x70, 0x65, 0x72, 0x73, 0x6F, 0x6E,
                             0x12, 0x75, 0x74, 0x68, 0x69, 0x6E, 0x67, 0x11,
                             0x41, 0x65, 0x59, 0x42, 0x6C, 0x61, 0x63, 0x6B,
                             0x77, 0x65, 0x6C, 0x6C, 0xB4, 0x74, 0x64, 0x61,
                             0x74, 0x65, 0x42, 0x07, 0x1D, 0x12, 0x13, 0x52,
                             0x44, 0x72))

    def test_dict(self):
        self._roundtrip({ Symbol(u'a'): 1,
                          u'b': True,
                          (1, 2, 3): b'c',
                          ImmutableDict({ Symbol(u'first-name'): u'Elizabeth', }):
                            { Symbol(u'surname'): u'Blackwell' } },
                        _buf(0xE8,
                             0x71, "a", 0x11,
                             0x51, "b", 0x01,
                             0xC3, 0x11, 0x12, 0x13, 0x61, "c",
                             0xE2, 0x7A, "first-name", 0x59, "Elizabeth",
                             0xE2, 0x77, "surname", 0x59, "Blackwell"),
                        nondeterministic = True)

    def test_iterator_stream(self):
        d = {u'a': 1, u'b': 2, u'c': 3}
        r = r'2c(c2516.1.){3}3c'
        if hasattr(d, 'iteritems'):
            # python 2
            bs = _e(d.iteritems())
            self.assertRegexpMatches(_hex(bs), r)
        else:
            # python 3
            bs = _e(d.items())
            self.assertRegex(_hex(bs), r)
        self.assertEqual(sorted(_d(bs)), [(u'a', 1), (u'b', 2), (u'c', 3)])

    def test_long_sequence(self):
        # Short enough to not need a varint:
        self._roundtrip((False,) * 14, _buf(0xCE, b'\x00' * 14))
        # Varint-needing:
        self._roundtrip((False,) * 15, _buf(0xCF, 0x0F, b'\x00' * 15))
        self._roundtrip((False,) * 100, _buf(0xCF, 0x64, b'\x00' * 100))
        self._roundtrip((False,) * 200, _buf(0xCF, 0xC8, 0x01, b'\x00' * 200))

    def test_format_c_twice(self):
        self._roundtrip(SequenceStream([StringStream([b'abc']), StringStream([b'def'])]),
                        _buf(0x2C, 0x25, 0x63, 'abc', 0x35, 0x25, 0x63, 'def', 0x35, 0x3C),
                        back=(u'abc', u'def'))

class RecordTests(unittest.TestCase):
    def test_getters(self):
        T = Record.makeConstructor('t', 'x y z')
        T2 = Record.makeConstructor('t', 'x y z')
        U = Record.makeConstructor('u', 'x y z')
        t = T(1, 2, 3)
        self.assertTrue(T.isClassOf(t))
        self.assertTrue(T2.isClassOf(t))
        self.assertFalse(U.isClassOf(t))
        self.assertEqual(T._x(t), 1)
        self.assertEqual(T2._y(t), 2)
        self.assertEqual(T._z(t), 3)
        with self.assertRaises(TypeError):
            U._x(t)
