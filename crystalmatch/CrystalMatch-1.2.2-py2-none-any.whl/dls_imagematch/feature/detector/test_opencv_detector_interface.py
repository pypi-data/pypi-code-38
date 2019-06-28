import numpy as np

import cv2
import unittest

from mock import Mock, patch, MagicMock

from CrystalMatch.dls_imagematch.feature.detector.opencv_detector_interface import OpencvDetectorInterface

class TestOpencvDetectorInterface(unittest.TestCase):

    @patch('cv2.FeatureDetector_create', create=True)
    def test_FeatureDetector_create_is_called_for_opencv2(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "2"
        detector_name = 'ORB'
        adaptation = ''
        name = adaptation+detector_name
        interface = OpencvDetectorInterface()
        interface.feature_detector_create(detector_name, adaptation)
        cv2_mock.assert_called_once_with(name)

    @patch('cv2.FeatureDetector_create', create=True)
    def test_FeatureDetector_create_is_not_called_for_opencv3(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        detector_name = 'ORB'
        adaptation = 10
        interface = OpencvDetectorInterface()
        interface.feature_detector_create(detector_name, adaptation)
        cv2_mock.assert_not_called()

    @patch('cv2.ORB', create=True)
    def test_ORB_is_not_called_for_ORB_detector_in_opencv3(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = 3
        detector_name = 'ORB'
        adaptation = Mock()
        interface = OpencvDetectorInterface()
        interface.feature_detector_create(detector_name, adaptation)
        cv2_mock.assert_called_once_with(adaptation)

    @patch('cv2.FastFeatureDetector_create', create=True)
    def test_FastFeatureDetector_create_called_for_FAST_in_opencv3(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        detector_name = 'FAST'
        adaptation = Mock()
        interface = OpencvDetectorInterface()
        interface.feature_detector_create(detector_name, adaptation)
        cv2_mock.assert_called_once_with()

    @patch('cv2.xfeatures2d', create=True)
    def test_StarDetector_create_called_for_STAR_in_opencv3(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        detector_name = 'STAR'
        adaptation = Mock()
        interface = OpencvDetectorInterface()
        interface.feature_detector_create(detector_name, adaptation)
        cv2_mock.StarDetector_create.assert_called_once_with()

    @patch('cv2.xfeatures2d', create=True)
    def test_HarrisLaplaceFeatureDetector_create_called_for_HARRIS_in_opencv3(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        detector_name = 'HARRIS'
        adaptation = Mock()
        interface = OpencvDetectorInterface()
        interface.feature_detector_create(detector_name, adaptation)
        cv2_mock.HarrisLaplaceFeatureDetector_create.assert_called_once_with()

    @patch('cv2.MSER_create', create=True)
    def test_MSER_create_called_for_MSER_in_opencv3(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        detector_name = 'MSER'
        adaptation = Mock()
        interface = OpencvDetectorInterface()
        interface.feature_detector_create(detector_name, adaptation)
        cv2_mock.assert_called_once_with()

    @patch('cv2.GFTTDetector_create', create=True)
    def test_GFTTDetector_create_called_for_GFTT_in_opencv3(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        detector_name = 'GFTT'
        adaptation = Mock()
        interface = OpencvDetectorInterface()
        interface.feature_detector_create(detector_name, adaptation)
        cv2_mock.assert_called_once_with()

    @patch('cv2.SimpleBlobDetector_create', create=True)
    def test_SimpleBlobDetector_create_called_for_SimpleBlob_in_opencv3(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        detector_name = 'SimpleBlob'
        adaptation = Mock()
        interface = OpencvDetectorInterface()
        interface.feature_detector_create(detector_name, adaptation)
        cv2_mock.assert_called_once_with()

    @patch('cv2.BRISK', create=True)
    def test_BRISK_called_for_other_in_opencv3(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        detector_name = 'BRISK'
        adaptation = Mock()
        interface = OpencvDetectorInterface()
        interface.feature_detector_create(detector_name, adaptation)
        cv2_mock.assert_called_once_with(adaptation)

    @patch('cv2.DescriptorExtractor_create', create=True)
    def test_DescriptorExtractor_create_called_for_opencv2(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "2"
        extractor = Mock()
        interface = OpencvDetectorInterface()
        interface.create_extractor(extractor, 'ORB')
        cv2_mock.assert_called_once_with(extractor)

    #only one extractor left in opecv3
    def test_for_opencv3_create_extractor_returns_none_if_detector_not_on_LIST_WITHOUT_EXTRACTORS(self):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        interface = OpencvDetectorInterface()
        extractor = interface.create_extractor(Mock(), 'ORB')
        self.assertIsNone(extractor)

    @patch('cv2.xfeatures2d', create=True)
    def test_BriefDescriptorExtractor_create_called_for_opencv3_if_detector_on_LIST_WITHOUT_EXTRACTORS(self,                                                                                                    cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        extractor = Mock()
        interface = OpencvDetectorInterface()
        interface.create_extractor(extractor, 'FAST')
        cv2_mock.BriefDescriptorExtractor_create.assert_called_once_with()
        self.assertIsNotNone(cv2_mock.BriefDescriptorExtractor_create)

    def test_compute_always_calls_compute_on_extractor_for_opecv2(self):
        OpencvDetectorInterface.OPENCV_MAJOR = "2"
        image = Mock()
        keypoints = Mock()
        extractor = Mock()
        extractor.compute = Mock(return_value = ([],[]))
        interface = OpencvDetectorInterface()
        interface.compute(image, keypoints, extractor, Mock())
        extractor.compute.assert_called_once_with(image, keypoints)

    def test_opecv3_when_extractor_is_none_than_compute_called_on_detector(self):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        image = Mock()
        keypoints = Mock()
        extractor = None
        detector = Mock()
        #extractor.compute = Mock(return_value=([], []))
        detector.compute = Mock(return_value=([], []))
        interface = OpencvDetectorInterface()
        interface.compute(image, keypoints, extractor, detector)
        detector.compute.assert_called_once_with(image, keypoints)
        #extractor.compute.assert_not_called_once_with(image, keypoints)

    def test_opecv3_when_extracor_is_not_none_than_compute_called_on_extractor(self):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        image = Mock()
        keypoints = Mock()
        extractor = Mock()
        detector = Mock()
        extractor.compute = Mock(return_value=([], []))
        #detector.compute = Mock(return_value=([], []))
        interface = OpencvDetectorInterface()
        interface.compute(image, keypoints, extractor, detector)
        #detector.compute.assert_not_called_once_with(image, keypoints)
        extractor.compute.assert_called_once_with(image, keypoints)

    @patch('cv2.BRISK', create=True) # testing my own mock? - noooo
    def test_brisk_constructor_returns_BRISK_for_opencv2(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "2"
        interface = OpencvDetectorInterface()
        constructor = interface.brisk_constructor()
        self.assertEqual(constructor, cv2_mock)

    @patch('cv2.BRISK_create', create=True)
    def test_brisk_constructor_returns_BRISK_create_for_opencv3(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        interface = OpencvDetectorInterface()
        constructor = interface.brisk_constructor()
        self.assertEqual(constructor, cv2_mock)

    @patch('cv2.ORB', create=True)
    def test_brisk_constructor_returns_ORB_for_opencv2(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "2"
        interface = OpencvDetectorInterface()
        constructor = interface.orb_constructor()
        self.assertEqual(constructor, cv2_mock)

    @patch('cv2.ORB_create', create=True)
    def test_brisk_constructor_returns_ORB_create_for_opencv3(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "3"
        interface = OpencvDetectorInterface()
        constructor = interface.orb_constructor()
        self.assertEqual(constructor, cv2_mock)

    @patch('cv2.estimateRigidTransform', create=True)
    def test_estimate_rigid_transform_triggers_estimateRigidTransform_for_opencv2(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "2"
        interface = OpencvDetectorInterface()
        img1 = Mock()
        img2 = Mock()
        interface.estimate_rigid_transform(img1, img2, True)
        cv2_mock.assert_called_once_with(img1, img2, fullAffine=True)

    @patch('cv2.estimateAffine2D', create=True)
    def test_estimate_rigid_transform_triggers_estimateAffine2D_for_opencv4_when_use_full_true(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "4"
        interface = OpencvDetectorInterface()
        img1 = Mock()
        img2 = Mock()
        interface.estimate_rigid_transform(img1, img2, True)
        cv2_mock.assert_called_once_with(img1, img2)

    @patch('cv2.estimateAffinePartial2D', create=True)
    def test_estimate_rigid_transform_triggers_estimateAffinePartial2D_for_opencv4_when_use_full_false(self, cv2_mock):
        OpencvDetectorInterface.OPENCV_MAJOR = "4"
        interface = OpencvDetectorInterface()
        img1 = Mock()
        img2 = Mock()
        interface.estimate_rigid_transform(img1, img2, False)
        cv2_mock.assert_called_once_with(img1, img2)


    def test_affine_to_np_uses_the_firts_two_rows_of_affine_for_opencv2(self):
         OpencvDetectorInterface.OPENCV_MAJOR = "2"
         interface = OpencvDetectorInterface()
         affine = [np.array([1,2,3]), np.array([4,5,6])]    #this is the affine array format used inopencv2
         new = interface.affine_to_np_array(affine)
         self.assertIn(affine[0], new[0])
         self.assertIn(affine[1], new[1])

    def test_affine_to_np_uses_the_first_array_of_affine_and_gets_the_first_two_rows_of_affine_opencv4(self):
        OpencvDetectorInterface.OPENCV_MAJOR = "4"
        interface = OpencvDetectorInterface()
        affine = (np.array([(1,2,3),(4,5,6)]), np.array([[7],[8],[9],[10],[11],[12]]))
        new = interface.affine_to_np_array(affine)
        self.assertIn(affine[0][0,:], new[0])
        self.assertIn(affine[0][1,:], new[1])