import bob.io.base
from bob.io.base.test_utils import datafile
import bob.ip.caffe_extractor
import pkg_resources
import numpy
import os


def test_vgg():

    file_name = os.path.join(
        pkg_resources.resource_filename(__name__, 'data'), '8821.hdf5')
    reference_file_name = os.path.join(
        pkg_resources.resource_filename(__name__, 'data'), 'reference.hdf5')
    reference = bob.io.base.load(reference_file_name)

    f = bob.io.base.load(file_name)

    extractor = bob.ip.caffe_extractor.VGGFace("fc7")
    feature = extractor(f)

    assert numpy.any(numpy.isclose(feature, reference, rtol=1e-08, atol=1e-08))


def test_lightcnn():
    ref_image = bob.io.base.load(
        datafile('lightcnn_reference_image.hdf5',
                 __name__))
    ref_feature = bob.io.base.load(
        datafile('lightcnn_reference_feature.hdf5',
                 __name__))
    extractor = bob.ip.caffe_extractor.LightCNN()
    feature = extractor(ref_image / 255)

    assert numpy.allclose(feature, ref_feature, rtol=1e-04, atol=1e-05), \
        str(feature) + '\n' + str(ref_feature)
