import numpy
import Image

# get image array
def getImageArray(image_object):
    # get list of pixels
    pixel_values = list(image_object.getdata())
    # get image array
    image_arr = numpy.array(pixel_values)
    # reshape the array in the dimensions of image
    image_arr = image_arr.reshape(image_object.size[0], image_object.size[1])
    return image_arr

# get histogram of image
def getHist(image_arr):
    row = image_arr.shape[0]    # get row of the image row
    col = image_arr.shape[1]    # get column of the image row
    hist = [0 for i in range(256)]
    for r in range(row):
        for c in range(col):
            hist[image_arr[r,c]] += 1
    return hist

# get image from array
def getImageFromArray(arr, width, height):
    arr = numpy.array(arr)
    # reshaping array
    arr = arr.reshape(width, height)
    arr = Image.fromarray(numpy.uint8(arr))
    return arr
