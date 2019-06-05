
from CrystalMatch.dls_util.imaging import Image
from CrystalMatch.dls_util.shape import Rectangle


class PointFFT:
    """
    Initialise a new pointfft object which allows to calculate fft within an region of a given size.
    :param point: point for which the fft can be calculated
    :param fftimage: image (array) from which a region of interest is cropped
    :param region size: size of region taken to calculate fft - it is a square (size x size)
    """

    def __init__(self, point, img, region_size):
        self.point = point
        self.fft_level = None
        self.image_number = None
        self.image_name = None
        self.img = img
        self.region_size = region_size

    def getFFT(self):
        return self.fft_level

    def setFFT(self, level):
        self.fft_level = level

    def crop_region_from_image(self):
        region = Rectangle.from_center(self.point, self.region_size, self.region_size)
        img = Image(self.img).crop(region)
        return img.raw()

    def set_image_number(self, num):
        self.image_number = num

    def set_image_name(self, name):
        self.image_name = name

    def get_image_number(self):
        return self.image_number

    def get_image_name(self):
        return self.image_name
