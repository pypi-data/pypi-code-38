import collections

from tokenizer_tools.conll.iterator_reader import iterator_reader


def entity_vocabulary(input_files, value_index=0, entity_index=1):
    all_vocabulary_set = collections.defaultdict(list)
    for sentence in iterator_reader(input_files):
        entity_set = {i[value_index]: i[entity_index] for i in sentence}

        for k, v in entity_set.items():
            all_vocabulary_set[v].append(k)

    return all_vocabulary_set


if __name__ == "__main__":
    pass
