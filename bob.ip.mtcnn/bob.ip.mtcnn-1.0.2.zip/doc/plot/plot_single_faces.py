import bob.io.base
import bob.io.image
import bob.io.base.test_utils
import bob.ip.mtcnn
import pkg_resources
import os
from matplotlib import pyplot
import bob.ip.draw
import bob.ip.facedetect

#print "###################################"
#print os.path.join(pkg_resources.resource_filename(__name__, 'data'), 'multiple-faces.jpg')

# detect multiple bob
bob_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
bob_bounding_box, _ = bob.ip.facedetect.detect_single_face(bob_color_image)

# detect multiple mtcnn
mtcnn_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
mtcnn_bounding_box, landmarks = bob.ip.mtcnn.FaceDetector().detect_single_face(mtcnn_color_image)

# create figure
bob.ip.draw.box(bob_color_image, bob_bounding_box.topleft, bob_bounding_box.size, color=(255, 0, 0))

bob.ip.draw.box(mtcnn_color_image, mtcnn_bounding_box.topleft, mtcnn_bounding_box.size, color=(255, 0, 0))
for p in landmarks:
    bob.ip.draw.plus(mtcnn_color_image, landmarks[p], radius=5, color=(255, 0, 0))

ax = pyplot.subplot(1, 2, 1)
ax.set_title("mtcnn")
pyplot.imshow(bob.io.image.to_matplotlib(mtcnn_color_image))
pyplot.axis('off')

ax = pyplot.subplot(1, 2, 2)
ax.set_title("Bob")
pyplot.imshow(bob.io.image.to_matplotlib(bob_color_image))
pyplot.axis('off')

#pyplot.show()

