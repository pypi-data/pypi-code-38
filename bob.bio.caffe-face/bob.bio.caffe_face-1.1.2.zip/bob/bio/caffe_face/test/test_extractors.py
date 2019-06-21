import bob.bio.base
import numpy
import bob.bio.caffe_face
from bob.io.base.test_utils import datafile


def test_vgg_feature():
    # read input
    input_data = bob.io.base.load(
        datafile('8821.hdf5', "bob.ip.caffe_extractor"))
    reference = bob.io.base.load(
        datafile('reference.hdf5', "bob.ip.caffe_extractor"))

    caffe_extractor = bob.bio.base.load_resource(
        'vgg_features', 'extractor', preferred_package='bob.bio.caffe_face')
    assert isinstance(
        caffe_extractor, bob.bio.caffe_face.extractor.VGGFeatures)
    assert not caffe_extractor.requires_training

    feature = caffe_extractor(input_data)
    assert numpy.any(numpy.isclose(feature, reference, rtol=1e-08, atol=1e-08))


def test_lightcnn_feature():
    input_data = bob.io.base.load(
        datafile('lightcnn_reference_image.hdf5', "bob.ip.caffe_extractor"))

    reference = bob.io.base.load(
        datafile('lightcnn_reference_feature.hdf5', "bob.ip.caffe_extractor"))

    caffe_extractor = bob.bio.base.load_resource(
        'lightcnn', 'extractor', preferred_package='bob.bio.caffe_face')
    assert not caffe_extractor.requires_training

    feature = caffe_extractor(input_data)
    assert numpy.any(numpy.isclose(feature, reference, rtol=1e-04, atol=1e-05))
