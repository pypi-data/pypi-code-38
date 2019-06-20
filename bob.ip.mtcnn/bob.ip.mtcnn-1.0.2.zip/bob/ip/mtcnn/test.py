import bob.io.base
import bob.io.image
import bob.ip.mtcnn
from bob.ip.facedetect import BoundingBox

import bob.ip.color
import pkg_resources

detector = bob.ip.mtcnn.FaceDetector()

import numpy as np

def test_face_detection():

    ### Testing multiple detections
    color_image = bob.io.base.load(pkg_resources.resource_filename('bob.ip.mtcnn', 'data/multiple-faces.jpg'))
    faces, landmarks = detector.detect_all_faces(color_image)
    assert len(faces) == 18
    assert len(landmarks) == 18

    possible_landmarks = ['reye', 'leye', 'nose', 'mouthleft', 'mouthright']
    for p in possible_landmarks:
        assert p in landmarks[0]

    ### Testing single detections
    color_image = bob.io.base.load(pkg_resources.resource_filename('bob.ip.facedetect', 'data/testimage.jpg'))
    faces, landmarks = detector.detect_single_face(color_image)
    assert isinstance(faces, BoundingBox)

    ### Testing no detections
    color_image = bob.io.base.load(pkg_resources.resource_filename('bob.ip.mtcnn', 'data/jeep.jpg'))
    faces, landmarks = detector.detect_single_face(color_image)
    assert faces is None
    assert landmarks is None

    #=========================================================================
    # assert negative coordinates and even arrays:

    image = np.zeros((3, 100, 100))
    result = detector.detect_single_face(image)
    assert result == (None, None)

    image = np.ones((3, 100, 100))
    result = detector.detect_single_face(image)
    assert result == (None, None)

    # test on the actual image:
    test_file = pkg_resources.resource_filename('bob.ip.mtcnn', 'data/test_image.hdf5')

    f = bob.io.base.HDF5File(test_file) #read only
    image = f.read('image') #reads integer
    del f

    result = detector.detect_single_face(image)
    assert result[0].topleft == (0, 58)
    assert result[0].bottomright == (228, 232)


def test_crop():

    ### Testing multiple detections
    color_image = bob.io.base.load(pkg_resources.resource_filename('bob.ip.facedetect', 'data/testimage.jpg'))
    face = detector.detect_crop_align(color_image, final_image_size=(224, 224))
    assert face.shape == (3, 224, 224)

