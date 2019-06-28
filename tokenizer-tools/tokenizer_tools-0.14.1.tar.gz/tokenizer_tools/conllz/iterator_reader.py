from tokenizer_tools.conllz.reader import read_conllz_from_string, read_conllx_from_string


def read_conllz_iterator(conll_file):
    with open(conll_file) as fd:
        content = fd.read()
        for sentence in read_conllz_from_string(content):
            yield sentence


def iterator_reader(input_file_list):
    for input_file in input_file_list:
        for i in read_conllz_iterator(input_file):
            yield i


def read_conllx_iterator(conll_file):
    with open(conll_file) as fd:
        content = fd.read()
        for sentence in read_conllx_from_string(content):
            yield sentence


def conllx_iterator_reader(input_file_list):
    for input_file in input_file_list:
        for i in read_conllx_iterator(input_file):
            yield i
