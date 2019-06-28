from tokenizer_tools.tagset import get_encoder_decoder


def plain_token_to_conll(plain_token_file, conll_file, tagset='BMES', include_id=False):
    encoder_decoder = get_encoder_decoder(tagset)

    with open(plain_token_file) as in_fd, open(conll_file, 'wt') as out_fd:
        for raw_line in in_fd:
            # initial conll content
            conll_line = []

            # try to clean
            line = raw_line.strip()
            for word in line.split():
                tag_code = encoder_decoder.encode_word(word)

                conll_line.append([word, tag_code])

            word_list_and_tag_list = list(map(lambda x: ''.join(x), zip(*conll_line)))
            word_tag_list = list(zip(*word_list_and_tag_list))

            for id, (word, tag) in enumerate(word_tag_list):
                if include_id:
                    out_fd.write("{}\t{}\t{}\n".format(id, word, tag))
                else:
                    out_fd.write("{}\t{}\n".format(word, tag))
            out_fd.write("\n")
