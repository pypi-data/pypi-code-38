from tokenizer_tools.conllz.iterator_reader import read_conllz_iterator
from tokenizer_tools.conll.writer import write_conll


def conllz_to_conll(conllz_file, conll_file):
    sentence_iterator = read_conllz_iterator(conllz_file)

    conll_data = []

    for sentence in sentence_iterator:
        conll_data.append((sentence.word_lines, sentence.get_attribute_by_index(0)))

    write_conll(conll_data, conll_file)
