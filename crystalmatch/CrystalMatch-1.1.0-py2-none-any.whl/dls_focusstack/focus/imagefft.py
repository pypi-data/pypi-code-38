
class ImageFFT:
    """Class which holds the image, mean_fft_value and image index in a sequence of images.
     Mean value of the image FFT is held in the fft_level parameter.
     :param input_img: an image array
     :param number: index of th image in the list of images passed
     :param name: names of the file - an absolute path"""

    def __init__(self, input_img, number, name):
        self.img = input_img
        self.image_number = number
        self.fft_level = None
        self.name = name

    def setFFT(self, fft_level):
        self.fft_level = fft_level

    def getFFT(self):
        return self.fft_level

    def get_image(self):
        return self.img

    def get_image_number(self):
        #first image has index 0
        return self.image_number

    def get_image_name(self):
        return self.name


