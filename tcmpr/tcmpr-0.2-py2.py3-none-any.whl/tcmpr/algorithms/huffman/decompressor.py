import os
import pickle
from . import compressor
from ..utils import tools


def decompress_huffman(input_file):
    output_filename = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(os.path.dirname(input_file), output_filename)

    with open(input_file, 'rb') as file:
        data = pickle.load(file)

    frequencies, byte_array = data
    root = compressor.build_binary_tree(frequencies)
    bits_string = tools.convert_bytes_to_bit_str(byte_array)
    encoded_string = tools.remove_padding_of_encoded_str(bits_string)
    decoded_string = tools.get_decoded_str(root, encoded_string)

    with open(output_file, 'w') as output:
        output.write(decoded_string)
    return output_file
