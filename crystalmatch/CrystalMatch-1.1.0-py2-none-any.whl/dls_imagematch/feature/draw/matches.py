from __future__ import division

import cv2

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

    def set_back_color(self, color):
        """ Set the background color. """
        self._back_color = color
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

    def draw_transform_points(self, image1_point, image2_point, image=None):
        """ Draw a cross at a point on image 1 and the corresponding transformed point on image 2. """
        if image is None:
            image = self._background_image.copy()

        if image1_point is not None:
            point1 = self._point_to_image_coords(image1_point, 1)
            image.draw_cross(point1, Color.green(), size=10, thickness=2)

        if image2_point is not None:
            point2 = self._point_to_image_coords(image2_point, 2)
            image.draw_cross(point2, Color.green(), size=10, thickness=2)

        return image

    def draw_transform_shapes(self, shape1, shape2, image=None):
        """ Draw a shape on image 1 and the corresponding transformed shape on image 2. """
        if image is None:
            image = self._background_image.copy()

        self._draw_shape(shape1, self.IMAGE_1, image)
        self._draw_shape(shape2, self.IMAGE_2, image)
        return image

    def _draw_shape(self, shape, image_num, image):
        """ Draw a polygon on the specified image. """
        if shape is not None:
            shape = self._polygon_to_image_coords(shape, image_num)
            for edge in shape.edges():
                image.draw_line(edge[0], edge[1], Color.orange(), thickness=2)

    def draw_matches(self, matches, highlight_matches=[], image=None):
        """ Draw lines for each of the matches between the respective points in the two images.
        Matches that are marked as included in the transformation will be colored blue whereas
        those not included will be alight grey. Highlighted matches will appear in yellow
        """
        if image is None:
            image = self._background_image.copy()

        for match in matches:
            color = Color.blue() if match.is_in_transformation() else Color.slate_gray()
            self._draw_match(image, match, color, thickness=1, radius=4)

        for match in highlight_matches:
            self._draw_match(image, match, Color.yellow(), thickness=2, radius=4)
            color = Color.blue() if match.is_in_transformation() else Color.slate_gray()
            self._draw_match(image, match, color, thickness=1, radius=4)

        return image

    def _draw_match(self, image, match, color, thickness, radius):
        """ Draw a single match on the image pair. """
        point1 = self._point_to_image_coords(match.image_point1(), 1)
        point2 = self._point_to_image_coords(match.image_point2(), 2)

        # Draw a small circle at both co-ordinates
        image.draw_circle(point1, radius, color, thickness)
        image.draw_circle(point2, radius, color, thickness)

        # Draw a line between the two points
        image.draw_line(point1, point2, color, thickness)

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

    @staticmethod
    def draw_keypoints(image, keypoints):
        """ Draw the list of keypoints to the specified image and display it as a popup window. """
        marked_image = cv2.drawKeypoints(image.raw(), keypoints, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        return Image(marked_image)
