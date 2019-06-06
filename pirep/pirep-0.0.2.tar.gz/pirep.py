#! /usr/bin/env python3

"""
[P]ython [I]nteger [REP]resentations & Arithmetic Library

Almost all arguments for functions of this module can be decimal,
hexadecimal ('0x...', or without '0x' or 0x...), binary ('0b...',
0b...) or float.

Arithmetic function results format is hexadecimal by default
(you can change this by calling the function `psetmode()` or
with the optional parameter `fmt` for almost any function).
Hexadecimal/binary output format is string with prefix '0x'/'0b'.

By default integers are signed, integer width is equal 64
(you can change this by calling the function `psetmode()`).
"""

from textwrap import wrap
import re

############################################################
#                      Representation                      #
############################################################

# By default, all integers are signed
_is_signed = True

# By default the integer width is equal to 64
_int_width = 64

# The default output format is hexadecimal
_out_format = 'h'
_ftable = {'d': int, 'h': hex, 'b': bin, 'f': float}


def psetmode(signed=None, width=None, fmt=None):
    """Set parameters of integers in module:
    signed - signed/unsigned integers. Should be equal True or False;
    width  - width of integer (including the sign bit). Should be > 0;
    fmt    - determine format of arithmetic results by default.
             May be equal:
              'd' - usual integer (decimal),
              'h' - string-hexadecimal begining with '0x',
              'b' - string-binary beginning with '0b',
              'f' - usual float"""

    global _is_signed, _int_width, _out_format

    if signed is not None:
        _is_signed = bool(signed)

    if width is not None:
        assert width > 0
        _int_width = int(width)

    if fmt:
        fmt = fmt.lower()
        assert fmt in _ftable
        _out_format = fmt


def pgetmode():
    return [_is_signed, _int_width, _out_format]


def str2int(a):
    """Convert {float, int, hex, bin} -> int"""

    if isinstance(a, str):

        # Remove all spaces
        a = re.sub(r'\s+', '', a)

        if a[:2] == '0b' or a[:3] == '-0b':
            return int(a, 2)
        else:
            return int(a, 16)
    else:
        return int(a)


def _inconv(a):
    """Convert {float, int, hex, bin} -> int;
    value is truncated to the integer width"""

    x = str2int(a)

    # Truncate
    x &= ((1 << _int_width)-1)

    # Converse unsigned int to signed back
    if _is_signed and x >= (1 << (_int_width-1)):
        x -= (1 << _int_width)

    return x


def _outconv(x, fmt=None):
    """Convert positive decimal value according to format `fmt` (if it's given)
    or default format `_out_format` (see `setoutformat()`)"""

    assert isinstance(x, int)
    assert x >= 0
    if fmt:
        return _ftable[fmt](x)
    else:
        return _ftable[_out_format](x)


def c2repr(val, fmt=None):
    """Represent value in a manner 'Two's complement' to given format;
    value is truncated to the integer width

    >>> psetmode(True, 4, 'h')
    >>> c2repr(-2)
    '0xe'

    >>> c2repr(-2, 'd')
    -2

    >>> c2repr(14, 'd')
    -2

    >>> psetmode(False, 4, 'h')
    >>> c2repr(-1, 'd')
    15"""

    x = str2int(val)

    # Truncate
    x &= ((1 << _int_width)-1)

    # Converse unsigned int to signed back
    if _is_signed:

        if not fmt:
            fmt = _out_format
        assert fmt in ('d', 'f', 'h', 'b')

        if x >= (1 << (_int_width-1)) and fmt in ('d', 'f'):
            return -_outconv((1 << _int_width) - x, fmt)

    # Usual formated output
    return _outconv(x, fmt)


def c2drepr(val):
    """Convert {float, int, hex, bin} -> int;
    value is truncated to the integer width.
    Equivalent of function call c2repr(val, fmt='d')"""
    return _inconv(val)


