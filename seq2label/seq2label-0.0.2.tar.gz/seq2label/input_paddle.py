import functools


def index_table_from_file(vocabulary_file=None):
    index_table = {}
    index_counter = 0
    with open(vocabulary_file) as fd:
        for line in fd:
            key = line.strip()
            index_table[key] = index_counter
            index_counter += 1

    class Lookuper(object):
        def __init__(self, index_table):
            self.index_table = index_table

        def lookup(self, string):
            return self.index_table.get(string)

    return Lookuper(index_table)


def to_fixed_len(words, fixed_len, defaults_words):
    if len(words) < fixed_len:
        for _ in range(fixed_len - len(words)):
            words.append(defaults_words)
    else:
        words = words[:fixed_len]

    return words


def generator_func(data_generator_func, config, vocabulary_lookup, tag_lookup):
    for sentence in data_generator_func():
        words, label = parse_fn(sentence)
        if config.get('max_seq_length'):
            words = to_fixed_len(words, config.get('max_seq_length'), config.get('default_value'))

        yield [vocabulary_lookup.lookup(i) for i in words], tag_lookup.lookup(label)


def parse_fn(offset_data):
    label = offset_data.label
    words = [i for i in offset_data.text]

    return words, label


class Vocabulary(object):
    def __init__(self, lookup_table):
        self.lookup_table = lookup_table
        self.reverse_lookup_table = {v: k for k, v in lookup_table.items()}

    def lookup(self, str_):
        if str_ in self.lookup_table:
            return self.lookup_table[str_]
        else:
            # not in the table: return extra max(id) + 1
            return len(self.lookup_table)

    def length(self):
        return len(self.lookup_table)

    def id_to_str(self, id_):
        if id_ in self.reverse_lookup_table:
            return self.reverse_lookup_table[id_]
        else:
            return '<UNK>'


def read_vocabulary(vocabulary):
    data = {}

    fd = open(vocabulary) if isinstance(vocabulary, str) else vocabulary
    for line in fd:
        word = line.strip()
        data[word] = len(data)

    if isinstance(vocabulary, str):
        fd.close()

    return Vocabulary(data)


def build_input_func(data_generator_func, config=None):
    vocabulary_lookup = read_vocabulary(config['vocab_data'])
    tag_lookup = read_vocabulary(config['tags_data'])

    def input_func():
        train_dataset = generator_func(data_generator_func, config, vocabulary_lookup, tag_lookup)

        return train_dataset

    return input_func


def build_gold_generator_func(offset_dataset):
    return functools.partial(generator_func, offset_dataset)

