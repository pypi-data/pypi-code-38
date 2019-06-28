import numpy
from skimage.color import rgb2hsv
from staplesremoval import remove_staples
from staplesremoval import triangular_fuzzy_color_segmentation
from staplesremoval.trapezoidal_fuzzy_color_segmentation import get_number_red_pixels


def detect_infection(image):
    """First, segment the image in different regions. Second,
    calculate the masks and apply the inpainting method to
    remove the staples. Finally, segment all regions using
    trapezoidal fuzzy membership functions.

    Args:
      image: An RGB image.
    Returns:
      The largest proportion of all sub-images in the image, including the image itself.
    """
    regions = generate_wound_regions(image, 5, 5)
    clean_regions = remove_staples_from_regions(regions)
    segmented_regions = segment_inpainted_regions(clean_regions)

    if len(segmented_regions) == 0:
        return 0
    else:
        return get_red_proportion(segmented_regions)


def get_red_proportion(regions):
    """Computes the largest proportion of all sub-images
    which contains wound in the image, including the image itself.

    Args:
      regions: An array of RGB images.
    Returns:
      The largest proportion of all sub-images in the image, including the image itself.
    """
    total_pixels = 0
    total_red_pixels = 0

    regions_proportions = []

    for image in regions:
        total, total_red = get_number_red_pixels(image)
        regions_proportions.append(total_red/total)
        total_pixels += total
        total_red_pixels += total_red

    regions_proportions.append(total_red_pixels/total_pixels)

    return max(regions_proportions)


def segment_inpainted_regions(regions):
    """Computes the segmentation for all regions in the image
    which contains wound.

    Args:
      regions: An array of RGB images.
    Returns:
      An array of segmented RGB images.
    """
    segmented_regions = [triangular_fuzzy_color_segmentation(image) for image in regions]
    return segmented_regions


def remove_staples_from_regions(regions):
    """Computes the mask and applies the inpainting method
    for all regions in the image which contains wound.

    Args:
      regions: An array of RGB images.
    Returns:
      An array of inpainted RGB images.
    """
    cleaned_regions = [remove_staples(image) for image in regions]
    return cleaned_regions


def generate_wound_regions(image, N_vertical, N_horizontal):
    """Splits the image into N_vertical x N_horizontal regions.

    Args:
      image: An RGB image.
      N_vertical: Number of vertical splits.
      N_horizontal: Number of horizontal splits.
    Returns:
      An array of RGB images that contain wound.
    """
    rgb_image = image.copy()
    height = rgb_image.shape[0]
    width = rgb_image.shape[1]

    vertical_grid = generate_grid(width, N_vertical)
    horizontal_grid = generate_grid(height, N_horizontal)

    wound_images = []

    for i in range(0, len(vertical_grid) - 1):
        for j in range(0, len(horizontal_grid) - 1):
            subimage = rgb_image[horizontal_grid[j]:horizontal_grid[j + 1], vertical_grid[i]:vertical_grid[i + 1], :]
            if image_contains_wound(subimage):
                wound_images.append(subimage)

    return wound_images


def generate_grid(size, N):
    """Generates the pixel range to split the image.

    Args:
      size: One dimension of an image (height or width).
      N: Number of splits.
    Returns:
      A sequence of pixels.
    """
    step = int(size / N)
    sequence = [(step * i) for i in range(0, 5)]
    sequence.append(size)

    return sequence


def image_contains_wound(image):
    """Determines if an image contains wound or not applying
    the separation hyperplane obtained by the SVM.

    Args:
      image: An RGB image.
    Returns:
      A boolean: True if contains wound and False otherwise.
    """
    hsv_image = rgb2hsv(image)
    h_range = numpy.max(hsv_image[:, :, 0]) - numpy.min(hsv_image[:, :, 0])
    v_range = numpy.max(hsv_image[:, :, 2]) - numpy.min(hsv_image[:, :, 2])

    if v_range >= 0.8886531 - 0.1108036 * h_range:
        return True
    else:
        return False
