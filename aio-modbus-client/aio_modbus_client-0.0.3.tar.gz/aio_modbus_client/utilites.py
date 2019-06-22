# from six import byte2int, int2byte


def __generate_crc16_table():
    """ Generates a crc16 lookup table

    .. note:: This will only be generated once
    """
    result = []
    for byte in range(256):
        crc = 0x0000
        for _ in range(8):
            if (byte ^ crc) & 0x0001:
                crc = (crc >> 1) ^ 0xa001
            else:
                crc >>= 1
            byte >>= 1
        result.append(crc)
    return result


__crc16_table = __generate_crc16_table()


def computeCRC(data):
    """ Computes a crc16 on the passed in string. For modbus,
    this is only used on the binary serial protocols (in this
    case RTU).

    The difference between modbus's crc16 and a normal crc16
    is that modbus starts the crc value out at 0xffff.

    :param data: The data to create a crc16 of
    :returns: The calculated CRC
    """
    crc = 0xffff
    for a in data:
        idx = __crc16_table[(crc ^ a) & 0xff]
        crc = ((crc >> 8) & 0xff) ^ idx
    swapped = ((crc << 8) & 0xff00) | ((crc >> 8) & 0x00ff)
    return swapped


def checkCRC(data, check):
    """ Checks if the data matches the passed in CRC

    :param data: The data to create a crc16 of
    :param check: The CRC to validate
    :returns: True if matched, False otherwise
    """
    crc = computeCRC(data)
    return crc == check


def rtuFrameSize(data, byte_count_pos):
    """ Calculates the size of the frame based on the byte count.

    :param data: The buffer containing the frame.
    :param byte_count_pos: The index of the byte count in the buffer.
    :returns: The size of the frame.

    The structure of frames with a byte count field is always the
    same:

    - first, there are some header fields
    - then the byte count field
    - then as many data bytes as indicated by the byte count,
    - finally the CRC (two bytes).

    To calculate the frame size, it is therefore sufficient to extract
    the contents of the byte count field, add the position of this
    field, and finally increment the sum by three (one byte for the
    byte count field, two for the CRC).
    """
    # return byte2int(data[byte_count_pos]) + byte_count_pos + 3
    return data[byte_count_pos][0] + byte_count_pos + 3


# --------------------------------------------------------------------------- #
# Bit packing functions
# --------------------------------------------------------------------------- #
def pack_bitstring(bits):
    """ Creates a string out of an array of bits
    :param bits: A bit array
    example::
        bits   = [False, True, False, True]
        result = pack_bitstring(bits)
    """
    ret = b''
    i = packed = 0
    for bit in bits:
        if bit:
            packed += 128
        i += 1
        if i == 8:
            ret += bytes((packed,))  #int2byte(packed)
            i = packed = 0
        else:
            packed >>= 1
    if 0 < i < 8:
        packed >>= (7 - i)
        # ret += int2byte(packed)
        ret += bytes((packed,))
    return ret


def unpack_bitstring(string):
    """ Creates bit array out of a string
    :param string: The modbus data packet to decode
    example::
        bytes  = 'bytes to decode'
        result = unpack_bitstring(bytes)
    """
    byte_count = len(string)
    bits = []
    for byte in range(byte_count):
        value = int(string[byte])
        for _ in range(8):
            bits.append((value & 1) == 1)
            value >>= 1
    return bits

#
# def make_byte_string(s):
#     """
#     Returns byte string from a given string, python3 specific fix
#     :param s:
#     :return:
#     """
#     if isinstance(s, string_types):
#         s = s.encode()
#     return s
