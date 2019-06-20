from bob.ip.flandmark import Flandmark
from bob.ip.draw import box, cross
from bob.ip.color import rgb_to_gray
from bob.ip.facedetect import detect_single_face
import bob.io.image


def get_data(f):
  from os.path import join
  from pkg_resources import resource_filename
  from bob.io.base import load
  return load(resource_filename('bob.ip.flandmark', join('data', f)))


lena = get_data('lena.jpg')
lena_gray = rgb_to_gray(lena)
bounding_box, quality = detect_single_face(lena)
bounding_box = bounding_box.scale(1.2, True)
y, x = bounding_box.topleft
height, width = bounding_box.size
width = height
# x, y, width, height = [214, 202, 183, 183] # Manual annotations
localizer = Flandmark()
keypoints = localizer.locate(lena_gray, y, x, height, width)

# draw the keypoints and bounding box
box(lena, (y, x), (height, width), (255, 0, 0))  # red bounding box
for k in keypoints:
  cross(lena, k.astype(int), 5, (255, 255, 0))  # yellow key points

bob.io.image.imshow(lena)
