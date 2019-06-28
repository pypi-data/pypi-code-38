from __future__ import division

from CrystalMatch.dls_util.shape import Point
from CrystalMatch.dls_util.imaging import Image, Color


class MatchPainter:
    """ Creates images illustrating the results of the feature match process. The resulting image shows the two
    images side-by-side with lines drawn between them indicating the matches.

    In addition, the image can contain the location of a point in image1 with its corresponding transform in
    image 2 as well as a rectangle from image 1 with its corresponding transformed shape in image 2.
    """
    DEFAULT_IMAGE_SIZE = 900
    DEFAULT_PADDING = 5
    DEFAULT_BACK_COLOR = Color.black()

    IMAGE_1 = 1
    IMAGE_2 = 2

    def __init__(self, image1, image2):
        self._image1 = image1
        self._image2 = image2

        self._image1_position = Point(0, 0)
        self._image2_position = Point(0, 0)
        self._scale_factor = 1
        self._background_image = None

        self._image_size = self.DEFAULT_IMAGE_SIZE
        self._padding = self.DEFAULT_PADDING
        self._back_color = self.DEFAULT_BACK_COLOR

        self._create_background_image()

    # -------- CONFIGURATION -------------------
    def set_image_size(self, size):
        """ Set the maximum size of the background image (should be a Point instance). """
        self._image_size = size
        self._create_background_image()

    def set_padding(self, padding):
        """ Set the number of pixels of padding between images 1 and 2 in the background image. """
        self._padding = padding
        self._create_background_image()


    # -------- FUNCTIONALITY -------------------
    def background_image(self):
        """ Get the background image (images 1 and 2 side-by-side) without any other markings (e.g. matches, etc.)"""
        return self._background_image.copy()

    def _create_background_image(self):
        """ Create the background image, which consists of the two images side-by-side with a colored backdrop.
        This must be recreated if the image size, padding, or background color changes. """
        self._calculate_image_positions()

        w, h = self._calculate_background_image_size()
        image = Image.blank(w, h)
        image.paste(self._image1, self._image1_position)
        image.paste(self._image2, self._image2_position)

        image, factor = self._rescale_to_max_size(image)
        self._background_image = image
        self._scale_factor = factor

    def _calculate_image_positions(self):
        """ Determine the positions of images 1 and 2 in the background image. """
        pad = self._padding
        w1, h1 = self._image1.size()
        w2, h2 = self._image2.size()

        self._image1_position = Point(pad, pad)
        self._image2_position = Point(2 * pad + w1, pad)

        if h2 > h1:
            self._image1_position += Point(0, pad + 0.5 * (h2 - h1))
        elif h2 > h1:
            self._image2_position += Point(0, pad + 0.5 * (h1 - h2))

    def _calculate_background_image_size(self):
        """ Determine the sizes of images 1 and 2 as displayed in the background image. """
        pad = self._padding
        w1, h1 = self._image1.size()
        w2, h2 = self._image2.size()

        w_bg = w1 + w2 + 3 * pad
        h_bg = 2 * pad + max(h1, h2)
        return w_bg, h_bg

    def _rescale_to_max_size(self, image):
        """ Resize the background image so that it fills up the maximum available space. """
        width, height = image.size()
        factor = self._image_size / max(width, height)
        rescaled = image.rescale(factor)
        return rescaled, factor

    def _point_to_image_coords(self, point, image_num):
        """ Convert a point on image 1 or 2 to a coordinate in the background image. """
        image_position = self._get_image_position(image_num)
        return (point + image_position) * self._scale_factor

    def _polygon_to_image_coords(self, polygon, image_num):
        """ Convert a polygon on image 1 or 2 to a polygon in the background image. """
        image_position = self._get_image_position(image_num)
        return polygon.offset(image_position).scale(self._scale_factor)

    def _get_image_position(self, num):
        """ Get the position of the specified image. """
        return self._image2_position if num == self.IMAGE_2 else self._image1_position

