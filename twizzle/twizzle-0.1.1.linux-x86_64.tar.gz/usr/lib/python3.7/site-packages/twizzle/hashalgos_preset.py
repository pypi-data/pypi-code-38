"""
This module defines common perceptual image hashing algorithms that can be used as an example
"""

import numpy
import cv2


def __resize_image_downscale(aInputImage, lImageWidth, lImageHeight):
    """resizing an image to a given size"""
    return cv2.resize(aInputImage, (lImageWidth, lImageHeight), interpolation=cv2.INTER_AREA)


def __convert_image_to_grayscale(aInputImage):
    """converting an image to grayscale"""
    return cv2.cvtColor(aInputImage, cv2.COLOR_BGR2GRAY)


def average_hash(image, hash_size=8):
    """
    Average Hash computation

    Implementation follows http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html

    Step by step explanation: https://www.safaribooksonline.com/blog/2013/11/26/image-hashing-with-python/
    """
    if hash_size < 0:
        raise ValueError("Hash size must be positive")

    # reduce size and complexity, then covert to grayscale
    # image = image.convert("L").resize((hash_size, hash_size),
    # Image.ANTIALIAS)
    image = __convert_image_to_grayscale(image)
    pixels = __resize_image_downscale(image, hash_size, hash_size)

    # find average pixel value; 'pixels' is an array of the pixel values,
    # ranging from 0 (black) to 255 (white)
    # pixels = numpy.array(image.getdata()).reshape((hash_size, hash_size))
    avg = pixels.mean()

    # create string of bits
    diff = pixels > avg
    # make a hash
    return diff.flatten()


def dhash(image, hash_size=8):
    """
    Difference Hash computation.

    following http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html

    computes differences horizontally

    """
    if hash_size < 0:
        raise ValueError("Hash size must be positive")

    image = __convert_image_to_grayscale(image)
    pixels = __resize_image_downscale(
        image, hash_size + 1, hash_size)
    # compute differences between columns
    diff = pixels[:, 1:] > pixels[:, :-1]
    return diff.flatten()
