import bob.io.base
import bob.io.image
import bob.io.base.test_utils
import bob.ip.dlib
from matplotlib import pyplot
from matplotlib.patches import Rectangle
import bob.ip.draw

# detect multiple dlib
image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
bob_image = bob.io.base.load(bob.io.base.test_utils.datafile('testimage.jpg', 'bob.ip.facedetect'))
bounding_box, _ = bob.ip.dlib.FaceDetector().detect_single_face(image)

# landmarks
detector = bob.ip.dlib.DlibLandmarkExtraction()
points = detector(image)

bob_detector = bob.ip.dlib.DlibLandmarkExtraction(bob_landmark_format=True)
bob_points = bob_detector(bob_image)


ax = pyplot.subplot(1, 2, 1)
ax.set_title("Dlib landmarks")
bob.io.image.imshow(image.astype("uint8"))
pyplot.axis('off')
x = [p[1] for p in points]
y = [p[0] for p in points]
pyplot.plot(x, y, '+', color='r')
ax.add_patch(Rectangle(bounding_box.topleft[::-1], bounding_box.size[1], bounding_box.size[0], edgecolor='r', facecolor='none'))

ax = pyplot.subplot(1, 2, 2)
ax.set_title("Dlib landmarks for Bob")
bob.io.image.imshow(bob_image.astype("uint8"))
pyplot.axis('off')
x = [p[1] for p in bob_points.values()]
y = [p[0] for p in bob_points.values()]
pyplot.plot(x, y, '+', color='r')
