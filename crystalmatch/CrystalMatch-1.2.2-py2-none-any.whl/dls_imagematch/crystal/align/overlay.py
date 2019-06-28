

class Overlayer:
    def __init__(self):
        pass

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
        offset = offset.intify() # VMXI-468 - round before cropping
        rect_a = image1.bounds()
        rect_b = image2.bounds().offset(offset)
        overlap_a_rect = rect_a.intersection(rect_b)
        overlap_a = image1.crop(overlap_a_rect)

        rect_a = image1.bounds().offset(-offset)
        rect_b = image2.bounds()
        overlap_b_rect = rect_a.intersection(rect_b)
        overlap_b = image2.crop(overlap_b_rect)

        return overlap_a, overlap_b
