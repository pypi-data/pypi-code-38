#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import numpy
import os
from . import Extractor, download_file
import logging
import bob.extension.download
logger = logging.getLogger(__name__)


class LightCNN(Extractor):
    """
    Extract features using the Deep Face Representation model (LightCNN)
    https://github.com/AlfredXiangWu/face_verification_experiment
    and the paper::

        @article{wulight,
          title={A Light CNN for Deep Face Representation with Noisy Labels},
          author={Wu, Xiang and He, Ran and Sun, Zhenan and Tan, Tieniu}
          journal={arXiv preprint arXiv:1511.02683},
          year={2015}
        }

    According to the issue #82, the feature layers are: The feature layer for A
    model is eltwise6 ant it is eltwise_fc1 for B and C model.

    """

    def __init__(self, end_cnn="eltwise_fc1", model_version="LightenedCNN_C"):
        """
        LightCNN constructor

        Parameters
        ----------
        end_cnn : :obj:`str`, optional
            The name of the layer that you want to use as a feature.
        model_version : :obj:`str`, optional
            Which model to use.
        """

        deploy_architecture = os.path.join(
            LightCNN.get_protofolder(), model_version + "_deploy.prototxt")
        model = os.path.join(
            LightCNN.get_modelfolder(), model_version + ".caffemodel")

        if not (os.path.exists(deploy_architecture) and os.path.exists(model)):
            zip_file = os.path.join(LightCNN.get_modelpath(),
                                    "face_verification_experiment.zip")
            urls = [
                # This is a private link at Idiap to save bandwidth.
                "http://beatubulatest.lab.idiap.ch/private/wheels/gitlab/"
                "face_verification_experiment.zip",
                # this works for everybody
                "https://github.com/AlfredXiangWu/face_verification_experiment/"
                "archive/master.zip",
            ]
            bob.extension.download.download_and_unzip(urls, zip_file)
            
            # Untar the C modeli
            import tarfile
            c_model_folder = LightCNN.get_modelfolder()
            c_model_paths = [os.path.join(c_model_folder, 'LightenedCNN_C.tar.gz'),
                             os.path.join(c_model_folder, 'LightenedCNN_C.tar.gz00'),
                             os.path.join(c_model_folder, 'LightenedCNN_C.tar.gz01')]
            with open(c_model_paths[1], 'rb') as f0, \
                 open(c_model_paths[2], 'rb') as f1, \
                 open(c_model_paths[0], 'wb') as fw:
                
                fw.write(f0.read())
                fw.write(f1.read())
        
            with tarfile.open(name=c_model_paths[0], mode='r:gz') as t:
                t.extractall(c_model_folder)
                                    
        super(LightCNN, self).__init__(
            deploy_architecture, model, end_cnn
        )
        self.model_version = model_version

    def __call__(self, image):
        """
        Forward the image with the loaded neural network.

        Parameters
        ----------
        image : numpy.array
            The image to be forwarded into the network. The image should be a
            128x128 gray image with 40 pixels between two eye centers and 48
            pixels between eye centers and mouth center. The image range should
            be [0, 1].

        Returns
        -------
        numpy.array
            The extracted features.
        """

        assert image.ndim == 2
        assert image.max() <= 1.001
        h, w = image.shape
        assert h == w == 128
        formatted_image = numpy.reshape(image, (1, 1, h, w)).astype(float)
        output = self.net.forward([self.end_cnn], data=formatted_image)
        return output[self.end_cnn].copy().flatten()

    @staticmethod
    def get_modelpath():
        import pkg_resources
        return pkg_resources.resource_filename(__name__, 'data')

    @staticmethod
    def get_modelfolder():
        return os.path.join(LightCNN.get_modelpath(),
                            'face_verification_experiment-master', 'model')

    @staticmethod
    def get_protofolder():
        return os.path.join(LightCNN.get_modelpath(),
                            'face_verification_experiment-master', 'proto')

