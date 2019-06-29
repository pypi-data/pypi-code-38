import cv2


def rotate(image, angle, center=None, scale=1.0):
    """
    rotate given %image by given %angle.
    :param image: input image as Mat object.
    :param angle: clockwise angle as integer.
    :param center: center point as point2f object.
    :param scale: isotropic scale factor.
    :return: rotated image by given angle.
    """

    # grab the dimensions of the image
    (h, w) = image.shape[:2]

    # if the center is None, initialize it as the center of
    # the image
    if center is None:
        center = (w // 2, h // 2)

    # perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))

    # return the rotated image
    return rotated


def resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    """

    :param image:
    :param width:
    :param height:
    :param inter:
    :return:
    """
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized