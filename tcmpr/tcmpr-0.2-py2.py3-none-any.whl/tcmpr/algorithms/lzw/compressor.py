"""
This module is responsible for implementing
LZW CODING algorithm which can be used to
compressing input file.
"""
import os


def compress_lzw(input_file):
    """
    Function compress input file and create new compressed
    file with extension ".lzw" (for decompression purposes)
    in place of use. Algorithm create dictionary of encoding
    base on input file and frequent subsequence of chars.
    :param input_file:
    :return: compressed file path
    """
    output_file_dir = os.path.dirname(input_file)
    output_filename = input_file + ".lzw"
    output_file_path = os.path.join(output_file_dir, output_filename)

    try:
        with open(input_file, "r", encoding='utf-8') as file:
            data = file.read()
    except UnicodeDecodeError:
        with open(input_file, "r", encoding='ISO-8859-1') as file:
            data = file.read()

    encoded_input_data = encode_data(data)

    # for decompression purpose save encoded data to file
    # with 2 bytes for each code
    with open(output_file_path, 'wb') as output:
        chunk_size = 2
        if max(encoded_input_data) > 2**15:
            chunk_size = 4
            output.write((4).to_bytes(2, byteorder='big'))
        else:
            output.write((2).to_bytes(2, byteorder='big'))
        for code in encoded_input_data:
            output.write(code.to_bytes(chunk_size, byteorder='big'))

    return output_file_path


def encode_data(data):
    """
    Create dictionary base on input data and encode data
    and look for frequent subsequences and assign them to
    proper codes in dictionary.
    :param data:
    :return:
    """
    dictionary = {chr(c): c for c in range(0, 256)}
    chars = dictionary.keys()
    max_code = 255

    index = 0
    data_length = len(data)
    codes = []
    z = data[index]
    while index < data_length -1:
        k = data[index + 1]
        if z + k in chars:
            z = z + k
            index += 1
        else:
            codes.append(dictionary[z])
            max_code += 1
            dictionary[z + k] = max_code
            z = k
            index += 1
    codes.append(dictionary[z])

    return codes


