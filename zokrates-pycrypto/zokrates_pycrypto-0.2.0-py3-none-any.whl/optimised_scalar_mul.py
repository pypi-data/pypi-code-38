import bitstring
from .babyjubjub import Point

# //TODO: add doc

WINDOW_SIZE_BITS = 2


def scalar_mul_windowed_bits(bits, base):
    """
    FIXED base point
    Log2(jubjubE) = 253.6
    => 253 bits!
    => 254 bits lenghts
    => 127 windows
    use WINDOW_SIZE_BITS
    """
    # Split into 2 bit windows
    if isinstance(bits, bitstring.BitArray):
        bits = bits.bin
    windows = [
        bits[i : i + WINDOW_SIZE_BITS] for i in range(0, len(bits), WINDOW_SIZE_BITS)
    ]
    assert len(windows) > 0

    # Hash resulting windows
    return scalar_mul_windowed(windows, base)


def scalar_mul_windowed(windows, base):
    # FIXED BASE POINT
    if not isinstance(base, Point):
        base = Point(*base)

    segments = len(windows)
    table = scalar_mul_windowed_gen_table(base, segments)
    a = Point.infinity()
    for j, window in enumerate(windows[::-1]):
        row = table[j]
        a += row[int(window, 2)]
    return a


def scalar_mul_windowed_gen_table(base, segments=127):
"""    Row i of the lookup table contains:
        [2**4i * base, 2 * 2**4i * base, 3 * 2**4i * base, 3 * 2**4i * base]
        E.g:
        row_0 = [base, 2*base, 3*base, 4*base]
        row_1 = [16*base, 32*base, 48*base, 64*base]
        row_2 = [256*base, 512*base, 768*base, 1024*base]"""

        
    # segments *  4 (WINDOW_SIZE_BITS**2)
    p = base
    table = []
    for _ in range(0, segments):
        row = [p.mult(i) for i in range(0, WINDOW_SIZE_BITS ** 2)]
        # FIXME: + 1 needed ... see pedersen hash
        table.append(row)
        p = p.double().double()
    return table


def pprint_scalar_mul_windowed_table(table):

    dsl = []

    segments = len(table)
    for i in range(0, segments):
        r = table[i]
        dsl.append("//Round {}".format(i))
        dsl.append(
            "cx = sel([e[{}], e[{}]], [{} , {}, {}, {}])".format(
                2 * i, 2 * i + 1, r[0].x, r[1].x, r[2].x, r[3].x
            )
        )
        dsl.append(
            "cy = sel([e[{}], e[{}]], [{} , {}, {}, {}])".format(
                2 * i, 2 * i + 1, r[0].y, r[1].y, r[2].y, r[3].y
            )
        )
        dsl.append("a = add(a , [cx, cy], context)")

        # //round X
        # cx = sel([e[2*X], e[2*X+1]], 0, x1, x2, x3)
        # cy = sel([...], 1, y1, y2, y3)
        # a = add(a, [cx, xy], context)

    return "\n".join(dsl)
