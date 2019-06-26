"""
This module is responsible for implementing
LZW CODING algorithm which can be used to
decompress input file with extension ".lzw".
"""
import os


class Step:
    def __init__(self):
        self._step = 0

    def set_step(self, step):
        self._step = step

    def get_step(self):
        return self._step


def decompress_lzw(input_file):
    """
    Function to decompress input file with extension ".lzw"
    """
    output_filename = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(os.path.dirname(input_file), output_filename)

    with open(input_file, 'rb') as f:
        data = f.read()

    # Because we store codes in 2-bytes in file so when reading it back,
    # we must read each 2 bytes for converting back properly
    step_setting = Step()
    if int.from_bytes(data[0:2], byteorder='big', signed=False) == 2:
        step_setting.set_step(2)
    elif int.from_bytes(data[0:2], byteorder='big', signed=False) == 4:
        step_setting.set_step(4)
    length = len(data)
    codes = []
    step = step_setting.get_step()
    for i in range(2, length, step):
        b = int.from_bytes(data[i:i + step], byteorder='big', signed=False)
        codes.append(b)

    encoded_str = decode_codes(codes)
    with open(output_file, 'w') as out:
        out.write(encoded_str)

    return output_file


def decode_codes(codes):
    # Initialize dictionary
    dictionary = {c: chr(c) for c in range(0, 256)}
    max_code = 255

    z = None
    entries = []
    for key in codes:
        entry = dictionary.get(key, None)
        if entry is None:
            entry = z + z[0]

        entries.append(entry)
        if z is not None:
            max_code += 1
            dictionary[max_code] = z + entry[0]
        z = entry
    return ''.join(entries)