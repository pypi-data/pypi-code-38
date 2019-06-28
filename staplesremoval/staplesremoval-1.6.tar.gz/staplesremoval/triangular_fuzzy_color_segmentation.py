from skimage import color


def get_number_red_pixels(image):
    """Computes the frequency of red pixels.

    Args:
      image: An RGB image.
    Returns:
      The total pixels of the image and the red pixels.
    """

    total_pixels = image.shape[0]*image.shape[1]

    red_pixels = 0;
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i, j, 0] == 255 and image[i, j, 1] == 0 and image[i, j, 2] == 0:
                red_pixels += 1

    return total_pixels, red_pixels


def triangular_fuzzy_color_segmentation(image):
    """Computes the color segmentation of an image.

    Args:
      image: An RGB image.
    Returns:
        An RGB color segmented image.
    """

    rgb_image = image.copy()
    hsv_image = color.rgb2hsv(rgb_image)

    h_channel = 360 * hsv_image[:, :, 0]

    for i in range(h_channel.shape[0]):
        for j in range(h_channel.shape[1]):

            p_red = fuzzy_segmentation_red_triangular(h_channel[i, j])
            p_darkorange = fuzzy_segmentation_darkorange_triangular(h_channel[i, j])
            p_lightorange = fuzzy_segmentation_lightorange_triangular(h_channel[i, j])
            p_yellow = fuzzy_segmentation_yellow_triangular(h_channel[i, j])
            p_lightgreen = fuzzy_segmentation_lightgreen_triangular(h_channel[i, j])
            p_darkgreen = fuzzy_segmentation_darkgreen_triangular(h_channel[i, j])
            p_aqua = fuzzy_segmentation_aqua_triangular(h_channel[i, j])
            p_blue = fuzzy_segmentation_blue_triangular(h_channel[i, j])
            p_darkpurple = fuzzy_segmentation_darkpurple_triangular(h_channel[i, j])
            p_lightpurple = fuzzy_segmentation_lightpurple_triangular(h_channel[i, j])

            m = max([p_red, p_darkorange, p_lightorange, p_yellow, p_lightgreen, p_darkgreen,
                     p_aqua, p_blue, p_darkpurple, p_lightpurple])

            if m == p_red:
                rgb_image[i, j, 0] = 255
                rgb_image[i, j, 1] = 0
                rgb_image[i, j, 2] = 0
            elif m == p_darkorange:
                rgb_image[i, j, 0] = 255
                rgb_image[i, j, 1] = 140
                rgb_image[i, j, 2] = 0
            elif m == p_lightorange:
                rgb_image[i, j, 0] = 255
                rgb_image[i, j, 1] = 165
                rgb_image[i, j, 2] = 0
            elif m == p_yellow:
                rgb_image[i, j, 0] = 255
                rgb_image[i, j, 1] = 255
                rgb_image[i, j, 2] = 0
            elif m == p_lightgreen:
                rgb_image[i, j, 0] = 144
                rgb_image[i, j, 1] = 238
                rgb_image[i, j, 2] = 144
            elif m == p_darkgreen:
                rgb_image[i, j, 0] = 0
                rgb_image[i, j, 1] = 100
                rgb_image[i, j, 2] = 0
            elif m == p_aqua:
                rgb_image[i, j, 0] = 0
                rgb_image[i, j, 1] = 255
                rgb_image[i, j, 2] = 255
            elif m == p_blue:
                rgb_image[i, j, 0] = 0
                rgb_image[i, j, 1] = 0
                rgb_image[i, j, 2] = 255
            elif m == p_darkpurple:
                rgb_image[i, j, 0] = 128
                rgb_image[i, j, 1] = 0
                rgb_image[i, j, 2] = 128
            elif m == p_lightpurple:
                rgb_image[i, j, 0] = 255
                rgb_image[i, j, 1] = 0
                rgb_image[i, j, 2] = 255

    return rgb_image


def fuzzy_segmentation_red_triangular(h):
    """Computes the triangular membership function of the red colour.

    Args:
      h: The value of the H channel of the pixel
    Returns:
        The membership function
    """

    if 0 <= h <= 30:
        return 1 - h / 30
    elif 330 <= h <= 360:
        return -11 + h / 30
    else:
        return 0


def fuzzy_segmentation_darkorange_triangular(h):
    """Computes the triangular membership function of the dark orange colour.

    Args:
      h: The value of the H channel of the pixel
    Returns:
        The membership function
    """

    if 0 <= h <= 30:
        return h / 30
    elif 30 <= h <= 45:
        return 3 - h / 15
    else:
        return 0


def fuzzy_segmentation_lightorange_triangular(h):
    """Computes the triangular membership function of the light orange colour.

    Args:
      h: The value of the H channel of the pixel
    Returns:
        The membership function
    """

    if 30 <= h <= 45:
        return -2 + h / 15
    elif 45 <= h <= 60:
        return 4 - h / 15
    else:
        return 0


def fuzzy_segmentation_yellow_triangular(h):
    """Computes the triangular membership function of the yellow colour.

    Args:
      h: The value of the H channel of the pixel
    Returns:
        The membership function
    """

    if 45 <= h <= 60:
        return -3 + h / 15
    elif 60 <= h <= 90:
        return 3 - h / 30
    else:
        return 0


def fuzzy_segmentation_lightgreen_triangular(h):
    """Computes the triangular membership function of the light green colour.

    Args:
      h: The value of the H channel of the pixel
    Returns:
        The membership function
    """

    if 60 <= h <= 75:
        return -4 + h / 15
    elif 75 <= h <= 120:
        return 8 / 3 - h / 45
    else:
        return 0


def fuzzy_segmentation_darkgreen_triangular(h):
    """Computes the triangular membership function of the dark green colour.

    Args:
      h: The value of the H channel of the pixel
    Returns:
        The membership function
    """

    if 90 <= h <= 120:
        return -3 + h / 30
    elif 120 <= h <= 180:
        return 3 - h / 60
    else:
        return 0


def fuzzy_segmentation_aqua_triangular(h):
    """Computes the triangular membership function of the aqua colour.

    Args:
      h: The value of the H channel of the pixel
    Returns:
        The membership function
    """

    if 120 <= h <= 180:
        return -2 + h / 60
    elif 180 <= h <= 240:
        return 4 - h / 60
    else:
        return 0


def fuzzy_segmentation_blue_triangular(h):
    """Computes the triangular membership function of the blue colour.

    Args:
      h: The value of the H channel of the pixel
    Returns:
        The membership function
    """

    if 180 <= h <= 240:
        return -3 + h / 60
    elif 240 <= h <= 300:
        return 5 - h / 60
    else:
        return 0


def fuzzy_segmentation_darkpurple_triangular(h):
    """Computes the triangular membership function of the dark purple colour.

    Args:
      h: The value of the H channel of the pixel
    Returns:
        The membership function
    """

    if 240 <= h <= 300:
        return -4 + h / 60
    elif 300 <= h <= 330:
        return 11 - h / 30
    else:
        return 0


def fuzzy_segmentation_lightpurple_triangular(h):
    """Computes the triangular membership function of the light purple colour.

    Args:
      h: The value of the H channel of the pixel
    Returns:
        The membership function
    """

    if 300 <= h <= 330:
        return -10 + h / 30
    elif 330 <= h <= 360:
        return 12 - h / 30;
    else:
        return 0
