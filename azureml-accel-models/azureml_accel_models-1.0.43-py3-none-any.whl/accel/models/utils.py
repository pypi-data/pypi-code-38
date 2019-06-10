# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for models - mostly preprocessing related."""
import warnings

try:
    import tensorflow as tf
except ImportError:
    warnings.warn("azureml-accel-models requires tensorflow version >= 1.6, please install it")


def preprocess_array(in_images, order='RGB', scaling_factor=1.0,
                     output_height=224, output_width=224, preserve_aspect_ratio=True):
    """Create a tensorflow op that takes an array of image bytes and returns regularized images.

    :param in_images: [?] dim tensor of image bytes. (Typically a placeholder)
    :param order: order of channels - either 'BGR' or 'RGB'
    :param scaling_factor: multiplier for channel values
    :param output_height: output image height
    :param output_width: output image width
    :param preserve_aspect_ratio: if True, preserve image aspect ratio while scaling
    :return: [?, output_height, output_width, 3] dim tensor of float32 pixel values of the image.
    """
    _decode = _decode_factory(order, scaling_factor, output_height,
                              output_width, preserve_aspect_ratio)
    return tf.map_fn(_decode, in_images, tf.float32, name="map_normalize_jpeg")


def _decode_factory(order, scaling_factor, output_height, output_width, preserve_aspect_ratio):
    if order != 'BGR' and order != 'RGB':
        raise ValueError("can only construct in RGB or BGR order.")

    def _decode(tensor):
        return tf.squeeze(_preprocess_tensor(tensor, order, scaling_factor,
                                             output_height, output_width, preserve_aspect_ratio))

    return _decode


def _preprocess_tensor(tensor, order, scaling_factor, output_height, output_width, preserve_aspect_ratio):
    image = tf.image.decode_png(tensor, 3)
    image = tf.cast(image, dtype=tf.float32)
    resize_min = 256

    if preserve_aspect_ratio:
        image = _aspect_preserving_resize(image, resize_min)
        output_height = min(output_height, resize_min)
        output_width = min(output_height, resize_min)
        image = _central_crop(image, output_height, output_width)
    else:
        image = _simple_resize(image, output_height, output_width)

    image.set_shape([output_height, output_width, 3])
    image = tf.to_float(image)
    image = tf.expand_dims(image, 0)

    slice_red = tf.slice(image, [0, 0, 0, 0], [
                         1, output_height, output_width, 1])
    slice_green = tf.slice(image, [0, 0, 0, 1], [
                           1, output_height, output_width, 1])
    slice_blue = tf.slice(image, [0, 0, 0, 2], [
                          1, output_height, output_width, 1])

    sub_red = tf.subtract(slice_red, 123.68)
    sub_green = tf.subtract(slice_green, 116.779)
    sub_blue = tf.subtract(slice_blue, 103.939)
    if order == 'BGR':
        return tf.concat([sub_blue, sub_green, sub_red], 3) * scaling_factor
    elif order == 'RGB':
        return tf.concat([sub_red, sub_green, sub_blue], 3) * scaling_factor


def _simple_resize(image, output_height, output_width):
    """Resize images without preserving the original aspect ratio.

    :param image: A 3-D image `Tensor`.
    :param output_height: Target height.
    :param output_width: Target width.

    :return: resized_image: A 3-D tensor containing the resized image.
    """
    image = tf.expand_dims(image, 0)
    resized_image = tf.image.resize_bilinear(image, [output_height, output_width],
                                             align_corners=False)
    resized_image = tf.squeeze(resized_image)
    resized_image.set_shape([None, None, 3])

    return resized_image


def _aspect_preserving_resize(image, smallest_side):
    """Resize images preserving the original aspect ratio.

    :param image: A 3-D image `Tensor`.
    :param smallest_side: A python integer or scalar `Tensor` indicating the size of
      the smallest side after resize.

    :return resized_image: A 3-D tensor containing the resized image.

    """
    smallest_side = tf.convert_to_tensor(smallest_side, dtype=tf.int32)

    shape = tf.shape(image)
    height = shape[0]
    width = shape[1]
    new_height, new_width = _smallest_size_at_least(
        height, width, smallest_side)
    image = tf.expand_dims(image, 0)
    resized_image = tf.image.resize_bilinear(image, [new_height, new_width],
                                             align_corners=False)
    resized_image = tf.squeeze(resized_image)
    resized_image.set_shape([None, None, 3])

    return resized_image


def _central_crop(image, crop_height, crop_width):
    """Perform central crops of the given image list.

    :param image_list: a list of image tensors of the same dimension but possibly
      varying channel.
    :param crop_height: the height of the image following the crop.
    :param crop_width: the width of the image following the crop.

    :return: the list of cropped images.

    """
    image_height = tf.shape(image)[0]
    image_width = tf.shape(image)[1]

    offset_height = (image_height - crop_height) / 2
    offset_width = (image_width - crop_width) / 2

    return _crop(image, offset_height, offset_width, crop_height, crop_width)


def _crop(image, offset_height, offset_width, crop_height, crop_width):
    """Crop the given image using the provided offsets and sizes.

    Note that the method doesn't assume we know the input image size but it does
    assume we know the input image rank.

    :param image: an image of shape [height, width, channels].
    :param offset_height: a scalar tensor indicating the height offset.
    :param offset_width: a scalar tensor indicating the width offset.
    :param crop_height: the height of the cropped image.
    :param crop_width: the width of the cropped image.

    :return:
    the cropped (and resized) image.

    :raises: InvalidArgumentError: if the rank is not 3 or if the image dimensions are
    less than the crop size.

    """
    original_shape = tf.shape(image)

    rank_assertion = tf.Assert(
        tf.equal(tf.rank(image), 3),
        ['Rank of image must be equal to 3.'])
    with tf.control_dependencies([rank_assertion]):
        cropped_shape = tf.stack([crop_height, crop_width, original_shape[2]])

    size_assertion = tf.Assert(
        tf.logical_and(
            tf.greater_equal(original_shape[0], crop_height),
            tf.greater_equal(original_shape[1], crop_width)),
        ['Crop size greater than the image size.'])

    offsets = tf.to_int32(tf.stack([offset_height, offset_width, 0]))

    # Use tf.slice instead of crop_to_bounding box as it accepts tensors to
    # define the crop size.
    with tf.control_dependencies([size_assertion]):
        image = tf.slice(image, offsets, cropped_shape)

    return tf.reshape(image, cropped_shape)


def _smallest_size_at_least(height, width, smallest_side):
    """Compute new shape with the smallest side equal to `smallest_side`.

    Computes new shape with the smallest side equal to `smallest_side` while
    preserving the original aspect ratio.

    :param height: an int32 scalar tensor indicating the current height.
    :param width: an int32 scalar tensor indicating the current width.
    :param smallest_side: A python integer or scalar `Tensor` indicating the size of
      the smallest side after resize.

    :returns:new_height: an int32 scalar tensor indicating the new height.
             new_width: and int32 scalar tensor indicating the new width.

    """
    smallest_side = tf.convert_to_tensor(smallest_side, dtype=tf.int32)

    height = tf.to_float(height)
    width = tf.to_float(width)
    smallest_side = tf.to_float(smallest_side)

    scale = tf.cond(tf.greater(height, width),
                    lambda: smallest_side / width,
                    lambda: smallest_side / height)
    new_height = tf.to_int32(height * scale)
    new_width = tf.to_int32(width * scale)
    return new_height, new_width