def decomp(val, ends=(), fmt=None):
    """Get bitwise representation of integer `val` by bytes (if list `ends`
    is empty) or by fields (if list `ends` determine boarders of fields).

    val  - integer in any form (int, hex, bin or float);
    ends - list of last bit numbers of every field;
    fmt  - format of output ('d', 'h', 'b' or 'f')

    >>> decomp(3932166)
    ['00111100', '00000000', '00000110']

    >>> decomp(3932166, fmt='b')
    ['0b111100', '0b0', '0b110']

    >>> decomp(3932166, (22, 17, 15, 13, 7))
    ['01111', '00', '00', '000000', '00000110']

    >>> decomp(3932166, (7, 13, 15, 17, 22), 'h')
    ['0xf', '0x0', '0x0', '0x0', '0x6']"""

    # For convenience reverse bitwise representation
    rev_val = c2repr(str2int(val), 'b')[-1:1:-1]
    #rev_val = bin(str2int(val))[-1:1:-1]

    if not ends:
        # Just split representation by bytes
        y = [x[::-1].zfill(8) for x in wrap(rev_val, 8)[::-1]]
    else:
        # Add to y all other fields
        y = []
        i = 0
        ends = sorted(ends)
        for j in ends:
            y.append(rev_val[i:j+1][::-1].zfill(j+1-i))
            i = j+1

        # Reverse back fields order
        y = y[::-1]

    if fmt:
        return [_outconv(int(x, 2), fmt) for x in y]
    else:
        return y


class Field:
    def __init__(self, fname, fbeg, fend):
        self.fname = fname
        self.fbeg = fbeg
        self.fend = fend
        self.verbose = {}
        self.invalid = set()
        self.only_true = set()

    def __repr__(self):
        if self.fbeg != self.fend:
            return '{}[{}:{}]'.format(self.fname, self.fend, self.fbeg)
        else:
            return '{}[{}]'.format(self.fname, self.fbeg)

    def borders(self, length=0):
        """Get string with boundary bit numbers. Whenever possible
        the string length will be equal to `length`."""

        if self.fbeg == self.fend:
            return str(self.fbeg).center(length)
        else:
            dash_num = max(length - len(str(self.fbeg)) - len(str(self.fend)),
                           1)
            return '{}{}{}'.format(self.fend, '-'*dash_num, self.fbeg)

    def add_verbose(self, fvalue, fvalue_name):
        self.verbose[str2int(fvalue)] = fvalue_name

    def add_invalid(self, fvalue):
        self.invalid.add(str2int(fvalue))

    def add_only_true(self, fvalue):
        self.only_true.add(str2int(fvalue))


class Enc:
    """Encoding of some entity. Consists of the entity name and
    the list of fields names and their last bit numbers."""

    def __init__(self, name, fields_unsorted):
        self.name = name
        fields = sorted(fields_unsorted, key=lambda x: x[1])

        last_fend = fields[0][1]
        self.fields = [Field(fields[0][0], 0, last_fend)]
        for f in fields[1:]:
            self.fields.append(Field(f[0], last_fend+1, f[1]))
            last_fend = f[1]

    def __repr__(self):
        return '{}: {}'.format(self.name, ', '.join(map(str,
                                                        self.fields[::-1])))

    def __iter__(self):
        for x in self.fields:
            yield x
        return

    def field(self, fname_lbit):
        for f in self.fields:
            if f.fend == fname_lbit[1]:
                assert f.fname == fname_lbit[0]
                return f


def decode(val, enc, fmt=None, borders=False, ret_string=False):
    """
    Consider the code `1700040f` of Sparc operation `sethi` for example:

      >>> e = Enc('sethi', (('opc', 31), ('rd', 29),
                            ('opc', 24), ('imm22', 21)))
      >>> decode('1700040f', e, borders=True)
       opc     rd    opc           imm22
        00   01011   100   0000000000010000001111
      31-30  29-25  24-22  21-------------------0

      >>> decode('17 00 04 0f', e)
      opc    rd   opc          imm22
       00  01011  100  0000000000010000001111

    Add checker of opcode and verbose values:

      >>> e.field(('opc', 31)).add_only_true(0)
      >>> e.field(('rd', 29)).add_verbose(8, 'eight')
      >>> e.field(('rd', 29)).add_verbose(9, 'nine')

      >>> decode('1700040f', e, 'h')
      opc   rd  opc  imm22
      0x0  0xb  0x4  0x40f

    Spoil code to see error message and verbose value of field `rd`:

      >>> decode(psetbits('1700040f', (25, 30), '0b101000'), e, 'h')
      opc   rd  opc  imm22
      0x1  0x8  0x4  0x40f

      Error! Wrong code: opc[31:30] = 0x1
      Valid codes: 0x0

      rd[29:25]:   eight"""

    # Collect data
    fields = list(enc)[::-1]
    decomp_ = decomp(val, (x.fend for x in fields), fmt)

    # Calc minimum lengths of borders strings
    if borders:
        bord_str_lens = [len(f.borders()) for f in fields]
    else:
        bord_str_lens = [0]*len(fields)

    # Calc lengths of fields strings
    str_lens = []
    for f, d, bl in zip(fields, decomp_, bord_str_lens):
        str_lens.append(max(len(f.fname), bl, len(str(d))))

    # Make output string
    s = ['  '.join(f.fname.center(l) for f, l in zip(fields, str_lens))]
    s += ['  '.join(str(d).center(l) for d, l in zip(decomp_, str_lens))]
    if borders:
        s += ['  '.join(f.borders(l) for f, l in zip(fields, str_lens))]
    s = '\n'.join(s)

    if fmt:
        # Any -> int
        decomp_int = [str2int(d) for d in decomp_]
    else:
        # Binary without leading '0b' -> int
        decomp_int = [int(d, 2) for d in decomp_]
        fmt = 'b'

    # Check only true
    for f, i, d in zip(fields, decomp_int, decomp_):
        if f.only_true and i not in f.only_true:
            s += '\n\nError! Wrong code: {} = {}'.format(f, d)
            s += '\nValid codes: {}'.format(', '.join(str(_outconv(x, fmt))
                                                      for x in f.only_true))

    # Check invalids
    for f, i, d in zip(fields, decomp_int, decomp_):
        if i in f.invalid:
            s += '\n\nError! Invalid value: {} = {}'.format(f, d)

    # Over encoding warning
    last_bit = fields[0].fend
    mask = pmask(0, last_bit)
    remainder = str2int(psrl(psub(val, pand(val, mask)), last_bit+1))
    if remainder:
        s += '\n\nWarning! There are significant bits higher than' \
             ' {}: {}'.format(last_bit, _outconv(remainder, fmt))

    # Check verbose values
    vs = '\n'
    for f, i in zip(fields, decomp_int):
        if i in f.verbose:
            vs += '\n{}:   {}'.format(f, f.verbose[i])
    if len(vs) > 1:
        s += vs

    # Output
    if ret_string:
        return s
    else:
        print(s)


