import numpy as np

import cv2

from CrystalMatch.dls_imagematch.feature.detector import DetectorType



class OpencvDetectorInterface:
    OPENCV_MAJOR = cv2.__version__[0]

    def __init__(self):
        pass

    def feature_detector_create(self, detector_name, adaptation):

        if int(self.OPENCV_MAJOR) < 3:
            name = adaptation + detector_name
            detector = cv2.FeatureDetector_create(name)
        else:
            if detector_name == DetectorType.ORB:
                detector = cv2.ORB(adaptation)
            elif detector_name == DetectorType.FAST:
                # noinspection PyUnresolvedReferences
                detector = cv2.FastFeatureDetector_create()
            elif detector_name == DetectorType.STAR:
                # noinspection PyUnresolvedReferences
                detector = cv2.xfeatures2d.StarDetector_create()
            elif detector_name == DetectorType.MSER:
                # noinspection PyUnresolvedReferences
                detector = cv2.MSER_create()
            elif detector_name == DetectorType.GFTT:
                # noinspection PyUnresolvedReferences
                detector = cv2.GFTTDetector_create()
            elif detector_name == DetectorType.HARRIS:
                # noinspection PyUnresolvedReferences
                detector = cv2.xfeatures2d.HarrisLaplaceFeatureDetector_create()
            elif detector_name == DetectorType.BLOB:
                # noinspection PyUnresolvedReferences
                detector = cv2.SimpleBlobDetector_create()
            else:  # detector.detector() == DetectorType.BRISK:
                detector = cv2.BRISK(adaptation)

        return detector

    def get_hamming_norm(self):
        return cv2.NORM_HAMMING

    def create_extractor(self, extractor_name, detector_name):
        if int(self.OPENCV_MAJOR) < 3:
            extractor = cv2.DescriptorExtractor_create(extractor_name)
        else:
            if detector_name in DetectorType.LIST_WITHOUT_EXTRACTORS:
                # noinspection PyUnresolvedReferences
                extractor = cv2.xfeatures2d.BriefDescriptorExtractor_create()
            else:
                extractor = None

        return extractor

    def compute(self, image, keypoints, extractor, detector):
        if int(self.OPENCV_MAJOR) < 3:
            keypoints, descriptors = extractor.compute(image, keypoints)
        else:
            if extractor is None:
                keypoints, descriptors = detector.compute(image, keypoints)
            else:
                keypoints, descriptors = extractor.compute(image, keypoints)


        return keypoints, descriptors

    def brisk_constructor(self):
        if int(self.OPENCV_MAJOR) < 3:
            constructor = cv2.BRISK
        else:
            # noinspection PyUnresolvedReferences
            constructor = cv2.BRISK_create

        return constructor

    def orb_constructor(self):
        if int(self.OPENCV_MAJOR) < 3:
            constructor = cv2.ORB
        else:
            # noinspection PyUnresolvedReferences
            constructor = cv2.ORB_create

        return constructor

    def estimate_rigid_transform(self, image1_pts, image2_pts, use_full):
        if int(self.OPENCV_MAJOR) < 4: # new in opencv4
            affine = cv2.estimateRigidTransform(image1_pts, image2_pts, fullAffine=use_full)
        else:
            if use_full:
                # noinspection PyUnresolvedReferences
                # new implementation returns also a vector which indicated which points are inliers
                affine = cv2.estimateAffine2D(image1_pts, image2_pts)
            else:
                # noinspection PyUnresolvedReferences
                affine = cv2.estimateAffinePartial2D(image1_pts, image2_pts)

        return affine

    # reshapes the affine result into a 3x3 array
    def affine_to_np_array(self, affine):
        if int(self.OPENCV_MAJOR) < 4: # new in opencv4
            affine_arr = np.array([affine[0], affine[1], [0, 0, 1]], np.float32)
        else:
            affine_zero = affine[0]
            affine_arr = np.array([affine_zero[0, :], affine_zero[1, :], [0, 0, 1]], np.float32)

        return affine_arr

