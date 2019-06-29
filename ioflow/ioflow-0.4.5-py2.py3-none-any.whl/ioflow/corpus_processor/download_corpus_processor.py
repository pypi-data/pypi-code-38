import functools
import json

import numpy as np

from ioflow.corpus_processor.corpus_processor_base import CorpusProcessorBase
from ioflow.corpus import Corpus
from ioflow.corpus_processor.download_file import download_file

from tokenizer_tools.tagset.offset.sequence import Sequence
from tokenizer_tools.tagset.offset.span import Span


def parse_corpus_to_offset(corpus_item):
    seq = Sequence(corpus_item['text'], label=corpus_item['classifications']['intent'], id=corpus_item['id'])
    for entity in corpus_item['annotations']['entity']:
        span = Span(
            int(entity['start']), int(entity['start']) + int(entity['length']),
            entity['type']
        )

        # get value which is not in corpus_item object
        span.fill_text(corpus_item['text'])

        seq.span_set.append(span)

    return seq


def generator_fn(input_file):
    with open(input_file) as fd:
        for corpus_string in fd:
            corpus_item = json.loads(corpus_string)
            offset_data = parse_corpus_to_offset(corpus_item)

            yield offset_data


def corpus_download(config):
    corpus_file = download_file(config['corpus_download_url'], params={"trainId": config['task_id']})
    return corpus_file


class DownloadCorpusProcessor(CorpusProcessorBase):
    def __init__(self, config):
        super(DownloadCorpusProcessor, self).__init__(config)
        self.dataset_mapping = {}

    def prepare(self):
        corpus_file = corpus_download(self.config)

        self.dataset_mapping[Corpus.TRAIN] = functools.partial(generator_fn, corpus_file)
        self.dataset_mapping[Corpus.EVAL] = functools.partial(generator_fn, corpus_file)

    def get_generator_func(self, data_set):
        return self.dataset_mapping[data_set]

    def get_meta_info(self):
        return {
            "tags": np.loadtxt(self.config['tags'], dtype=np.unicode, encoding=None) if self.config.get('tags') else None,
            "labels": np.loadtxt(self.config['labels'], dtype=np.unicode, encoding=None) if self.config.get('labels') else None
        }
