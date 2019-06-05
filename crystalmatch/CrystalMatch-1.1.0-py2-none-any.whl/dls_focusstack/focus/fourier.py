
import cv2
import numpy as np

class Fourier:
    """
    Initialise a new fourier object.
    :param input_array: input for the fourier transform calculation
    """
    def __init__(self, input_array):
        self.array = input_array

    def runFFT(self):
        return self.fourier_bandpass()

    # algorithm provided by Charles
    def fourier_bandpass(self):
        """Function used to calcualte FFT of the image and apply a bandpass filter"""
        rows, cols = self.array.shape
        nrows = cv2.getOptimalDFTSize(rows)
        ncols = cv2.getOptimalDFTSize(cols)
        nimg = np.zeros((nrows, ncols))
        nimg[:rows, :cols] = self.array

        data_fft = np.fft.rfft2(nimg)
        fft_abs = np.abs(data_fft)

        h, w = fft_abs.shape
        l = int(min(h/2, w)) # rfft2 returns half the width of fft2
        min_l = 0.2 * l
        max_l = 0.6 * l

        def filter_indices(x, y, max_x, max_y):
            x2, y2 = x*x, y*y
            return (x > 0.05 * max_x) \
                    & (y > 0.05 * max_y) \
                    & (min_l * min_l < x2 + y2) \
                    & (x2 + y2 < max_l * max_l)

        # count values in a band around the "origin"
        # positive offsets start at [0, 0], negative at [h, 0] and go backwards
        indices = np.fromfunction(lambda y, x: filter_indices(y, x, h/2., w), (h, w))
        indices |= np.fromfunction(lambda y, x: filter_indices(h - y, x, h/2., w), (h, w))
        return np.sum(fft_abs[indices])
