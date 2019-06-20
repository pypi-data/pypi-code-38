#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import numpy
import os
import bob.core

logger = bob.core.log.setup("bob.ip.mtcnn")
bob.core.log.set_verbosity_level(logger, 3)
import os
os.environ['GLOG_minloglevel'] = '2'
import caffe
import bob.ip.base
import bob.io.image

from bob.ip.facedetect import BoundingBox
from .legacy import detect_face
from .utils import rectangle2bounding_box2


class FaceDetector(object):
    """
    Detects face and 5 landmarks using the MTCNN
    (https://github.com/kpzhang93/MTCNN_face_detection_alignment) from the
    paper.

    Zhang, Kaipeng, et al. "Joint face detection and alignment using multitask
    cascaded convolutional networks." IEEE Signal Processing Letters 23.10
    (2016): 1499-1503.

    """

    def __init__(self):
        """
        Load the caffe models
        """

        caffe_base_path = FaceDetector.get_mtcnn_model_path()

        # Default value from the example
        self.minsize = 20
        self.threshold = [0.6, 0.7, 0.7]
        self.factor = 0.709
        self.fastresize = False

        # Loading the models
        caffe.set_mode_cpu()
        self.p_net = caffe.Net(
            os.path.join(caffe_base_path, "det1.prototxt"),
            os.path.join(caffe_base_path, "det1.caffemodel"), caffe.TEST)
        self.r_net = caffe.Net(
            os.path.join(caffe_base_path, "det2.prototxt"),
            os.path.join(caffe_base_path, "det2.caffemodel"), caffe.TEST)
        self.o_net = caffe.Net(
            os.path.join(caffe_base_path, "det3.prototxt"),
            os.path.join(caffe_base_path, "det3.caffemodel"), caffe.TEST)

    def _convert_list_to_landmarks(self, points):
        """
        Convert the list to 10 landmarks to a dictionary with the points
        """

        landmarks = []
        possible_landmarks = ['reye', 'leye',
                              'nose', 'mouthleft', 'mouthright']
        for i in range(points.shape[0]):
            landmark = dict()
            for offset, p in enumerate(possible_landmarks):
                landmark[p] = (int(points[i][offset + 5]),
                               int(points[i][offset]))
            landmarks.append(landmark)

        return landmarks

    def detect_all_faces(self, image, return_bob_bb=True):
        """
        Detect all the faces with its respective landmarks, if any, in a
        COLORED image

        Parameters
        ----------
        image : numpy.array
            The color image [c, w, h]
        return_bob_bb : bool, optional
            If true, will return faces wrapped using
            :any:`bob.ip.facedetect.BoundingBox`.

        Returns
        -------
        object
            Returns two lists; the first on contains the bounding boxes with
            the detected faces and the second one contains list with the faces
            landmarks. The CNN returns 5 facial landmarks (leye, reye, nose,
            mouthleft, mouthright). If there's no face, `None` will be returned

        Raises
        ------
        ValueError
            When image.ndim is not 3.

        """
        assert image is not None

        if len(image.shape) != 3:
            raise ValueError("Only color images is supported")

        bb, landmarks = detect_face(bob.io.image.to_matplotlib(
            image), self.minsize, self.p_net, self.r_net, self.o_net, self.threshold, self.fastresize, self.factor)

        # If there's no face, return none
        if len(bb) == 0:
            return None, None

        if return_bob_bb:
            bb = rectangle2bounding_box2(bb)

        return bb, self._convert_list_to_landmarks(landmarks)

    def detect_single_face(self, image):
        """
        Returns the biggest face in a COLORED image, if any.

        Parameters
        ----------
        image : numpy.array
            numpy array with color image [c, w, h]

        Returns
        -------
        The face bounding box and its respective 5 landmarks (leye, reye, nose,
        mouthleft, mouthright). If there's no face, `None` will be returned

        """

        faces, landmarks = self.detect_all_faces(image)
        # Return None if
        if faces is None:
            return None, None

        index = numpy.argmax([(f.bottomright[0] - f.topleft[0])
                              * (f.bottomright[1] - f.topleft[1]) for f in faces])

        return faces[index], landmarks[index]

    def detect_crop_align(self, image, final_image_size=(160, 160)):
        """
        Detects the biggest face and crop it based in the eyes location
        using py:class:`bob.ip.base.FaceEyesNorm`.

        Final eyes location was inspired here: https://gitlab.idiap.ch/bob/bob.bio.caffe_face/blob/master/bob/bio/caffe_face/config/preprocessor/vgg_preprocessor.py

        **Parameters**
           image: numpy array with color image [c, w, h]
           final_image_size: Image dimensions [w, h]

        **Returns**
           The cropped image. If there's no face, `None` will be returned

        """

        face, landmark = self.detect_single_face(image)

        if face is None:
            return None

        CROPPED_IMAGE_WIDTH = final_image_size[0]
        CROPPED_IMAGE_HEIGHT = final_image_size[1]

        # final image position w.r.t the image size
        RIGHT_EYE_POS = (CROPPED_IMAGE_HEIGHT / 3.44,
                         CROPPED_IMAGE_WIDTH / 3.02)
        LEFT_EYE_POS = (CROPPED_IMAGE_HEIGHT / 3.44,
                        CROPPED_IMAGE_WIDTH / 1.49)

        extractor = bob.ip.base.FaceEyesNorm(
            (CROPPED_IMAGE_HEIGHT, CROPPED_IMAGE_WIDTH), RIGHT_EYE_POS, LEFT_EYE_POS)
        return extractor(image, landmark['reye'], landmark['leye'])

    def detect_crop(self, image, final_image_size=(182, 182), margin=44):
        """
        Detects the biggest face and crop it

        **Parameters**
           image: numpy array with color image [c, w, h]
           final_image_size: Image dimensions [w, h]

        **Returns**
           The cropped image. If there's no face, `None` will be returned

        """

        face, landmark = self.detect_single_face(image)

        if face is None:
            return None

        top = numpy.uint(numpy.maximum(face.top - margin / 2, 0))
        left = numpy.uint(numpy.maximum(face.left - margin / 2, 0))

        bottom = numpy.uint(numpy.minimum(
            face.bottom + margin / 2, image.shape[1]))
        right = numpy.uint(numpy.minimum(
            face.right + margin / 2, image.shape[2]))

        cropped = image[:, top:bottom, left:right]

        dst = numpy.zeros(shape=(3, final_image_size[0], final_image_size[1]))
        bob.ip.base.scale(cropped, dst)
        return dst

    @staticmethod
    def get_mtcnn_model_path():
        import pkg_resources
        return pkg_resources.resource_filename(__name__, 'data')
