import cv2

from CrystalMatch.dls_util.shape import Rectangle, Point
from CrystalMatch.dls_util.imaging import Image, Color


class Overlayer:
    def __init__(self):
        pass

    @staticmethod
    def create_overlay_image(image1, image2, offset, rect_color=Color.black()):
        """ For the two images, A and B, where the position of B is offset from that of A, overlay
        image B onto image A at the appropriate position. The overlaid area will ve a blending of the
        two images. A rectangle will be drawn around the area.
        """
        # Make a copy of A, the background image
        background = image1.copy()

        # Get overlapping regions of images
        overlap_a, overlap_b = Overlayer.get_overlap_regions(image1, image2, offset)
        if overlap_a is None or overlap_b is None:
            return background

        # Blend the two overlapping regions
        perc_a, perc_b = 0.5, 0.5
        blended = cv2.addWeighted(overlap_a.raw(), perc_a, overlap_b.raw(), perc_b, 0)
        background.paste(Image(blended), Point(max(offset.x, 0), max(offset.y, 0)))
        background = background.to_channels(3)

        # Define the rectangle that will be pasted to the background image
        w, h = image2.size()
        rect = Rectangle.from_corner(offset, w, h)
        background.draw_rectangle(rect, color=rect_color)

        return background

    @staticmethod
    def get_overlap_regions(image1, image2, offset):
        """ For the two images, A and B, where the position of B is offset from that of A,
        return two new images that are the overlapping segments of the original images.

        As a simple example, if image B is smaller than A and it is completely contained
        within the borders of the image A, then we will simply return the whole of image B,
        and the section of image A that it overlaps. e.g., if A is 100x100 pixels, B is
        14x14 pixels, and the offset is (x=20, y=30), then the returned section of A will
        be (20:34, 30:44).

        If image B only partially overlaps image A, only the overlapping sections of each
        are returned.
        """
        rect_a = image1.bounds()
        rect_b = image2.bounds().offset(offset)
        overlap_a_rect = rect_a.intersection(rect_b)
        overlap_a = image1.crop(overlap_a_rect)

        rect_a = image1.bounds().offset(-offset)
        rect_b = image2.bounds()
        overlap_b_rect = rect_a.intersection(rect_b)
        overlap_b = image2.crop(overlap_b_rect)

        return overlap_a, overlap_b
