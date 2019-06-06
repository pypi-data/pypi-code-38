import numpy as np
from scipy.stats import sem
from skimage import color

from .roi import Roi, CenterPosition
from ..helpers.point import IntPoint
from ..helpers.voxel_data import VoxelData


VALID_COLOURS = {
    'SkyBlue': (135, 206, 235),
    'MediumBlue': (0, 0, 205)
}


class SquareRoi(Roi):
    """
    A class for square ROIs in images.

    Attributes
    ----------
    center : CenterPosition
        The coordinates for the center position (x-, y-, and z-index) of the ROI
    height : float
        ROI height in mm
    width : float
        ROI width in mm
    pixel_size : VoxelData
        Pixel size/spacing in mm
    resize_too_big_roi : bool
        Resize a ROI that reaches outside of the image

    Methods
    -------
    get_mean(image)
        Returns the mean of the pixel values in the ROI
    get_stdev(image)
        Returns the standard deviation of the pixel values in the ROI
    get_sum(image, axis=1)
        Returns the sum of the pixel values in the ROI
    get_std_error_of_the_mean(image)
        Returns the standard error of the mean of the pixel values in the ROI
    add_roi_to_image(image, roi_color='SkyBlue')
        Returns the image with the ROI added, coloured in the requested colour
    get_roi_part_of_image(image)
        Returns a numpy ndarray only containing the part of the image that is contained in the ROI
    """

    def __init__(self, center: CenterPosition, height: float, width: float, pixel_size: VoxelData,
                 resize_too_big_roi: bool = False):
        super().__init__(center=center)
        self.Height: float = height
        self.Width: float = width
        self.ResizeTooBigRoi: bool = resize_too_big_roi

        height_pixels = int(round(self.Height / pixel_size.y))
        width_pixels = int(round(self.Width / pixel_size.x))

        if height_pixels < 1 or width_pixels < 1:
            raise ValueError((f'Too small ROI size specified. Both width ({width_pixels}) and height ({height_pixels}) '
                              f'must be at least 1 pixel'))

        height_pixels = int(round((self.Height - pixel_size.y) / pixel_size.y))
        if height_pixels < 0:
            height_pixels = 0
        width_pixels = int(round((self.Width - pixel_size.x) / pixel_size.x))
        if width_pixels < 0:
            width_pixels = 0

        self.UpperLeft: IntPoint = IntPoint(
            x=int(np.floor(self.Center.x - (width_pixels / 2) + 0.5)),
            y=int(np.floor(self.Center.y - (height_pixels / 2) + 0.5))
        )
        # Validate corner does not have negative index
        if self.UpperLeft.x < 0 or self.UpperLeft.y < 0:
            if not resize_too_big_roi:
                raise ValueError(("The upper left corner of the ROI reaches outside of the image "
                                  f"(x = {self.UpperLeft.x}, y = {self.UpperLeft.y})"))
            if self.UpperLeft.x < 0:
                self.UpperLeft.x = 0
            if self.UpperLeft.y < 0:
                self.UpperLeft.y = 0

        self.LowerLeft: IntPoint = IntPoint(
            x=int(np.floor(self.Center.x - (width_pixels / 2) + 0.5)),
            y=int(np.floor(self.Center.y + (height_pixels / 2) + 0.5))
        )

        self.UpperRight: IntPoint = IntPoint(
            x=int(np.floor(self.Center.x + (width_pixels / 2) + 0.5)),
            y=int(np.floor(self.Center.y - (height_pixels / 2) + 0.5)))

        self.LowerRight: IntPoint = IntPoint(
            x=int(np.floor(self.Center.x + (width_pixels / 2) + 0.5)),
            y=int(np.floor(self.Center.y + (height_pixels / 2) + 0.5)))

    def _check_roi_placement(self, image: np.ndarray) -> (int, int):
        """ Checks that the ROI is inside the given image. If not raise Value error or if ResizeTooBigRoi == True,
        calculate new ending indexes.

        :param image: Numpy ndarray containing the image
        :return: The resulting ending indexes as a x, y
        """
        image_shape = image.shape
        if self.UpperLeft.x > image_shape[1] or self.UpperLeft.y > image_shape[0]:
            raise ValueError("Entire image outside of the image")

        x2 = self.LowerRight.x
        if self.LowerRight.x >= image_shape[1]:
            if not self.ResizeTooBigRoi:
                raise ValueError("The ROI reaches outside of the image")
            x2 = image_shape[1]

        y2 = self.LowerRight.y
        if self.LowerRight.y >= image_shape[0]:
            if not self.ResizeTooBigRoi:
                raise ValueError("The ROI reaches outside of the image")
            y2 = image_shape[0]

        return x2, y2

    def get_mean(self, image: np.ndarray) -> np.ndarray:
        """ Calculates the mean of the pixel values contained in the ROI from the input image

        :param image: Numpy ndarray containing the image
        :return: The mean of the pixel values from the part of the input image contained in the ROI
        """
        x2, y2 = self._check_roi_placement(image=image)

        return np.mean(image[self.UpperLeft.y:y2 + 1, self.UpperLeft.x:x2 + 1])

    def get_stdev(self, image: np.ndarray) -> np.ndarray:
        """ Calculates the standard deviation of the pixel values contained in the ROI from the input image

        :param image: Numpy ndarray containing the image
        :return: The standard deviation of the pixel values from the part of the input image contained in the ROI
        """
        x2, y2 = self._check_roi_placement(image=image)

        return np.std(image[self.UpperLeft.y:y2 + 1, self.UpperLeft.x:x2 + 1])

    def get_sum(self, image: np.ndarray, axis: int = 1):
        """ Calculates the sum of the pixel values contained in the ROI from the input image

        :param image: Numpy ndarray containing the image
        :param axis: The axis over which to calculate the sum
        :return: The sum of the square ROI applied to the supplied image over the specified axis
        """
        x2, y2 = self._check_roi_placement(image=image)

        return np.sum(a=image[self.UpperLeft.y:y2 + 1, self.UpperLeft.x:x2 + 1], axis=axis)

    def get_std_error_of_the_mean(self, image: np.ndarray) -> np.ndarray:
        """ Calculates the standard error of the mean of the pixel values contained in the ROI from the input image

        :param image: Numpy ndarray containing the image
        :return: The standard error of the mean of the pixel values from the part of the input image contained in the
        ROI
        """
        x2, y2 = self._check_roi_placement(image=image)

        return sem(image[self.UpperLeft.y:y2 + 1, self.UpperLeft.x:x2 + 1].flatten())

    def add_roi_to_image(self, image: np.ndarray, roi_color: str = 'SkyBlue') -> np.ndarray:
        """ Adds the ROI to the given image using the color specified.

        :param image: Numpy ndarray containing the image
        :param roi_color: The color to use for the ROI
        :return: The input image with the ROI added
        """
        roi_color = VALID_COLOURS.get(roi_color)

        if roi_color is None:
            raise ValueError(f'The colour must be one of {",".join(VALID_COLOURS.keys())}')

        x2, y2 = self._check_roi_placement(image=image)

        image = color.gray2rgb(image)

        image[self.UpperLeft.y:y2 + 1, self.UpperLeft.x:x2 + 1] = roi_color
        return image

    def get_roi_part_of_image(self, image: np.ndarray) -> np.ndarray:
        """ Extracts the part of the image contained in the ROI

        :param image: Numpy ndarray containing the image
        :return: The part of the input image contained in the square ROI as a numpy ndarray
        """
        x2, y2 = self._check_roi_placement(image=image)

        return image[self.UpperLeft.y:y2 + 1, self.UpperLeft.x:x2 + 1]
