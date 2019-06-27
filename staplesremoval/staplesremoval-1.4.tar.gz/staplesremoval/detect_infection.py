import numpy
from skimage.color import rgb2hsv
from staplesremoval import remove_staples
from staplesremoval import triangular_fuzzy_color_segmentation
from staplesremoval.triangular_fuzzy_color_segmentation import get_number_red_pixels
from skimage import io


def detect_infection(image):
    regions = generate_wound_regions(image, 5, 5)
    clean_regions = remove_staples_from_regions(regions)
    segmented_regions = segment_inpainted_regions(clean_regions)

    if len(segmented_regions) == 0:
        return 0
    else:
        return get_red_proportion(segmented_regions)


def get_red_proportion(regions):
    total_pixels = 0
    total_red_pixels = 0
    for image in regions:
        total, total_red = get_number_red_pixels(image)
        total_pixels += total
        total_red_pixels += total_red

    return total_red_pixels/total_pixels


def segment_inpainted_regions(regions):
    segmented_regions = [triangular_fuzzy_color_segmentation(image) for image in regions]
    return segmented_regions


def remove_staples_from_regions(regions):
    cleaned_regions = [remove_staples(image) for image in regions]
    return cleaned_regions


def generate_wound_regions(image, N_vertical, N_horizontal):
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
    step = int(size / N)
    sequence = [(step * i) for i in range(0, 5)]
    sequence.append(size)

    return sequence


def image_contains_wound(image):
    hsv_image = rgb2hsv(image)
    h_range = numpy.max(hsv_image[:, :, 0]) - numpy.min(hsv_image[:, :, 0])
    v_range = numpy.max(hsv_image[:, :, 2]) - numpy.min(hsv_image[:, :, 2])

    if v_range >= 0.8886531 - 0.1108036 * h_range:
        return True
    else:
        return False
