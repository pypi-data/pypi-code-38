import bob.io.base
import bob.io.image
import bob.io.base.test_utils
import bob.ip.dlib
from matplotlib import pyplot
from matplotlib.patches import Rectangle
import bob.ip.draw
import bob.ip.facedetect

# detect multiple bob
bob_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
bob_bounding_box, _ = bob.ip.facedetect.detect_single_face(bob_color_image)

# detect multiple dlib
dlib_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
dlib_bounding_box, _ = bob.ip.dlib.FaceDetector().detect_single_face(dlib_color_image)

# create figure
# bob.ip.draw.box(bob_color_image, bob_bounding_box.topleft, bob_bounding_box.size, color=(255, 0, 0))

# bob.ip.draw.box(dlib_color_image, dlib_bounding_box.topleft, dlib_bounding_box.size, color=(255, 0, 0))

ax = pyplot.subplot(1, 2, 1)
ax.set_title("bob.ip.dlib")
pyplot.imshow(bob.io.image.to_matplotlib(dlib_color_image).astype("uint8"))
pyplot.axis('off')
ax.add_patch(Rectangle(dlib_bounding_box.topleft[::-1], dlib_bounding_box.size[1], dlib_bounding_box.size[0], edgecolor='r', facecolor='none'))

ax = pyplot.subplot(1, 2, 2)
ax.set_title("bob.ip.facedetect")
pyplot.imshow(bob.io.image.to_matplotlib(bob_color_image).astype("uint8"))
pyplot.axis('off')
ax.add_patch(Rectangle(bob_bounding_box.topleft[::-1], bob_bounding_box.size[1], bob_bounding_box.size[0], edgecolor='r', facecolor='none'))
