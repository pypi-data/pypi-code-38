class ModelSaverBase(object):
    def __init__(self, config):
        self.config = config

    def save_model(self, model_path):
        raise NotImplementedError
