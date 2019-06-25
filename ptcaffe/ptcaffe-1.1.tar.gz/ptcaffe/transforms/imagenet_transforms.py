from __future__ import division, print_function
from PIL import Image
import numpy as np
import torch

__all__ = ['Lighting', 'TFResizer']

class Lighting(object):
    """Lighting noise(AlexNet - style PCA - based noise)"""

    def __init__(self, alphastd):
        self.alphastd = alphastd
        self.eigval = torch.Tensor([0.2175, 0.0188, 0.0045])
        self.eigvec = torch.Tensor([
            [-0.5675,  0.7192,  0.4009],
            [-0.5808, -0.0045, -0.8140],
            [-0.5836, -0.6948,  0.4203],
        ])

    def __call__(self, img):
        if self.alphastd == 0:
            return img

        alpha = img.new().resize_(3).normal_(0, self.alphastd)
        rgb = self.eigvec.type_as(img).clone()\
            .mul(alpha.view(1, 3).expand(3, 3))\
            .mul(self.eigval.view(1, 3).expand(3, 3))\
            .sum(1).squeeze()

        return img.add(rgb.view(3, 1, 1).expand_as(img))

class TFResizer(object):
    def __init__(self, size):
        import tensorflow as tf
        self.data = tf.placeholder(tf.float32, [1,None,None,3])
        self.resized = tf.image.resize_bilinear(self.data, [size,size])
        session_config = tf.ConfigProto(allow_soft_placement=True,
                                log_device_placement=False)
        session_config.gpu_options.allow_growth=True
        self.sess = tf.Session(config = session_config)

    def __call__(self, image):
        image = np.array(image)
        im = image.reshape((1,)+image.shape)
        resized = self.sess.run(self.resized, feed_dict={self.data: im})
        resized = resized.reshape(resized.shape[1:])
        return Image.fromarray(resized.astype(np.uint8))
