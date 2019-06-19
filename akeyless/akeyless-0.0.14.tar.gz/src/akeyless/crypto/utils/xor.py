

def xor_fragments(fragments):
    if not fragments:
        raise ValueError("No fragment was provided")

    n = len(fragments[0])
    res = fragments[0]
    for i in range(1, len(fragments)):
        if len(fragments[i]) is not n:
            raise ValueError("The fragments are not in the same size")
        res = xor_bytes(res, fragments[i])
    return bytes(res)


def xor_bytes(a, b):
    max_len = max(len(a), len(b))
    dst = bytearray(max_len)
    for i in range(0, len(a)):
        dst[i] = a[i] ^ b[i]
    return dst
