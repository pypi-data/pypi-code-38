"""
`pytest` testing framework file for ELFIN preprocessor
"""

import satnogsdecoders.process


def test_answer():
    """
    `pytest` entry point
    """

    dut = satnogsdecoders.process.ElfinPp()
    escaped = bytearray([0x00, 0x11, 0x27, 0x27, 0x22])
    normal = bytearray([0x00, 0x11, 0xa2, 0x72, 0x72, 0x20])
    test = bytearray([
        0x93, 0x00, 0x27, 0x00, 0x5e, 0x00, 0x27, 0x93, 0x27, 0x27, 0x27, 0x5e
    ])
    packets = [escaped, normal, test]
    target_len = [4, 6, 9]

    index = 0
    for frame in packets:
        temp1 = dut.decode(frame)
        assert len(temp1) == target_len[index]
        index += 1
