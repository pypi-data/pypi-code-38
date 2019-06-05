import logging

from CrystalMatch.dls_imagematch import logconfig
from CrystalMatch.dls_imagematch.crystal.align.sized_image import SizedImage
from CrystalMatch.dls_imagematch.feature import FeatureMatcher
from CrystalMatch.dls_util.shape import Point
from CrystalMatch.dls_imagematch.crystal.align.aligned_images import AlignedImages
from CrystalMatch.dls_imagematch.crystal.align.exception import ImageAlignmentError


class ImageAligner:

    def __init__(self, image1, image2, align_config, detector_config=None):
        """
        Takes two images and uses feature detection to provide a best fit alignment. The scale of the images will be
        normalized by resizing image1 to the same resolution as image2.  Note that this does not mean the images
        will be the same size!
        :param image1: This image will be rescaled to the same resolution as image2.
        :param image2: The image used to align the sample.
        :param align_config: Configuration object for this process.
        :param detector_config: Configuration object for the feature detector.
        """
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        assert(align_config is not None)
        # Create images with associated real sizes
        px_size_1 = align_config.pixel_size_1.value()
        px_size_2 = align_config.pixel_size_2.value()
        self._resolution = px_size_2  # The resolution of the second image will be the working resolution
        self._scale_factor = px_size_1 / px_size_2


        log.info("Image 1 original size: %d x %d (%f um/pixel)", image1.width(), image1.height(), px_size_1)
        log.info("Image 2 original size: %d x %d (%f um/pixel)", image2.width(), image2.height(), px_size_2)
        extra = {'scale_factor': str(self._scale_factor)}
        log = logging.LoggerAdapter(log, extra)
        log.info("Scale Factor calculated as " + str(self._scale_factor))
        log.debug(extra)

        self._image1 = SizedImage.from_image(image1, px_size_1)
        self._image2 = SizedImage.from_image(image2, px_size_2)

        self._align_config = align_config
        self._detector_config = detector_config

        self._rescale_image_1()

    # -------- CONFIGURATION -------------------
    def set_align_config(self, config):  # pragma: no cover
        self._align_config = config

    def set_detector_config(self, config):  # pragma: no cover
        self._detector_config = config

    def _rescale_image_1(self):
        # Resize image A so it has the same size per pixel as image B
        if self._scale_factor != 1:
            self._image1 = self._image1.rescale(self._scale_factor)
            log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
            log.addFilter(logconfig.ThreadContextFilter())
            log.info("Rescaling image 1 by scale factor " + str(self._scale_factor) +
                         ", new size: %d x %d", self._image1.width(), self._image1.height())

    # -------- FUNCTIONALITY -------------------
    def align(self):
        """ Perform image alignment, returning an AlignedImages object. """
        self._check_config()

        if not self._align_config.use_alignment.value():
            return self._default_alignment()

        detector = self._get_detector()
        match_result = self._perform_match(detector)
        aligned_images = self._generate_alignment(match_result, detector)

        return aligned_images

    def scale_points(self, points_array):
        """
        Apply the scale transform from image 1 to an array of Point objects.
        :param points_array: An array of Point objects
        :return: A scaled array of Point object.
        """
        output_array = []
        for point in points_array:
            output_array.append(point * self._scale_factor)
        return output_array

    def _default_alignment(self):
        """ Default alignment result with 0 offset. """
        translation = Point()
        description = "DISABLED!"
        return AlignedImages(self._image1, self._image2, self._resolution, self._scale_factor,
                             translation, self._align_config, description)

    def _check_config(self):
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())
        """ Raises an exception if configuration has not been properly set. """
        if self._align_config is None:
            log.error(ImageAlignmentError("Must set Alignment config before performing alignment"))
            raise ImageAlignmentError("Must set Alignment config before performing alignment")
        elif self._detector_config is None:
            log.error("Must set Detector config before performing alignment")
            raise ImageAlignmentError("Must set Detector config before performing alignment")

    def _get_detector(self):
        """ Get the selected detector and raise and exception if it is disabled. """
        detector = self._align_config.align_detector.value()
        enabled = self._detector_config.is_detector_enabled(detector)
        if not enabled:
            log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
            log.addFilter(logconfig.ThreadContextFilter())
            log.error("Cannot perform image alignment as detector '{}' is disabled.".format(detector))
            raise ImageAlignmentError("Cannot perform image alignment as detector '{}' is disabled.".format(detector))

        return detector

    def _perform_match(self, detector):
        """ Perform feature matching between the two images. """
        # Note images are passed in backwards - FeatureMatcher was written to map points from image 2 to image 1
        matcher = FeatureMatcher(self._image2.to_mono(), self._image1.to_mono(), self._detector_config)
        matcher.set_detector(detector)
        match_result = matcher.match_translation_only()
        return match_result

    def _generate_alignment(self, match_result, detector):
        """ Generate a translation that maps image 2 to image 1 based on the feature match results. """
        if not match_result.has_transform():
            raise ImageAlignmentError("Image Alignment failed - no matches found.")

        translation = match_result.transform().translation()
        description = "Feature matching - " + detector
        aligned_images = AlignedImages(self._image1, self._image2, self._resolution, self._scale_factor,
                                       translation, self._align_config, description)
        aligned_images.feature_match_result = match_result
        return aligned_images
