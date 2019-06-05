from CrystalMatch.dls_imagematch.util.status import StatusFlag
from CrystalMatch.dls_util.imaging import Color
from CrystalMatch.dls_util.shape import Point
from CrystalMatch.dls_imagematch.crystal.align.metric_overlap import OverlapMetric
from CrystalMatch.dls_imagematch.crystal.align.overlay import Overlayer


class AlignedImagesStatus(StatusFlag):
    pass
# Status values
ALIGNED_IMAGE_STATUS_NOT_SET = AlignedImagesStatus(-1, "NOT SET")
ALIGNED_IMAGE_STATUS_OK = AlignedImagesStatus(1, "OK")
ALIGNED_IMAGE_STATUS_FAIL = AlignedImagesStatus(0, "FAIL")


class AlignedImages:
    """
    Represents a pair of images on which an alignment operation has been performed. The images should have the same
    real size per pixel.
    """
    def __init__(self, image1, image2, resolution, original_scale_factor, translation, align_config, method="Unknown"):
        """
        The images must have the same resolution - scale_factor is the value used to map image1 onto image2.
        The translation is the distance (in pixels) that the top-left corner of image B should be offset from the
        top-left corner of image A, in order to properly align the images. Together the translation and scale_factor
        describe the alignment transformation.
        :param image1: The before image - if rescaling was necessary it should have been done to this image!
        :param image2: The after image
        :param resolution: The shared resolution of the images
        :param original_scale_factor: Original scale factor used to rescale image1 to the resolution of image2.
        :param translation: The translation which maps a point in image 1 onto image 2
        :param align_config: Alignment configuration object.
        :param method: Description text for detector used.
        """
        self.image1 = image1
        self.image2 = image2
        self.method = method

        self.feature_match_result = None

        self._scale_factor = original_scale_factor
        self._resolution = resolution
        self._translation = translation
        self._limit_low = align_config.metric_limit_low.value()
        self._limit_high = align_config.metric_limit_high.value()

        self._real_offset = None
        self._pixel_offset = None
        self._real_center = None
        self._pixel_center = None
        self._overlay = None
        self._metric = None
        self._overlap_images = None

    def get_working_resolution(self):
        """
        Gets the pixel size for the aligned images, usually in micro-meters per pixel.
        :return: The resolution of the aligned images as a float value.
        """
        return self._resolution

    def is_alignment_good(self):
        """ If True the alignment metric is less than the low limit and the alignment is considered to
        be a good fit. """
        return self.overlap_metric() <= self._limit_low

    def is_alignment_poor(self):
        """ If True the alignment metric is between the 2 limits and the alignment is considered to be poor. """
        return self._limit_low < self.overlap_metric() <= self._limit_high

    def is_alignment_bad(self):
        """ If True, the alignment quality metric exceeds the top limit and the alignment is considered
        to have failed. """
        return self.overlap_metric() > self._limit_high

    def get_alignment_transform(self):
        """
        Return the scale and translation transform which must be applied to a point in image 1 to map it to image 2.
        :return: A scale factor float and a Point() object offset.
        """
        return self._scale_factor, self.pixel_offset()

    def pixel_offset(self):
        """ The translation (offset) in pixels - nearest whole number. """
        if self._pixel_offset is None:
            self._pixel_offset = Point(int(round(self._translation.x, 0)), int(round(self._translation.y, 0)))

        return self._pixel_offset

    def real_offset(self):
        """ The transform in real units (um) with no rounding. """
        if self._real_offset is None:
            x, y = self._translation.x, self._translation.y
            pixel_size = self._resolution
            self._real_offset = Point(x * pixel_size, y * pixel_size)

        return self._real_offset

    def pixel_center(self):
        """ The position of the center of image B (in image A coordinates) - in pixels. """
        if self._pixel_center is None:
            width, height = self.image2.size()
            x, y = self._translation.x + width / 2, self._translation.y + height / 2
            x, y = int(round(x)), int(round(y))
            self._pixel_center = Point(x, y)

        return self._pixel_center

    def real_center(self):
        """ The position of the center of image B (in image A coordinates) - in pixels. """
        if self._real_center is None:
            width, height = self.image2.size()
            x, y = self._translation.x + width / 2, self._translation.y + height / 2
            self._real_center = Point(x, y)

        return self._real_center

    def overlay(self, rect_color=Color.black()):
        """ An image which consists of Image A with the overlapping regions of Image B in a 50:50 blend. """
        if self._overlay is None:
            # DEV NOTE: Overlayer uses the offset of image B from Image A - the translation must be inverted
            self._overlay = Overlayer.create_overlay_image(self.image1, self.image2, -self._translation, rect_color)
        return self._overlay

    def alignment_status_code(self):
        if self.is_alignment_bad():
            return ALIGNED_IMAGE_STATUS_FAIL
        return ALIGNED_IMAGE_STATUS_OK

    def overlap_metric(self):
        """ Metric which gives an indication of the quality of the alignment (lower is better). """
        if self._metric is None:
            metric_calc = OverlapMetric(self.image1, self.image2, self._limit_high)
            # DEV NOTE: Overlayer uses the offset of image B from Image A - the translation must be inverted
            self._metric = metric_calc.calculate_overlap_metric(-self._translation)
        return self._metric

    def overlap_images(self):
        """ Two images which are the sub-regions of Images A and B which overlap. """
        if self._overlap_images is None:
            region_a, region_b = Overlayer.get_overlap_regions(self.image1, self.image2, self.pixel_offset())
            self._overlap_images = (region_a, region_b)

        return self._overlap_images
