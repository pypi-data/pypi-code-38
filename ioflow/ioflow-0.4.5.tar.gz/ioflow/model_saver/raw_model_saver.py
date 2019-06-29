from ioflow.model_saver.model_saver_base import ModelSaverBase


class RawModelSaver(ModelSaverBase):
    def save_model(self, model_path):
        print('{}:{}'.format(self.__class__, model_path))
