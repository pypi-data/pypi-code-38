class CorpusProcessorBase(object):
    def __init__(self, config):
        self.config = config

    def prepare(self):
        pass

    def get_generator_func(self, data_set):
        raise NotImplementedError

    def get_meta_info(self):
        return NotImplementedError
