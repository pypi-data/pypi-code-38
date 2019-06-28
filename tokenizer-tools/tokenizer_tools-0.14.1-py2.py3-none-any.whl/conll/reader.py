def read_conll(conll_file, sep='\t'):
    sentence_list = []
    with open(conll_file) as fd:
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
                line = raw_line
                # line = raw_line.strip()
                item = line.split(sep)

                if not item:
                    # skip
                    continue

                sentence.append(item)

            sentence_list.append(sentence)

    return sentence_list


if __name__ == "__main__":
    sentence = read_conll('test.conllu')
    print(sentence)
