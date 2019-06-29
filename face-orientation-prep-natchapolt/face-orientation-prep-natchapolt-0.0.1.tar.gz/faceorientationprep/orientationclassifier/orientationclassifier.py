from enum import Enum
import numpy as np
import dlib
import cv2
from faceorientationprep.utils import rotate, resize
from faceorientationprep.exceptions import GivenImageNotValidError, FaceNotFoundOnImageError


class OrientationType(Enum):
    """
    Types of image orientation
    """
    NORMAL = 0
    CLOCKWISE_90_DEG = 1
    CLOCKWISE_180_DEG = 2
    CLOCKWISE_270_DEG = 3


class OrientationClassifier:
    """
    A class which responsible for classifying the image
    into one of the type in OrientationType Enum
    """

    def __init__(self, faceDetectorFunc = dlib.get_frontal_face_detector()):
        """ constructor """
        self.faceDetectorFunc = faceDetectorFunc

    def classifyOrientation(self, image):
        """
        Execute image classification on a given image to find its current
        orientation type
        :param image: input image read by OpenCV as Mat object
        :return: one of the OrientationType Enum
        """

        if not isinstance(image, np.ndarray):
            raise GivenImageNotValidError("Given image is invalid")

        # pre-process an image to a proper format for face detection
        prepImg = self.__preprocessImage(image)

        for orientationType in OrientationType:

            # detect any faces in the image
            faceRects = self.faceDetectorFunc(prepImg, 1)

            # stop if faces were found
            if faceRects:
                return orientationType

            # rotate image to find faces in other orientation type
            prepImg = rotate(prepImg, -90)

        raise FaceNotFoundOnImageError("No face was found on the given image")

    def __preprocessImage(self, image):
        """
        private method that handles the pre-processing of the
        image to reduce computation time by
            - resize down
            - convert to grayscale
        :param image:
        :return:
        """
        (h, w) = image.shape[:2]

        prepImg = image
        # reduce the size down to 500
        if h == max(h, w) and h > 500:
            prepImg = resize(image, height=500)
        elif  w == max(h, w) and w > 500:
            prepImg = resize(image, width=500)

        return cv2.cvtColor(prepImg, cv2.COLOR_BGR2GRAY)
