from __future__ import division

from CrystalMatch.dls_util.imaging import Image


class SizedImage(Image):
    """ Extended Image class which also keeps track of the real size of a pixel in the image.
    """
    def __init__(self, img, pixel_size):
        Image.__init__(self, img)

        # The real size represented by a single pixel in the image
        self._pixel_size = pixel_size

    def pixel_size(self):
        return self._pixel_size

    @staticmethod
    def from_image(image, pixel_size):
        sized_image = SizedImage(image.raw(), pixel_size)
        sized_image.set_file(image.get_file())
        return sized_image

    @staticmethod
    def from_file(filename, pixel_size=0):
        image = Image.from_file(filename)
        return SizedImage(image, pixel_size)

    def copy(self):
        return SizedImage(self._img.copy(), self._pixel_size)

    def crop(self, rect):
        image = Image.crop(self, rect)
        return self.from_image(image, self._pixel_size)

    def resize(self, new_size):
        image = Image.resize(self, new_size)

        # Because the image must be an integer number of pixels, we must correct the
        # factor to calculate the pixel size properly.
        corrected_factor = new_size[0] / self.width()
        pixel_size = self._pixel_size / corrected_factor

        return self.from_image(image, pixel_size)

    def rotate(self, angle, center):
        image = Image.rotate(self, angle, center)
        return self.from_image(image, self._pixel_size)

    def to_mono(self):
        image = Image.to_mono(self)
        return self.from_image(image, self._pixel_size)

    def to_color(self):
        image = Image.to_color(self)
        return self.from_image(image, self._pixel_size)

    def to_alpha(self):
        image = Image.to_alpha(self)
        return self.from_image(image, self._pixel_size)

    def freq_range(self, coarseness_range, scale_factor):
        image = Image.freq_range(self, coarseness_range, scale_factor)
        return self.from_image(image, self._pixel_size)

    def set_file(self, image_file):
        self._file = image_file
