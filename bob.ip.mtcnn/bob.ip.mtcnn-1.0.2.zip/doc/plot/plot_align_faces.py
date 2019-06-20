import bob.io.base
import bob.io.image
import bob.io.base.test_utils
import bob.ip.mtcnn
import numpy
import os
from matplotlib import pyplot
import bob.ip.draw
from bob.ip.facedetect import BoundingBox

color_image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
face_crop = bob.ip.mtcnn.FaceDetector().detect_crop(color_image, final_image_size=(224, 224))
face_crop_aligned = bob.ip.mtcnn.FaceDetector().detect_crop_align(color_image, final_image_size=(224, 224))

ax = pyplot.subplot(1, 3, 1)
ax.set_title("Before normalization")
pyplot.imshow(bob.io.image.to_matplotlib(color_image))
pyplot.axis('off')

ax = pyplot.subplot(1, 3, 2)
ax.set_title("Normalized")
pyplot.imshow(bob.io.image.to_matplotlib(face_crop).astype("uint8"))
pyplot.axis('off')

ax = pyplot.subplot(1, 3, 3)
ax.set_title("Normalized and aligned")
pyplot.imshow(bob.io.image.to_matplotlib(face_crop_aligned).astype("uint8"))
pyplot.axis('off')

#pyplot.show()


