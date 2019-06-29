model_saver_mapping = {}


def registry_model_saver(data_source_scheme, corpus_processor_class):
    model_saver_mapping[data_source_scheme] = corpus_processor_class


def get_model_saver(data_source_scheme):
    return model_saver_mapping[data_source_scheme]


class ModelSaver(object):
    def __init__(self, config):
        self.config = config
        model_saver_class = get_model_saver(config.get('model_saver_scheme', 'raw'))
        self.model_saver = model_saver_class(config)

    def save_model(self, *args, **kwargs):
        self.model_saver.save_model(*args, **kwargs)


from ioflow.model_saver.raw_model_saver import RawModelSaver
registry_model_saver('raw', RawModelSaver)

from ioflow.model_saver.http_based_model_saver import HttpBasedModelSaver
registry_model_saver('http', HttpBasedModelSaver)
