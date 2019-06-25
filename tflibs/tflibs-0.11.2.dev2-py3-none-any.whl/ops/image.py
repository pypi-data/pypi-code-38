"""
    Image ops
    ~~~~~~~~~
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools

import tensorflow as tf
import cv2


def normalize(images):
    images = tf.image.convert_image_dtype(images, tf.float32)
    # [0, 1] --> [-1, 1]
    images -= 0.5
    images *= 2.

    return images


def decode_image(encoded_image, image_shape, image_format=None, conditional=False):
    # TODO: Fuse decode and crop
    if conditional:
        image = tf.cond(tf.equal(image_format, 'raw', name='is_raw'),
                        true_fn=lambda: tf.decode_raw(encoded_image, tf.uint8),
                        false_fn=lambda: tf.image.decode_image(encoded_image),
                        name='decoded_image')
    else:
        image = tf.image.decode_image(encoded_image)
    image = tf.reshape(image, image_shape)

    return image


def normalize_images(images):
    with tf.name_scope('normalize_images', values=[images]):
        images -= tf.reduce_min(images)
        return images / tf.reduce_max(images)


def concat_images(*list_images, shape=(1, -1), normalize=True):
    with tf.name_scope('concat_images', values=list_images):
        if normalize:
            list_images = list(map(normalize_images, list_images))
        num_images = len(list_images)

        if shape[0] == -1:
            assert num_images % shape[1] == 0

            num_rows = num_images // shape[1]
            num_columns = shape[1]

        elif shape[1] == -1:
            assert num_images % shape[0] == 0

            num_rows = shape[0]
            num_columns = num_images // shape[0]
        else:
            num_rows = shape[0]
            num_columns = shape[1]

        rows = list(map(lambda r: tf.concat(list_images[r * num_columns:(r + 1) * num_columns], axis=2),
                        range(num_rows)))
        return tf.concat(rows, axis=1)


def rgb2ycrcb(inputs: tf.Tensor):
    with tf.name_scope('rgb2ycrcb'):
        ycrcb = tf.py_func(functools.partial(cv2.cvtColor, code=cv2.COLOR_RGB2YCrCb),
                           [inputs],
                           tf.uint8)
        ycrcb.set_shape((None, None, 3))

        return ycrcb


def random_crop_op(from_size: tf.Tensor, crop_size: tf.Tensor):
    with tf.name_scope('random_crop'):
        sample_space = from_size - crop_size

        sampled_height = tf.random_uniform((), maxval=sample_space[0], dtype=tf.int32)
        sampled_width = tf.random_uniform((), maxval=sample_space[1], dtype=tf.int32)

        def random_crop(inputs: tf.Tensor, scale: tf.Tensor = 1):
            offset = (sampled_height * scale, sampled_width * scale)
            target = (crop_size * scale, crop_size * scale)

            return tf.image.crop_to_bounding_box(inputs, *offset, *target)

        return random_crop
