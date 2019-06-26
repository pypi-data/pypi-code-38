

def _assign_codes(current, code, codes):
    """Recursive utility to getting codes"""
    if current.left:
        code.append('0')
        _assign_codes(current.left, code, codes)
        code.pop()

    if current.right:
        code.append('1')
        _assign_codes(current.right, code, codes)
        code.pop()

    if current.is_leaf():
        key = current.char
        codes[key] = ''.join(code)
        return


def get_codes_from_binary_tree(root):
    """Return code for each char in input data (original)"""
    current = root
    code = []
    codes = {}

    _assign_codes(current, code, codes)
    return codes


def get_encoded_str(root, data):
    """Change data to encoded string and return it"""
    codes = get_codes_from_binary_tree(root)
    compressed_data = []
    for element in data:
        compressed_data.append(codes[element])
    return ''.join(compressed_data)


def get_decoded_str(root, encoded_string):
    """Decode encoded string and return it"""
    decoded_data = []
    current = root
    for code in encoded_string:
        if code == '0':
            current = current.left
        if code == '1':
            current = current.right
        if current.is_leaf():
            char = current.char
            decoded_data.append(char)
            current = root
    return ''.join(decoded_data)


def pad_encoded_str(encoded_string):
    """Return padded encoded string with zero
       to full byte if missing
    """
    extra_zero = 8 - len(encoded_string) % 8
    padded_encoded_string = '0' * extra_zero + encoded_string
    extra_zero_info = '{0:08b}'.format(extra_zero)
    padded_encoded_string = extra_zero_info + padded_encoded_string
    return padded_encoded_string


def remove_padding_of_encoded_str(padded_encoded_string):
    """Remove padding to get original encoded string"""
    extra_zero_info = padded_encoded_string[:8]
    extra_zero = int(extra_zero_info, 2)
    padded_encoded_string = padded_encoded_string[8:]
    encoded_string = padded_encoded_string[extra_zero:]
    return encoded_string


def get_byte_array(padded_encoded_string):
    """Convert padded encoded string into bytes"""
    byte_array = bytearray()
    length = len(padded_encoded_string)
    for i in range(0, length, 8):
        byte = padded_encoded_string[i:i+8]
        byte_array.append(int(byte, 2))
    return byte_array


def convert_bytes_to_bit_str(byte_array):
    """Convert bytes to bits string for decoding purpose"""
    bin_format = '{0:08b}'
    bit_data = []
    for element in byte_array:
        data = bin_format.format(element)
        bit_data.append(data)
    return ''.join(bit_data)

