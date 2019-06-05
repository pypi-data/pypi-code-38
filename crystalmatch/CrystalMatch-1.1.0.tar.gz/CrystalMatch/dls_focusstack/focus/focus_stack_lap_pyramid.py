import logging
from CrystalMatch.dls_imagematch import logconfig
import time

import cv2
import numpy as np

from CrystalMatch.dls_focusstack.config.focus_config import FocusConfig
from CrystalMatch.dls_util.imaging import Image
from CrystalMatch.dls_focusstack.focus.image_fft_manager import ImageFFTManager
from os.path import join, abspath

from CrystalMatch.dls_focusstack.focus.pyramid_manager import PyramidManager
from CrystalMatch.dls_focusstack.focus.sharpness_detector import SharpnessDetector


class FocusStack:
    CONFIG_FILE_NAME = "focus_stack.ini"

    def __init__(self, images, config_dir):
        self._image_file_list = images
        self._config = FocusConfig(abspath(join(abspath(config_dir), self.CONFIG_FILE_NAME)))
        self.fft_images = None


    def composite(self):
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        extra = self._config.all_to_json()
        log = logging.LoggerAdapter(log, extra)
        log.info("Focusstack Started, first image, " + self._image_file_list[0].name)
        log.debug(extra)

        start_t = time.time()

        t1 = time.time()
        man = ImageFFTManager(self._image_file_list)
        man.read_ftt_images()
        sd = SharpnessDetector(man.get_fft_images(), self._config)

        images = sd.images_to_stack()
        self.fft_images = sd.get_fft_images_to_stack()

        t2 = time.time() - t1

        #add extra field to the log
        extra = {'FTT_time': t2}
        log = logging.LoggerAdapter(log, extra)
        log.info("FFT calculation finished")
        log.debug(extra)
        images = np.array(images, dtype=images[0].dtype)

        #TODO:Implement alignment algo
        #aligned_images, gray_images = self.align(images)

        #stacked_image = pyramid(aligned_images, self._config).get_pyramid_fusion()
        stacked_image = PyramidManager(images, self._config).get_pyramid_fusion()

        stacked_image  = cv2.convertScaleAbs(stacked_image)
        backtorgb = cv2.cvtColor(stacked_image, cv2.COLOR_GRAY2RGB)

        calculation_time = time.time() - start_t
        extra = {'stack_time': calculation_time}
        log = logging.LoggerAdapter(log, extra)
        log.info("Stacking Finished")
        log.debug(extra)

        return Image(backtorgb)

    def get_fft_images_to_stack(self):
        return self.fft_images





