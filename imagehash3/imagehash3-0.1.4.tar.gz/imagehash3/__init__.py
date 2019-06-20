name="imagehash3"

# https://github.com/JohannesBuchner/imagehash.git

from PIL import Image
import numpy as np
import os


def hash_to_int_string(hash):
    hash = hash.flatten()
    hash = [str(int(i)) for i in hash]
    return str(int(''.join(hash), 2))


def average_hash(image, hash_size=32, resize_func=Image.BICUBIC ):
    if hash_size < 2:
        raise ValueError("Hash size must be greater than or equal to 2")

    # reduce size and complexity, then covert to grayscale
    image = image.convert("L")
    image = image.resize((hash_size, hash_size), resize_func)

    # find average pixel value; 'pixels' is an array of the pixel values, ranging from 0 (black) to 255 (white)
    pixels = np.asarray(image)
    avg = pixels.mean()
    diff = pixels > avg
    return hash_to_int_string(diff)


def phash(image, hash_size=32, highfreq_factor=4, resize_func=Image.BICUBIC):
    if hash_size < 2:
        raise ValueError("Hash size must be greater than or equal to 2")

    import scipy.fftpack
    img_size = hash_size * highfreq_factor
    image = image.convert("L").resize((img_size, img_size), resize_func)
    pixels = np.asarray(image)
    dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
    dctlowfreq = dct[:hash_size, :hash_size]
    med = np.median(dctlowfreq)
    diff = dctlowfreq > med
    return hash_to_int_string(diff)


def dhash(image, hash_size=32, resize_func =Image.BICUBIC):

    if hash_size < 2:
        raise ValueError("Hash size must be greater than or equal to 2")

    image = image.convert("L").resize((hash_size + 1, hash_size), resize_func)
    pixels = np.asarray(image)

    # compute differences between columns
    diff = pixels[:, 1:] > pixels[:, :-1]
    return hash_to_int_string(diff)

def whash(image, hash_size = 32, image_scale = None, mode = 'haar', remove_max_haar_ll = True, resize_func =Image.BICUBIC):
    import pywt
    if image_scale is not None:
        assert image_scale & (image_scale - 1) == 0, "image_scale is not power of 2"
    else:
        image_natural_scale = 2**int(np.log2(min(image.size)))
        image_scale = max(image_natural_scale, hash_size)

    ll_max_level = int(np.log2(image_scale))

    level = int(np.log2(hash_size))
    assert hash_size & (hash_size-1) == 0, "hash_size is not power of 2"
    assert level <= ll_max_level, "hash_size in a wrong range"
    dwt_level = ll_max_level - level

    image = image.convert("L").resize((image_scale, image_scale), resize_func)
    pixels = np.asarray(image) / 255

    # Remove low level frequency LL(max_ll) if @remove_max_haar_ll using haar filter
    if remove_max_haar_ll:
        coeffs = pywt.wavedec2(pixels, 'haar', level = ll_max_level)
        coeffs = list(coeffs)
        coeffs[0] *= 0
        pixels = pywt.waverec2(coeffs, 'haar')

    # Use LL(K) as freq, where K is log2(@hash_size)
    coeffs = pywt.wavedec2(pixels, mode, level = dwt_level)
    dwt_low = coeffs[0]

    # Substract median and compute hash
    med = np.median(dwt_low)
    diff = dwt_low > med
    return hash_to_int_string(diff)

