import numpy as np
from faceorientationprep.utils import rotate
from faceorientationprep.orientationclassifier.orientationclassifier import OrientationType, OrientationClassifier
from faceorientationprep.exceptions import GivenImageNotValidError


class FaceOrientationFixer:
    """
    A class that handles the orientation fixing from a given
    OpenCV image.
    """

    def __init__(self, orientationClassifier = OrientationClassifier()):
        """ constructor """
        self.orientationClassifier = orientationClassifier

    def fixOrientation(self, image):
        """
        Identify the orientation and rotate the image if the orientation
        is not in a normal state.
        :param image: a given image as Mat object
        :return: an image that was rotated to the normal orientation
        """

        if not isinstance(image, np.ndarray):
            raise GivenImageNotValidError("Given image is invalid")

        orientationType = self.orientationClassifier.classifyOrientation(image)

        if orientationType == OrientationType.CLOCKWISE_90_DEG:
            image = rotate(image, -90)

        elif orientationType == OrientationType.CLOCKWISE_180_DEG:
            image = rotate(image, 180)

        elif orientationType == OrientationType.CLOCKWISE_270_DEG:
            image = rotate(image, 90)

        return image
