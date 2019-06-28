import skimage
from skimage.color import rgb2hsv
from skimage import morphology
import numpy
import scipy


def generate_mask(image):
    """Computes the mask using the gradient method.

    Args:
      image: An RGB image.
    Returns:
      An RGB image with the mask overlapped and the binary mask.
    """
    hsv_image = convert_image_to_HSV(image)
    V = get_V_channel(hsv_image)

    GY = calculate_sobel_vertical_gradient(V)
    BY = binarize_image(GY, 60 / 255)

    se = numpy.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    C = morphological_closing(BY, se)

    holes = fill_small_holes(C)
    filtered = remove_small_objects(holes, 50)

    dilated_mask = dilate_mask(dilate_mask(dilate_mask(dilate_mask(filtered, se), se), se),se)
    colormask = get_drawn_mask(image, dilated_mask)

    return colormask, dilated_mask


def convert_image_to_HSV(image):
    """Converts the image from RGB to HSV color space.

    Args:
      image: An RGB image.
    Returns:
      An HSV image.
    """
    return (rgb2hsv(image))


def get_V_channel(hsvImage):
    """Gets the V channel.

    Args:
      hsvImage: An HSV image.
    Returns:
      The first channel (H) of the hsvImage.
    """
    return (hsvImage[:, :, 2])


def calculate_sobel_vertical_gradient(image):
    """Computes the Sobel gradient in the vertical direction

    Args:
      image: An RGB image.
    Returns:
      The grayscale image containing the Sobel gradient.
    """
    ky = numpy.array([[1, 2, 1],
                      [0, 0, 0],
                      [-1, -2, -1]])
    return (scipy.ndimage.convolve(image, ky))


def binarize_image(image, threshold):
    """Binarizes an image given threshold.

    Args:
      image: A grayscale image.
      threshold: A real number in the interval [0,1].
    Returns:
      Binary image.
    """
    binary = image.copy()
    binary[binary > threshold] = 1
    binary[binary <= threshold] = 0

    return binary


def morphological_closing(image, structuring_element):
    """Computes the binary morphological closing.

    Args:
      image: A binary image.
      structuring_element: A structuring element.
    Returns:
      A binary image.
    """
    return (skimage.morphology.binary_closing(image,
                                              structuring_element))


def fill_small_holes(image):
    """Computes the hole filling.

    Args:
      image: A binary image.
    Returns:
      A binary image without holes.
    """
    return (scipy.ndimage.morphology.binary_fill_holes(image))


def remove_small_objects(image, area):
    """Removes the small objects in a binary image whose area is
    less than a given area.

    Args:
      image: A binary image.
      area: An integer.
    Returns:
      A binary image without small objects.
    """
    return (skimage.morphology.remove_small_objects(image, area))


def dilate_mask(mask, structuring_element):
    """Computes the binary morphological dilation.

    Args:
      mask: A binary image.
      structuring_element: A structuring element.
    Returns:
      A binary image.
    """
    return (skimage.morphology.binary_dilation(mask,
                                               structuring_element))

def get_drawn_mask(image,mask):
    """Computes the image with the mask overlapped.

    Args:
      image: An RGB image.
      mask: A binary image.
    Returns:
      An RGB image with the mask drawn with different color.
    """
    colormask = image.copy()
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            if mask[i, j]:
                colormask[i, j, 0] = 70/255
                colormask[i, j, 1] = 253/255
                colormask[i, j, 2] = 52/255

    return colormask
