import json


def buf_to_hex(buf):
    return buf.hex()


def hex_to_buf(s_hex):
    return bytes.fromhex(s_hex)


def dump_buf(buf, dump=True):
    return buf_to_hex(buf) if dump else buf


def get_sorted_qs(data):
    return json.dumps(sorted(data))


def remove_prefix_0x(s):
    """remove prefix '0x' or '0X' from string s

    :param s: str

    :return: str, the substring which remove the prefix '0x' or '0X'
    """
    if s[:2].lower() == '0x':
        s = s[2:]
    return s
