"""
This module is responsible for implementing
HUFFMAN CODING algorithm which can be used to
compressing input file.
"""

import pickle
import collections
import os
from ..entity.node import Node
from queue import PriorityQueue
from ..utils import tools


def compress_huffman(input_file):
    """
    Function compress input file and create new compressed
    file in the same folder (or in defined output path).
    Algorithm uses a priority queue where the node with
    lowest probability (frequency) is given highest priority.
    :param: input_file,
    :return: compressed output file path
    """
    output_file_dir = os.path.dirname(input_file)
    output_filename = input_file + ".huffman"
    output_file_path = os.path.join(output_file_dir, output_filename)

    try:
        with open(input_file, "r", encoding='utf-8') as file:
            data = file.read()
    except UnicodeDecodeError:
        with open(input_file, "r", encoding='ISO-8859-1') as file:
            data = file.read()

    frequencies = collections.Counter(data)
    root = build_binary_tree(frequencies)
    encoded_string = tools.get_encoded_str(root, data)
    padded_encoded_string = tools.pad_encoded_str(encoded_string)
    byte_encoded_data = tools.get_byte_array(padded_encoded_string)

    with open(output_filename, 'wb') as output:
        pickle.dump((frequencies, byte_encoded_data), output)
    return output_file_path


def build_binary_tree(frequencies):
    """
    Function to create binary huffman tree
    based on counted frequencies in input data
    """
    queue = put_frequencies_into_priority_queue(frequencies)
    while queue.qsize() > 1:
        left = queue.get()[1]
        right = queue.get()[1]
        # create alternative char node for two nodes with lowest probability
        # which is sum of these two
        alt_char_node = Node('', left.frequency + right.frequency, left, right)
        queue.put((alt_char_node.frequency, alt_char_node))

    root_of_tree = queue.get()[1]
    return root_of_tree


def put_frequencies_into_priority_queue(frequencies):
    """Create PriorityQueue and put there frquencies"""
    queue = PriorityQueue()
    for key, value in frequencies.items():
        node = Node(key, value)
        queue.put((node.frequency, node))
    return queue

