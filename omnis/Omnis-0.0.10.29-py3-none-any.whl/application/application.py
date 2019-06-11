from keras.models import load_model

import numpy
import cv2

import os
import platform


class Application(object):

    def __init__(self):
        try:
            self.os_type = platform.system()
        except Exception as e:
            print("Application initialize failed")
            raise e
        # default setting for using 1gpu and gpu_ids for 0
        self.gpu_num = 1
        self.gpu_ids = [0]
        self.deepblock_log = False

    def use_specific_gpus(self, gpuids):
        self.gpu_ids = gpuids
        self.gpu_num = len(gpuids)

    def use_deepblock_site_log(self, use_or_not=False):
        self.deepblock_log = use_or_not