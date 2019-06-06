# -*- coding: utf-8 -*-


class StateCounter(object):
    def __init__(self, callback):
        self.callback = callback
        self.epoch = 0
        self.batch = 0
        # batch count is one-indexed

    def begin_batch(self, epoch):
        # Infer current batch
        if epoch == self.epoch:
            if self.batch == 0:
                self.callback.epoch_begin(epoch)

            self.batch += 1
        else:
            if not (self.epoch == 0 and self.batch == 0):
                self.callback.epoch_end(self.epoch)

            self.epoch = epoch
            self.batch = 1

            self.callback.epoch_begin(epoch)

        self.callback.batch_begin(self.batch, self.epoch)

    def end_epoch(self, epoch):
        self.epoch = epoch
