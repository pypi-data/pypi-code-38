import bob.io.base
import bob.io.image
import bob.io.base.test_utils
import bob.ip.dlib
import numpy
from matplotlib import pyplot
import bob.ip.draw
from bob.ip.facedetect import BoundingBox

# Align
dlib_image_g = bob.io.base.load(bob.io.base.test_utils.datafile('image_r10.hdf5', 'bob.ip.dlib'))
align = bob.ip.dlib.AlignDLib()
bb = BoundingBox((31, 22), (77, 60))
norm_image_g = align(dlib_image_g, bb=bb, image_size=(100, 100))


# plotin landmarks
detector = bob.ip.dlib.DlibLandmarkExtraction()
points_before = detector(dlib_image_g, bb=bb)
points_after = detector(norm_image_g, bb=BoundingBox((0, 0), (100, 100)))

#making it color
dlib_image = numpy.zeros(shape=(3, dlib_image_g.shape[0], dlib_image_g.shape[1]))
dlib_image[0, :, :] = dlib_image_g; dlib_image[2, :, :] = dlib_image_g; dlib_image[2, :, :] = dlib_image_g;
norm_image = numpy.zeros(shape=(3, norm_image_g.shape[0], norm_image_g.shape[1]))
norm_image[0, :, :] = norm_image_g; norm_image[2, :, :] = norm_image_g; norm_image[2, :, :] = norm_image_g;

for p in points_before:
    bob.ip.draw.plus(dlib_image, p, radius=3, color=(255, 0, 0))

for p in points_after:
    bob.ip.draw.plus(norm_image, p, radius=3, color=(255, 0, 0))

ax = pyplot.subplot(1, 2, 1)
ax.set_title("Before normalization")
pyplot.imshow(bob.io.image.to_matplotlib(dlib_image).astype("uint8"))
pyplot.axis('off')

ax = pyplot.subplot(1, 2, 2)
ax.set_title("Normalized")
pyplot.imshow(bob.io.image.to_matplotlib(norm_image).astype("uint8"))
pyplot.axis('off')


