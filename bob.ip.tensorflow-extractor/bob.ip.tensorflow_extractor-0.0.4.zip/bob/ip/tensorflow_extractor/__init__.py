#!/usr/bin/env python
def scratch_network(inputs, end_point="fc1", reuse=False):

    import tensorflow as tf
    slim = tf.contrib.slim

    # Creating a random network
    initializer = tf.contrib.layers.xavier_initializer(seed=10)
    end_points = dict()

    graph = slim.conv2d(inputs, 10, [3, 3], activation_fn=tf.nn.relu, stride=1,
                        scope='conv1', weights_initializer=initializer,
                        reuse=reuse)
    end_points["conv1"] = graph

    graph = slim.max_pool2d(graph, [4, 4], scope='pool1')
    end_points["pool1"] = graph

    graph = slim.flatten(graph, scope='flatten1')
    end_points["flatten1"] = graph

    graph = slim.fully_connected(graph, 10, activation_fn=None, scope='fc1',
                                 weights_initializer=initializer, reuse=reuse)
    end_points["fc1"] = graph

    return end_points[end_point]


def get_config():
    """Returns a string containing the configuration information.
    """
    import bob.extension
    return bob.extension.get_config(__name__)


from .Extractor import Extractor
from .FaceNet import FaceNet
from .DrGanMSU import  DrGanMSUExtractor
from .Vgg16 import VGGFace, vgg_16
from .MTCNN import MTCNN


# gets sphinx autodoc done right - don't remove it
def __appropriate__(*args):
    """Says object was actually declared here, and not in the import module.
    Fixing sphinx warnings of not being able to find classes, when path is
    shortened. Parameters:

      *args: An iterable of objects to modify

    Resolves `Sphinx referencing issues
    <https://github.com/sphinx-doc/sphinx/issues/3048>`
    """

    for obj in args:
        obj.__module__ = __name__


__appropriate__(
    Extractor,
    FaceNet,
    DrGanMSUExtractor,
    VGGFace,
    MTCNN,
)

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
