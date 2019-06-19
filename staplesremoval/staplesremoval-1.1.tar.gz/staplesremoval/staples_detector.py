import skimage
from skimage.color import rgb2hsv
from skimage import morphology
import numpy
import scipy

def generate_mask(image):
    HSV_image = convert_image_to_HSV(image)
    V = get_V_channel(HSV_image)

    GY = calculate_sobel_vertical_gradient(V)
    BY = binarize_image(GY,60/255)

    se = numpy.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    C = morphological_closing(BY,se)

    holes = fill_small_holes(C)
    filtered = remove_small_objects(holes,50)

    dilated_mask = dilate_mask(dilate_mask(filtered, se),se)
    return(dilated_mask)

def convert_image_to_HSV(image):
    return(rgb2hsv(image))

def get_V_channel(hsvImage):
    return(hsvImage[:, :, 2])

def calculate_sobel_vertical_gradient(image):
    ky = numpy.array([[1, 2, 1],
                      [0, 0, 0],
                      [-1, -2, -1]])
    return(scipy.ndimage.convolve(image,ky))

def binarize_image(image, threshold):
    binary = image.copy()
    binary[binary > threshold] = 1
    binary[binary <= threshold] = 0

    return binary

def morphological_closing(image, structuring_element):
    return(skimage.morphology.binary_closing(image,
                                             structuring_element))

def fill_small_holes(image):
    return(scipy.ndimage.morphology.binary_fill_holes(image))

def remove_small_objects(image, area):
    return(skimage.morphology.remove_small_objects(image,area))

def dilate_mask(mask,structuring_element):
    return (skimage.morphology.binary_dilation(mask,
                                               structuring_element))