############################################################
#                        Arithmetic                        #
############################################################

def padd(a1, a2, fmt=None):
    """Sum of integers"""
    return c2repr(_inconv(a1) + _inconv(a2), fmt)


def psub(a1, a2, fmt=None):
    """Subtraction of integers"""
    return c2repr(_inconv(a1) - _inconv(a2), fmt)


def pmul(a1, a2, fmt=None):
    """Multiplication of integers"""
    return c2repr(_inconv(a1) * _inconv(a2), fmt)


def pdiv(a1, a2, fmt=None):
    """Division of integers"""
    return c2repr(_inconv(a1) // _inconv(a2), fmt)


def pdivf(a1, a2):
    """Division of integers with float result"""
    return _inconv(a1) / _inconv(a2)


def prem(a1, a2, fmt=None):
    """Remainder of the division of integers"""
    return c2repr(_inconv(a1) % _inconv(a2), fmt)


def psll(a, i, fmt=None):
    """Logical left shift of integers"""
    return c2repr(_inconv(a) << _inconv(i), fmt)


def psrl(a, i, fmt=None):
    """Logical right shift of integers"""
    return c2repr(_inconv(a) >> _inconv(i), fmt)


def pand(a1, a2, fmt=None):
    """Bitwise AND"""
    return c2repr(_inconv(a1) & _inconv(a2), fmt)


def por(a1, a2, fmt=None):
    """Bitwise OR"""
    return c2repr(_inconv(a1) | _inconv(a2), fmt)


def pxor(a1, a2, fmt=None):
    """Bitwise XOR"""
    return c2repr(_inconv(a1) ^ _inconv(a2), fmt)


def pmask(l, h, fmt=None):
    """Get mask. Example:

    >>> pmask(1, 3, 'b')
    '0b1110'"""

    return c2repr(((-1) << _inconv(l)) & (~((-1) << (_inconv(h)+1))), fmt)


def pinv(a, fmt=None):
    """Bitwise inversion (or, XOR with -1)"""
    return pxor(a, -1)

def pgetbits(a, r, fmt=None):
    """Get bit or bits range of integer. Example:

    >>> c2repr(694, 'b')
    '0b1010110110'

    >>> pgetbits(694, 7, 'd')
    1

    >>> pgetbits(694, (3, 7), 'b')
    '0b10110'"""

    if isinstance(r, int):
        return c2repr((_inconv(a) & (1<<r)) >> r, fmt)
    else:
        return c2repr((_inconv(a) & pmask(r[0], r[1], 'd')) >> r[0], fmt)


def psetbits(a, r, v=-1, fmt=None):
    """Assign the value `v` to the bits specified by `r`. Example:

    >>> c2repr(694, 'b')
    '0b1010110110'

    >>> psetbits(694, 1, 0, 'b')
    '0b1010110100'

    >>> psetbits(694, (2, 7), fmt='b')
    '0b1011111110'

    >>> psetbits(694, (2, 7), '0b010101', 'b')
    '0b1001010110'"""

    if isinstance(r, int):
        v_mask = 1 << r
        return c2repr((_inconv(a) & (~v_mask))
                      | (_inconv(v) << r) & v_mask, fmt)
    else:
        v_mask = pmask(r[0], r[1], 'd')
        return c2repr((_inconv(a) & (~v_mask))
                      | (_inconv(v) << r[0]) & v_mask, fmt)


def pdropbits(a, r, fmt=None):
    """Set bits to zero (it is psetbits(a, r, v=0, fmt))"""
    return psetbits(a, r, 0, fmt)


def pintmin(fmt=None):
    """Get minimum integer according to current mode"""

    if _is_signed:
        return c2repr(1 << (_int_width-1), fmt)
    else:
        return c2repr(0, fmt)


def pintmax(fmt=None):
    """Get maximum integer according to current mode"""

    if _is_signed:
        return c2repr(~(1 << (_int_width-1)), fmt)
    else:
        return c2repr(-1, fmt)


############################################################
# Prevent importing re, wrap and test_pir by `from pirep import *`
############################################################
__all__ = [i for i in dir() if not i.startswith('_')]
__all__.remove('re')
__all__.remove('wrap')


############################################################
#                           Test                           #
############################################################

def test_module():
    s, w, f = pgetmode()

    psetmode(True, 64, 'h')
    assert ( decomp(3932166) == ['00111100', '00000000', '00000110'] )
    assert ( decomp('0x3c0006') == ['00111100', '00000000', '00000110'] )
    assert ( decomp('3c0006') == ['00111100', '00000000', '00000110'] )
    assert ( decomp('0b1111000000000000000110')
             == ['00111100', '00000000', '00000110'] )
    assert ( decomp(3932166.) == ['00111100', '00000000', '00000110'] )
    assert ( decomp(3932166, (7, 13, 15, 17, 22))
             == ['01111', '00', '00', '000000', '00000110'] )
    assert ( decomp(3932166, fmt='b') == ['0b111100', '0b0', '0b110'] )
    assert ( decomp(3932166, (7, 13, 15, 17, 22), 'h')
             == ['0xf', '0x0', '0x0', '0x0', '0x6'] )
    assert ( psub('0b100000', padd('a', 11)) == '0xb' )
    psetmode(fmt='b')
    assert ( pmul(3, padd(pdiv('f', '0b100'), prem(11, '0x3'))) == '0b1111' )
    psetmode(width=4)
    assert ( c2repr(-1) == '0b1111' )
    assert ( c2repr(8) == c2repr(-8) == '0b1000' )
    assert ( c2repr(7) == c2repr(-9) == '0b111' )
    psetmode(fmt='h')
    assert ( padd(15, 15) == '0xe' )
    assert ( psub(1, 15) == '0x2' )
    assert ( padd(7, 1., fmt='b') == '0b1000' )
    assert ( pmul('0b1000', '0b111') == '0x8' )
    assert ( pmul('0b1000', '0b111', fmt='f') == -8. )
    assert ( c2repr(14, fmt='d') == -2 )
    assert ( c2repr(14, fmt='h') == '0xe' )
    assert ( pmul('0b1000', '0b110', fmt='d') == 0 )
    assert ( padd(7, 7, 'd') == -2 )
    assert ( psub(1, 2, 'd') == -1 )
    psetmode(width=64)
    assert ( psub('0b100000', padd('a', 11)) == '0xb' )
    assert ( psub('0b10000', padd('a', 11)) == '0xfffffffffffffffb' )
    psetmode(fmt='b')
    assert ( pmul(3, padd(pdiv('f', '0b100'), prem(11, '0x3'))) == '0b1111' )
    assert ( pgetmode() == [True, 64, 'b'] )
    psetmode(signed=False, width=4, fmt='h')
    assert ( padd(7, 7, 'd') == 14 )
    assert ( psub(1, 2) == '0xf' )
    assert ( psub(1, 2, 'd') == 15 )
    assert ( psub(1, 1000) == '0x9' )
    assert ( c2repr(-1, 'd') == 15 )
    psetmode(False, 6, 'b')
    assert ( pintmin() == '0b0' and pintmax() == '0b111111' )
    psetmode(True)
    assert ( pintmin() == '0b100000' and pintmax() == '0b11111' )
    assert ( padd(pintmin(), pintmax(), 'd') == -1 )
    assert ( psub(pintmin(), 1, 'd') == pintmax('d') == 31 )
    psetmode(True, 64, 'f')
    assert ( pand(204, 694, 'h') == '0x84' and por(204, 694, 'h') == '0x2fe' )
    assert ( pxor(204, 694, 'h') == '0x27a' and pmask(1, 3, 'b') == '0b1110' )
    assert ( pgetbits(694, 7, 'd') == 1 )
    assert ( pgetbits(694, (3, 7), 'b') == '0b10110' )
    assert ( psetbits(694, 1, 0, 'h') == '0x2b4' )
    assert ( psetbits(694, (2, 7), fmt='h') == '0x2fe' )
    assert ( psetbits(694, (2, 7), '0b010101', 'b') == '0b1001010110' )
    assert ( pdropbits('0b10100', 2, 'd') == 16 )
    psetmode(False, 8, 'h')
    assert ( pinv(0) == '0xff' and pinv(1) == '0xfe' and pinv(-2) == '0x1' )
    psetmode(True)
    assert ( pinv(0) == '0xff' and pinv(1) == '0xfe' and pinv(-2) == '0x1' )
    psetmode(width=64)
    e = Enc('sethi', (('opc', 31), ('rd', 29), ('opc', 24), ('imm22', 21)))
    s = '\n'.join((decode('17 00 04 0f', e, ret_string=True),
                   decode('1700040f', e, 'h', ret_string=True),
                   decode('1700040f', e, 'd', ret_string=True),
                   decode('1700040f', e, borders=True, ret_string=True)))
    assert ( s == '\n'.join(('opc    rd   opc          imm22         ', 
                             ' 00  01011  100  0000000000010000001111',
                             'opc   rd  opc  imm22',
                             '0x0  0xb  0x4  0x40f',
                             'opc  rd  opc  imm22',
                             ' 0   11   4    1039',
                             ' opc     rd    opc           imm22         ',
                             '  00   01011   100   0000000000010000001111',
                             '31-30  29-25  24-22  21-------------------0')) )
    e.field(('opc', 31)).add_only_true(0)
    e.field(('opc', 24)).add_verbose('0b100', 'four')
    e.field(('opc', 31)).add_invalid(1.)
    e.field(('rd', 29)).add_invalid(1.)
    e.field(('imm22', 21)).add_verbose('0b100', 'four')
    s = '\n'.join((decode('1700040f', e, ret_string=True),
                   decode(padd('1700040f', 5<<30), e, ret_string=True),
                   decode(padd('1700040f', 7<<31), e, ret_string=True)))
    assert ( s == '\n'.join(('opc    rd   opc          imm22         ',
                             ' 00  01011  100  0000000000010000001111',
                             '\nopc[24:22]:   four',
                             'opc    rd   opc          imm22         ',
                             ' 01  01011  100  0000000000010000001111',
                             '\nError! Wrong code: opc[31:30] = 01',
                             'Valid codes: 0b0',
                             '\nError! Invalid value: opc[31:30] = 01',
                             '\nWarning! There are significant bits' \
                                                        ' higher than 31: 0b1',
                             '\nopc[24:22]:   four',
                             'opc    rd   opc          imm22         ',
                             ' 10  01011  100  0000000000010000001111',
                             '\nError! Wrong code: opc[31:30] = 10',
                             'Valid codes: 0b0',
                             '\nWarning! There are significant bits' \
                                                        ' higher than 31: 0b11',
                             '\nopc[24:22]:   four')) )
    e = Enc('someth', (('d', 7), ('ccccc', 4), ('B', 3), ('A', 0)))
    s = decode('a5', e, ret_string=True)
    assert ( s == '\n'.join((' d   ccccc   B   A',
                             '101    0    010  1')) )
    assert len(decomp(-13)) == 8
    assert decomp(-13)[-1] == '11110011'
    assert decomp(-13)[-2] == decomp(-13)[0] == '11111111'
    e = Enc('bla-bla', (('long_long_name', 31), ('oth_name', 30)))
    s = decode(151330522, e, borders=True, ret_string=True)
    assert s == '\n'.join(('long_long_name              oth_name           ',
                           '      0         0001001000001010001111011011010',
                           '      31        30----------------------------0'))

    psetmode(True, 3, 'b')
    for i in range(-30, 30):
        assert c2drepr(i) == _inconv(i)
        assert c2drepr(i) == c2repr(i, 'd')
    psetmode(False, 3, 'b')
    for i in range(-30, 30):
        assert c2drepr(i) == _inconv(i)
        assert c2drepr(i) == c2repr(i, 'd')

    psetmode(s, w, f)
    print('Successfully tested')

if __name__ == '__main__':
    test_module()

