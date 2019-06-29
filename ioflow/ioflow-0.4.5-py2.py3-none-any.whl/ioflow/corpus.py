corpus_processor_mapping = {}


def registry_corpus_processor(data_source_scheme, corpus_processor_class):
    corpus_processor_mapping[data_source_scheme] = corpus_processor_class


def get_corpus_processor(data_source_scheme):
    return corpus_processor_mapping[data_source_scheme]


class Corpus(object):
    EVAL = 'eval'
    TRAIN = 'train'

    def __init__(self, config):
        self.config = config
        self.dataset_mapping = {}
        corpus_processor_class = get_corpus_processor(config['data_source_scheme'])
        self.corpus_processor = corpus_processor_class(config)

    def prepare(self):
        return self.corpus_processor.prepare()

    def get_generator_func(self, data_set):
        return self.corpus_processor.get_generator_func(data_set)

    def get_meta_info(self):
        return self.corpus_processor.get_meta_info()


from ioflow.corpus_processor.raw_corpus_processor import RawCorpusProcessor
registry_corpus_processor('raw', RawCorpusProcessor)

from ioflow.corpus_processor.local_corpus_processor import LocalCorpusProcessor
registry_corpus_processor('local', LocalCorpusProcessor)

from ioflow.corpus_processor.http_corpus_processor import HttpCorpusProcessor
registry_corpus_processor('http', HttpCorpusProcessor)