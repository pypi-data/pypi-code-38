import logging
from multiprocessing import Pool

import cv2
import numpy as np

from CrystalMatch.dls_focusstack.focus.fourier import Fourier
from CrystalMatch.dls_imagematch import logconfig
from CrystalMatch.dls_focusstack.focus.imagefft import ImageFFT


def fft(param):
    "Function that reads an image of a given name and  starts fft calculation."
    #read as soon as it appears
    name = param[0]
    count = param[1]
    img_color = cv2.imread(name)
    img = cv2.cvtColor(img_color.astype(np.float32), cv2.COLOR_BGR2GRAY)
    image_fft = ImageFFT(img, count, name)
    level= Fourier(img).runFFT()
    image_fft.setFFT(level)
    log = logging.getLogger(".".join([__name__]))
    log.addFilter(logconfig.ThreadContextFilter())
    extra = ({'fft': image_fft.getFFT()})
    log = logging.LoggerAdapter(log, extra)
    log.info("Finished calculating fft for:" + name)
    log.debug(extra)
    return image_fft


class ImageFFTManager:
    """Class which manages fft calculations."""
    def __init__(self, name_list):
        self._image_file_list = name_list
        self.fft_images = []

    def read_ftt_images(self):
        """Function which starts fft calculation for each input image name.
        Multiprocessing is used to speed up the calculation.
        One process for one input image name."""
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        parameters = []
        for idx, file_obj in enumerate(self._image_file_list):
            #first image has index 0 
            param = (file_obj.name, idx)
            parameters.append(param)

        pool = Pool()
        results = pool.map_async(fft, parameters)
        self.fft_images = results.get()
        pool.close()
        pool.join()

    def get_fft_images(self):
        return self.fft_images
