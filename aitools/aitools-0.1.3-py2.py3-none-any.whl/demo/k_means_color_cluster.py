from __future__ import print_function

import matplotlib.image as mpimg
from aitools.core import k_means


PATH_TO_IMG_FILE = '../data/hexagons.png'

img = mpimg.imread(PATH_TO_IMG_FILE)

top_row = img[0]
# print_function(top_row)

top_left_pixel = top_row[0]
# print_function(top_left_pixel)

red, green, blue = top_left_pixel

# print_function(red)
# print_function(green)
# print_function(blue)

print_function('reached level 1')

pixels = [pixel for row in img for pixel in row]
print_function(pixels)

print_function('reached level 2')

clusterer = k_means.KMeans(5)

print_function('reached level 3')

clusterer.build(pixels)

print_function('reached level 4')


def recolor(pixel):
    cluster = clusterer.predict(pixel)
    return clusterer.means[cluster]


print_function('reached level 5')

new_img = [[recolor(pixel) for pixel in row]
           for row in img]

print_function('reached level 6')

print_function.imshow(new_img)
# plt.axes('off')
print_function.show()

print_function('reached end')
