from __future__ import division

import math

import cv2
import numpy as np

from CrystalMatch.dls_util.shape import Rectangle, Point
from CrystalMatch.dls_util.imaging.color import Color


class Image:
    """Class that wraps an OpenCV image and can perform various operations on it that are useful
    in this program.
    """
    def __init__(self, img):
        self._img = img
        self._file = None

    def get_file(self):
        return self._file

    def raw(self):
        return self._img

    def width(self):
        return self._img.shape[1]

    def height(self):
        return self._img.shape[0]

    def size(self):
        return self.width(), self.height()

    def bounds(self):
        """ Return a rectangle that bounds the image (0,0,w,h). """
        return Rectangle(Point(), Point(self.width(), self.height()))

    def channels(self):
        """ Number of image color channels (1=mono, 3=rgb, 4=rgba). """
        shape = self._img.shape
        if len(shape) > 2:
            return shape[2]
        else:
            return 1

    def save(self, filename):
        """ Write the image to file. """
        cv2.imwrite(filename, self._img)

    @staticmethod
    def from_file(filename):
        """ Create a new image by reading from file. """
        raw_img = cv2.imread(filename)

        if raw_img is None:
            raise ValueError("Could not read specified Image File: {}".format(filename))

        image = Image(raw_img)
        image._file = filename
        return image

    @staticmethod
    def blank(width, height, channels=3, color=Color.black()):
        """ Return a new empty image of the specified size. """
        blank = Image(np.full((height, width, channels), 0, np.uint8))
        blank.draw_rectangle(blank.bounds(), color, thickness=-1)
        return blank

    def popup(self, title='Popup Image', block=True):
        """ Pop up a window to display an image until a key is pressed (blocking)."""
        cv2.imshow(title, self._img)
        if block:
            cv2.waitKey(0)
            cv2.destroyWindow(title)
        else:
            cv2.waitKey(1)

    def copy(self):
        """ Return an Image object which is a deep copy of this one. """
        return Image(self._img.copy())

    def crop(self, rect):
        """ Return a new image which is a region of this image specified by the rectangle. """
        rect = rect.intersection(self.bounds()).intify()
        sub = self._img[rect.y1:rect.y2, rect.x1:rect.x2]
        return Image(sub)

    def resize(self, new_size):
        """ Return a new Image that is a resized version of this one. """
        resized_img = cv2.resize(self._img, new_size)
        return Image(resized_img)

    def rescale(self, factor):
        """ Return a new Image that is a version of this image, resized to the specified scale. """
        scaled_size = (int(self.width() * factor), int(self.height() * factor))
        return self.resize(scaled_size)

    def paste(self, src, point):
        """ Paste the source image onto the target one at the specified position. If any of the
        source is outside the bounds of this image, it will be lost. """
        x_off, y_off = point.intify().tuple()

        # Overlap rectangle in target image coordinates
        width, height = src.size()
        x1 = max(x_off, 0)
        y1 = max(y_off, 0)
        x2 = min(x_off+width, self.width())
        y2 = min(y_off+height, self.height())

        # Paste location is totally outside image
        if x1 > x2 or y1 > y2:
            return

        # Overlap rectangle in source image coordinates
        sx1 = x1 - x_off
        sy1 = y1 - y_off
        sx2 = x2 - x_off
        sy2 = y2 - y_off

        # Perform paste
        target = self._img
        source = src.to_channels(self.channels()).raw()

        if self.channels() == 4:
            # Use alpha blending
            alpha = 3
            for c in range(0, 3):
                target[y1:y2, x1:x2, c] = source[sy1:sy2, sx1:sx2, c] * (source[sy1:sy2, sx1:sx2, alpha] / 255.0) \
                                          + target[y1:y2, x1:x2, c] * (1.0 - source[sy1:sy2, sx1:sx2, alpha] / 255.0)

            target[y1:y2, x1:x2, alpha] = np.full((y2-y1, x2-x1), 255, np.uint8)

        else:
            # No alpha blending
            target[y1:y2, x1:x2] = source[sy1:sy2, sx1:sx2]

    def rotate(self, angle, center):
        """ Rotate the image around the specified center. Note that this will
        cut off any areas that are rotated out of the frame.
        """
        degrees = angle * 180 / math.pi
        matrix = cv2.getRotationMatrix2D(center, degrees, 1.0)

        rotated = cv2.warpAffine(self._img, matrix, (self.width(), self.height()))
        return Image(rotated)

    def rotate_no_clip(self, angle):
        """Rotate the image about its center point, but expand the frame of the image
        so that the whole rotated shape will be visible without any being cropped.
        """
        # Calculate the size the expanded image needs to be to contain rotated image
        x, y = self.size()
        w = abs(x*math.cos(angle)) + abs(y*math.sin(angle))
        h = abs(x*math.sin(angle)) + abs(y*math.cos(angle))

        # Paste the image into a larger frame and rotate
        image = Image.blank(w, h, 4, 0)
        image.paste(self, w/2-x/2, h/2-y/2)
        rotated = image.rotate(angle, (w/2, h/2))

        return rotated

    ############################
    # Colour Space Conversions
    ############################
    def to_channels(self, num_channels):
        """ Return image converted to specified number of channels. """
        if num_channels == 1:
            return self.to_mono()
        elif num_channels == 3:
            return self.to_color()
        elif num_channels == 4:
            return self.to_alpha()
        else:
            return None

    def to_mono(self):
        """ Return a grayscale version of the image. """
        if self.channels() == 3:
            mono = cv2.cvtColor(self._img, cv2.COLOR_BGR2GRAY)
        elif self.channels() == 4:
            mono = cv2.cvtColor(self._img, cv2.COLOR_BGRA2GRAY)
        else:
            mono = self._img
        return Image(mono)

    def to_color(self):
        """Convert the image into a 3 channel BGR image. """
        if self.channels() == 1:
            color = cv2.cvtColor(self._img, cv2.COLOR_GRAY2BGR)
        elif self.channels() == 4:
            color = cv2.cvtColor(self._img, cv2.COLOR_BGR2BGRA)
        else:
            color = self._img
        return Image(color)

    def to_alpha(self):
        """Convert the image into a 4 channel BGRA image. """
        if self.channels() == 1:
            alpha = cv2.cvtColor(self._img, cv2.COLOR_GRAY2BGRA)
        elif self.channels() == 3:
            alpha = cv2.cvtColor(self._img, cv2.COLOR_BGR2BGRA)
        else:
            alpha = self._img
        return Image(alpha)

    ############################
    # Drawing Functions
    ############################
    def draw_dot(self, point, color=Color.black(), thickness=5):
        """ Draw the specified dot on the image (in place) """
        cv2.circle(self._img, point.intify().tuple(), 0, color.bgra(), thickness)

    def draw_circle(self, point, radius, color=Color.black(), thickness=2):
        """ Draw the specified circle on the image (in place) """
        cv2.circle(self._img, point.intify().tuple(), int(radius), color.bgra(), thickness)

    def draw_rectangle(self, rect, color=Color.black(), thickness=1):
        """ Draw the specified rectangle on the image (in place) """
        tl, br = rect.intify().top_left().tuple(), rect.intify().bottom_right().tuple()
        cv2.rectangle(self._img, tl, br, color.bgra(), thickness=thickness)

    def draw_line(self, pt1, pt2, color=Color.black(), thickness=2):
        """ Draw the specified line on the image (in place) """
        cv2.line(self._img, pt1.intify().tuple(), pt2.intify().tuple(), color.bgra(), thickness=thickness)

    def draw_polygon(self, points, color=Color.black(), thickness=2):
        """ Draw a polygon with vertices given by points. """
        i = 0
        while i < len(points) - 1:
            self.draw_line(points[i], points[i + 1], color, thickness)
            i += 1

        self.draw_line(points[i], points[0], color, thickness)

    def draw_text(self, text, point, color=Color.black(), centered=False, scale=1.5, thickness=3):
        """ Draw the specified text on the image (in place) """
        position = point
        if centered:
            size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontScale=scale, thickness=thickness)[0]
            position = point + Point(-size[0]/2, +size[1]/2)

        position = position.intify().tuple()
        cv2.putText(self._img, text, position, cv2.FONT_HERSHEY_SIMPLEX, scale, color.bgra(), thickness)

    def draw_cross(self, point, color=Color.black(), size=5, thickness=1):
        """ Draw an X on the image (in place). """
        self.draw_line(point - Point(size, size), point + Point(size, size), color, thickness)
        self.draw_line(point + Point(size, -size), point + Point(-size, size), color, thickness)

    def freq_range(self, coarseness_range, scale_factor):
        """Copy an image, discarding all but a range of frequency components.

        E.g. for a coarseness range of (1, 50), only features with sizes between 1
        and 50 pixels are retained (providing `working_size_factor == 1`).

        `1.0/working_size_factor` is used as a prefactor to the coarseness range
        bounds. This is useful for the purposes of the implementation of
        `find_tr()`. (A full-sized `img` should be passed in, regardless of whether
        `working_size_factor == 1`.)
        """
        (c_lo, c_hi) = coarseness_range
        lower = int(c_lo/scale_factor)
        upper = int(c_hi/scale_factor)

        a = cv2.blur(self._img, (lower, lower))
        b = cv2.blur(self._img, (upper, upper))

        grain_extract = np.subtract(a, b) + 128

        return Image(grain_extract)


