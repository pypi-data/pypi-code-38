import copy
import io
import json
import uuid
from typing import List

from tokenizer_tools.conllz.sentence import Sentence, SentenceX


def write_conllx(sentence_list: List[SentenceX], output_fd):
    for sentence in sentence_list:
        sentence_id = sentence.id

        for index, row in enumerate(sentence.read_as_row()):
            if index == 0:  # only write at head
                sentence_id = sentence_id if sentence_id else str(uuid.uuid4())
                meta = copy.deepcopy(sentence.meta)
                meta.update({'id': sentence_id})
                meta_string = json.dumps(meta, ensure_ascii=False)
                output_fd.write('{}\n'.format('\t'.join(['#', meta_string])))

            output_fd.write('{}'.format("\t".join(row)))
            output_fd.write('\n')

        output_fd.write('\n')


def write_conllz(sentence_list, output_fd):
    for sentence in sentence_list:
        sentence_id = sentence.id

        for index, row in enumerate(sentence.read_as_row()):
            if index == 0:  # only write at head
                sentence_id = sentence_id if sentence_id else str(uuid.uuid4())
                output_fd.write('{}\n'.format('\t'.join(['#', sentence_id])))

            output_fd.write('{}'.format("\t".join(row)))
            output_fd.write('\n')

        output_fd.write('\n')


if __name__ == "__main__":
    gold = "#\tSID-1\nchar-1\ttag-1\nchar-2\ttag-2\n\n#\tSID-2\nchar-1\ttag-1\nchar-2\ttag-2\n\n"""
    sentence_1 = Sentence()
    sentence_1.id = 'SID-1'
    sentence_1.write_as_row(['char-1', 'tag-1'])
    sentence_1.write_as_row(['char-2', 'tag-2'])

    sentence_2 = Sentence()
    sentence_2.id = 'SID-2'
    sentence_2.write_as_row(['char-1', 'tag-1'])
    sentence_2.write_as_row(['char-2', 'tag-2'])

    with io.StringIO() as fd:
        write_conllz([sentence_1, sentence_2], fd)

        output = fd.getvalue()
        assert output == gold
