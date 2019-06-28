def read_conll_iterator(conll_file):
    with open(conll_file) as fd:
        while True:

            content = fd.read()

            raw_sentence_list = content.split('\n\n')

            for raw_sentence in raw_sentence_list:
                cleaned_sentence = raw_sentence.strip()

                if not cleaned_sentence:
                    # skip
                    continue

                sentence = []
                raw_line_list = raw_sentence.split('\n')
                for raw_line in raw_line_list:
                    line = raw_line.strip()
                    item = line.split()

                    if not item:
                        # skip
                        continue

                    sentence.append(item)

                yield sentence

            break


def iterator_reader(input_file_list):
    for input_file in input_file_list:
        for i in read_conll_iterator(input_file):
            yield i
