from keras import backend as K
import keras

from keras.preprocessing.image import load_img, img_to_array
import numpy as np
from scipy.optimize import fmin_l_bfgs_b
import time
import os
import skimage
import cv2
from ...application import Application

from multiprocessing import Process, Queue
from .style_transfer_worker import Style_Transfer_Worker


class Style_Transfer(Application):
    def __init__(self):
        super().__init__()

        # This application does not support Window now
        if self.os_type == "Window":
            raise ValueError("This application does not support window yet")
        self.loss_value = None
        self.grad_values = None
        self._queue = Queue()

    def prepare_train_data(
            self,
            get_content_image_from='directory',
            content_image_path=None,
            get_style_image_as='filepath',
            style_image_path=None):
        assert get_content_image_from in [
            "directory", "argument"], "get_content_image_from should be either 'directory' or 'argument'."
        assert get_style_image_as in [
            "filepath", "ndarray"], "get_style_image_as should be either 'filepath' or 'ndarray'."

        self._workers = list()
        for gpuid in self.gpu_ids:
            self._workers.append(Style_Transfer_Worker(
                gpuid=gpuid,
                queue=self._queue,
                get_content_image_from=get_content_image_from,
                get_style_image_as=get_style_image_as,
                content_image_path=content_image_path,
                style_image_path=style_image_path,
                use_deepblock_log=self.deepblock_log))

        # scan all files under get_content_image_path
        for content_file in os.listdir(content_image_path):
            self._queue.put(os.path.join(content_image_path, content_file))
        self._queue.put(None)

    def generate(
            self,
            iterations=10,
            output_type="file",
            output_path="result",
            total_variation_weight=1.0,
            style_weight=1.0,
            content_weight=0.025):
        for worker in self._workers:
            worker.output_type = output_type
            worker.output_path = output_path
            worker.iterations = iterations
            worker.style_weight = style_weight
            worker.content_weight = content_weight
            worker.total_variation_weight = total_variation_weight

        for worker in self._workers:
            worker.start()

        for worker in self._workers:
            worker.join()

        print("all of workers have been done")
