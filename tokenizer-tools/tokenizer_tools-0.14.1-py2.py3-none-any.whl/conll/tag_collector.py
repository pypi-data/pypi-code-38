from tokenizer_tools.conll.iterator_reader import iterator_reader


def tag_collector(input_files, tag_index=1):
    all_tag_set = set()
    for sentence in iterator_reader(input_files):
        tag_set = {i[tag_index] for i in sentence}

        all_tag_set.update(tag_set)

    return all_tag_set


def collect_tag_to_file(input_files, output_file, tag_index=1):
    all_tags = tag_collector(input_files, tag_index)

    # for better human reading, sort it
    all_tags_except_oscar = all_tags - {'O'}

    sorted_all_tags = ['O'] + sorted(all_tags_except_oscar)

    with open(output_file, 'wt') as fd:
        fd.write('\n'.join(sorted_all_tags))
