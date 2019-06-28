from tokenizer_tools.conllz.iterator_reader import iterator_reader, conllx_iterator_reader
from tokenizer_tools.converter.conllz_to_offset import conllx_to_offset


def tag_collector(input_files, tag_index=0):
    all_tag_set = set()
    for sentence in iterator_reader(input_files):
        tag_set = {i for i in sentence.attribute_lines[tag_index]}

        all_tag_set.update(tag_set)

    return all_tag_set


def collect_tag_to_file(input_files, output_file, tag_index=0):
    all_tags = tag_collector(input_files, tag_index)

    # for better human reading, sort it
    all_tags_except_oscar = all_tags - {'O'}

    sorted_all_tags = ['O'] + sorted(all_tags_except_oscar)

    with open(output_file, 'wt') as fd:
        fd.write('\n'.join(sorted_all_tags))


def entity_collector(input_files, tag_index=0):
    all_tag_set = set()
    for sentence in conllx_iterator_reader(input_files):
        offset_sentence, _ = conllx_to_offset(sentence)
        tag_set = {i.entity for i in offset_sentence.span_set}

        all_tag_set.update(tag_set)

    return all_tag_set


def collect_entity_to_file(input_files, output_file, tag_index=0):
    all_tags = entity_collector(input_files, tag_index)

    # for better human reading, sort it
    all_tags_except_oscar = all_tags - {'O'}

    sorted_all_tags = sorted(all_tags_except_oscar)

    with open(output_file, 'wt') as fd:
        fd.write('\n'.join(sorted_all_tags))


def label_collector(input_files, tag_index=0):
    all_tag_set = set()
    for sentence in conllx_iterator_reader(input_files):
        offset_sentence, _ = conllx_to_offset(sentence)
        tag_set = {offset_sentence.label}

        all_tag_set.update(tag_set)

    return all_tag_set


def collect_label_to_file(input_files, output_file, tag_index=0):
    all_tags = label_collector(input_files, tag_index)

    # for better human reading, sort it
    all_tags_except_oscar = all_tags - {'O'}

    sorted_all_tags = sorted(all_tags_except_oscar)

    with open(output_file, 'wt') as fd:
        fd.write('\n'.join(sorted_all_tags))
