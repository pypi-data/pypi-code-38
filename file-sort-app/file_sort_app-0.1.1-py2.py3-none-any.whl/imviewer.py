import warnings
warnings.simplefilter('ignore', category=UserWarning)

from skimage.viewer import ImageViewer
from skimage.io import imread
from sys import argv



script, image = argv

print(f"Image is {image}")
# path to IMG
img = imread(image)
view = ImageViewer(img)
view.show()
