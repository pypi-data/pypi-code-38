import bob.io.base
import bob.io.image
import bob.io.base.test_utils
import bob.ip.dlib
from matplotlib import pyplot
from matplotlib.patches import Rectangle
import bob.ip.draw
import bob.ip.facedetect


# detect multiple bob
bob_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('multiple-faces.jpg', 'bob.ip.dlib'))
bob_bounding_box, _ = bob.ip.facedetect.detect_all_faces(bob_color_image)

# detect multiple dlib
dlib_color_image = bob.io.base.load(bob.io.base.test_utils.datafile('multiple-faces.jpg', 'bob.ip.dlib'))
dlib_bounding_box, _ = bob.ip.dlib.FaceDetector().detect_all_faces(dlib_color_image)

# create figure
ax = pyplot.subplot(1, 2, 1)
ax.set_title("bob.ip.dlib")
pyplot.imshow(bob.io.image.to_matplotlib(dlib_color_image).astype("uint8"))
pyplot.axis('off')

for b in dlib_bounding_box:
    ax.add_patch(Rectangle(b.topleft[::-1], b.size[1], b.size[0], edgecolor='r', facecolor='none'))

ax = pyplot.subplot(1, 2, 2)
ax.set_title("bob.ip.facedetect")
pyplot.imshow(bob.io.image.to_matplotlib(bob_color_image).astype("uint8"))
pyplot.axis('off')

for b in bob_bounding_box:
    ax.add_patch(Rectangle(b.topleft[::-1], b.size[1], b.size[0], edgecolor='r', facecolor='none'))
