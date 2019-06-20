#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date: Fri 17 Jun 2016 10:41:36 CEST

import numpy
import os
import bob.core

logger = bob.core.log.setup("bob.ip.dlib")
bob.core.log.set_verbosity_level(logger, 3)
import dlib
import bob.io.image
from bob.ip.facedetect import BoundingBox


class FaceDetector(object):
    """
    Detects face using the dlib Face Detector (http://dlib.net/face_detector.py.html)
    """

    def __init__(self):
        self.face_detector = dlib.get_frontal_face_detector()

    def detect_all_faces(self, image):
        """
        Find all face bounding boxes in an image.

        Parameters
        ----------

        image:  2D or 3D :py:class:`numpy.ndarray`
          GRAY scaled or RGB image in the format (CxWxH)
        """
        assert image is not None

        if len(image.shape) == 2:
            rows, cols = image.shape
        if len(image.shape) == 3:
            _, rows, cols = image.shape

        try:
            rectangles = self.face_detector(bob.io.image.to_matplotlib(image), 1)
            bbs = []
            for r in rectangles:

                top  = numpy.max( [0, r.top()] )
                left = numpy.max( [0, r.left()])
                height = numpy.min( [rows-top,  r.height()] )
                width  = numpy.min( [cols-left, r.width() ] )

                bbs.append(BoundingBox((top, left),
                                       (height, width),
                                       ))

            # This detector does not have the `quality` of the detection so I will fill it up with 100
            qualities = tuple(100 * numpy.ones(shape=(len(rectangles))))
            bbs = tuple(bbs)

            return (bbs, qualities)

        except Exception as e:
            print("Warning: {}".format(e))
            # In rare cases, exceptions are thrown.
            return []

    def detect_single_face(self, image):
        """
        Detect the biggest detected face in an image

        Parameters
        ----------

        image:  2D or 3D :py:class:`numpy.ndarray`
          GRAY scaled or RGB image in the format (CxWxH)
        """

        faces = self.detect_all_faces(image)
        if len(faces) > 1 and not all([not f for f in faces]):
            index = numpy.argmax([(f.bottomright[0] - f.topleft[0]) * (f.bottomright[1] - f.topleft[1]) for f in faces[0]])
            return (faces[0][index], faces[1][index])
        else:
            return None
