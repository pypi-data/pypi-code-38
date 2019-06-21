import bob.io.base
import bob.io.image
import bob.ip.caffe_extractor
import bob.io.base.test_utils
import numpy
from matplotlib import pyplot


def norm_image(image):
    return (255 * ((image - numpy.min(image)) / (numpy.max(image) - numpy.min(image)))).astype("uint8")


image = bob.io.base.load(bob.io.base.test_utils.datafile(
    '8821.hdf5', 'bob.ip.caffe_extractor'))
caffe_extractor = bob.ip.caffe_extractor.VGGFace("conv2_1")
convs = caffe_extractor(image)  # Getting the first convolved image

pyplot.subplot(2, 3, 1)
pyplot.imshow(norm_image(convs[0]), cmap='Greys_r')

pyplot.subplot(2, 3, 2)
pyplot.imshow(norm_image(convs[3]), cmap='Greys_r')

pyplot.subplot(2, 3, 3)
pyplot.imshow(norm_image(convs[14]), cmap='Greys_r')

pyplot.subplot(2, 3, 4)
pyplot.imshow(norm_image(convs[45]), cmap='Greys_r')

pyplot.subplot(2, 3, 5)
pyplot.imshow(norm_image(convs[105]), cmap='Greys_r')

pyplot.subplot(2, 3, 6)
pyplot.imshow(norm_image(convs[118]), cmap='Greys_r')
