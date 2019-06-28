import json
from collections import OrderedDict

from keras.callbacks import Callback


class ImageClassificationCallback(Callback):
    def __init__(self, total_step, total_epoch):
        Callback.__init__(self)
        self.step = 1
        self.epoch = 1
        self.total_step = total_step
        self.total_epoch = total_epoch

    def on_batch_end(self, batch, logs=None):
        if logs is None: logs = {}
        log_json = OrderedDict()
        log_json['logType'] = "batchend"
        log_json['totalStep'] = self.total_step
        log_json['nowStep'] = self.step
        log_json['totalEpoch'] = self.total_epoch
        log_json['nowEpoch'] = self.epoch
        log_json['loss'] = str(logs.get('loss'))
        log_json['acc'] = str(logs.get('acc'))
        print(json.dumps(log_json, ensure_ascii=False))
        self.step += 1

    def on_epoch_end(self, epoch, logs=None):
        if logs is None: logs = {}
        self.step = 1
        log_json = OrderedDict()
        log_json['logType'] = "epochend"
        log_json['totalEpoch'] = self.total_epoch
        log_json['nowEpoch'] = self.epoch
        log_json['loss'] = str(logs.get('loss'))
        log_json['acc'] = str(logs.get('acc'))
        print(json.dumps(log_json, ensure_ascii=False))
        self.epoch += 1
