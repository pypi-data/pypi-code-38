from ioflow.corpus import Corpus
from ioflow.corpus_processor.corpus_processor_base import CorpusProcessorBase


class RawCorpusProcessor(CorpusProcessorBase):
    def __init__(self, config):
        super(RawCorpusProcessor, self).__init__(config)
        self.dataset_mapping = {}

    def prepare(self):
        self.dataset_mapping[Corpus.TRAIN] = self.config[
            'corpus_train_input_func']
        self.dataset_mapping[Corpus.EVAL] = self.config[
            'corpus_eval_input_func']

    def get_generator_func(self, data_set):
        return self.dataset_mapping[data_set]

    def get_meta_info(self):
        return self.config['corpus_meta_info']
