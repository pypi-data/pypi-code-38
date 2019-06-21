import bob.io.base
import bob.io.image
from bob.io.base.test_utils import datafile
import bob.ip.tensorflow_extractor
import tensorflow as tf

import pkg_resources
import numpy
import json
import os

numpy.random.seed(10)

slim = tf.contrib.slim
from . import scratch_network


def test_output():

    # Loading MNIST model
    filename = os.path.join(
        pkg_resources.resource_filename(__name__, "data"), "model.ckp"
    )
    inputs = tf.placeholder(tf.float32, shape=(None, 28, 28, 1))

    # Testing the last output
    graph = scratch_network(inputs)
    extractor = bob.ip.tensorflow_extractor.Extractor(filename, inputs, graph)

    data = numpy.random.rand(2, 28, 28, 1).astype("float32")
    output = extractor(data)
    assert extractor(data).shape == (2, 10)
    del extractor

    # Testing flatten
    inputs = tf.placeholder(tf.float32, shape=(None, 28, 28, 1))
    graph = scratch_network(inputs, end_point="flatten1")
    extractor = bob.ip.tensorflow_extractor.Extractor(filename, inputs, graph)

    data = numpy.random.rand(2, 28, 28, 1).astype("float32")
    output = extractor(data)
    assert output.shape == (2, 1690)
    del extractor


def test_facenet():
    from bob.ip.tensorflow_extractor import FaceNet

    extractor = FaceNet()
    data = numpy.random.rand(3, 160, 160).astype("uint8")
    output = extractor(data)
    assert output.size == 128, output.shape


def test_drgan():
    from bob.ip.tensorflow_extractor import DrGanMSUExtractor

    extractor = DrGanMSUExtractor()
    data = numpy.random.rand(3, 96, 96).astype("uint8")
    output = extractor(data)
    assert output.size == 320, output.shape


def test_vgg16():
    pass
    # from bob.ip.tensorflow_extractor import VGGFace
    # extractor = VGGFace()
    # data = numpy.random.rand(3, 224, 224).astype("uint8")
    # output = extractor(data)
    # assert output.size == 4096, output.shape


def test_mtcnn():
    test_image = datafile("mtcnn/test_image.png", __name__)
    ref_numbers = datafile("mtcnn/mtcnn.hdf5", __name__)
    ref_annots = datafile("mtcnn/mtcnn.json", __name__)
    from bob.ip.tensorflow_extractor import MTCNN

    mtcnn = MTCNN()
    img = bob.io.base.load(test_image)
    bbox, prob, landmarks = mtcnn.detect(img)
    with bob.io.base.HDF5File(ref_numbers, "r") as f:
        ref_bbox = f["bbox"]
        ref_scores = f["scores"]
        ref_landmarks = f["landmarks"]

    assert numpy.allclose(bbox, ref_bbox), (bbox, ref_bbox)
    assert numpy.allclose(prob, ref_scores), (prob, ref_scores)
    assert numpy.allclose(landmarks, ref_landmarks), (landmarks, ref_landmarks)

    annots = mtcnn.annotations(img)
    ref_annots = json.load(open(ref_annots))
    assert len(annots) == len(ref_annots), (len(annots), len(ref_annots))
    for a, aref in zip(annots, ref_annots):
        for k, v in a.items():
            vref = aref[k]
            assert numpy.allclose(v, vref)
