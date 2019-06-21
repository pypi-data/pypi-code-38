#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>


from bob.bio.base.baseline import Baseline
import pkg_resources


class LightCNN(Baseline):
    """
    Light CNN Baseline
    """

    def __init__(self, **kwargs):

        name              = "lightcnn"
        extractor         = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/lightcnn_extractor.py")
        preprocessors      = dict()
        preprocessors["default"] = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/lightcnn_preprocessor.py")
        preprocessors["thermal"] = pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/lightcnn_preprocessor_polathermal.py")
        algorithm = "distance-cosine"

        self.baseline_type     = "Standard FaceRec"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None

        super(LightCNN, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)
       

htface_lightcnn = LightCNN()


class Facenet(Baseline):
    """
    Facenet CNN Baseline
    """

    def __init__(self, **kwargs):

        name              = "facenet"
        extractor         = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/facenet_sandberg/inception_v1.py")
        preprocessors     = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/facenet_preprocessor.py")}
        algorithm = "distance-cosine"
               
        self.baseline_type     = "Standard FaceRec"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None

        super(Facenet, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)

htface_facenet = Facenet()


class VGG16(Baseline):
    """
    VGG16 CNN Baseline
    """

    def __init__(self, **kwargs):
 
        name              = "vgg16"
        extractor         = "vgg_features"
        preprocessors      = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/vgg16_preprocessor.py")}
        algorithm          = "distance-cosine"

        self.baseline_type     = "Standard FaceRec"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None

        super(VGG16, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)

htface_vgg16 = VGG16()


##########################
# INCEPTION MSCELEB MODELS
##########################


class Inceptionv1_gray(Baseline):
    """
    Inception v1 gray
    """

    def __init__(self, **kwargs):

        name              = "htface_idiap_msceleb_inception_v1_centerloss_gray"
        extractor         = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/msceleb/inception_resnet_v1/centerloss_gray.py")
        preprocessors      = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm = "distance-cosine"
 
        self.baseline_type     = "Standard FaceRec"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None

        super(Inceptionv1_gray, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)

htface_idiap_msceleb_inception_v1_centerloss_gray = Inceptionv1_gray()


class Inceptionv1_rgb(Baseline):
    """
    Inception v1 rgb
    """

    def __init__(self, **kwargs):

        name              = "htface_idiap_msceleb_inception_v1_centerloss_rgb"
        extractor         = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/msceleb/inception_resnet_v1/centerloss_rgb.py")
        preprocessors      = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/facenet_preprocessor.py")}
        algorithm = "distance-cosine"
 
        self.baseline_type     = "Standard FaceRec"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None

        super(Inceptionv1_rgb, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)

htface_idiap_msceleb_inception_v1_centerloss_rgb = Inceptionv1_rgb()


class Inceptionv2_gray(Baseline):
    """
    Inception v2 gray
    """

    def __init__(self, **kwargs):

        name              = "htface_idiap_casia_inception_v2_centerloss_gray"
        extractor         = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/msceleb/inception_resnet_v2/centerloss_gray.py")
        preprocessors      = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/inception_resnet_v2_gray_preprocessor.py")}
        algorithm = "distance-cosine"

        self.baseline_type     = "Standard FaceRec"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None

        super(Inceptionv2_gray, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)

htface_idiap_msceleb_inception_v2_centerloss_gray = Inceptionv2_gray()

       
class Inceptionv2_rgb(Baseline):
    """
    VGG16 CNN Baseline
    """

    def __init__(self, **kwargs):

        name              = "htface_idiap_casia_inception_v2_centerloss_rgb"
        extractor         = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/msceleb/inception_resnet_v2/centerloss_rgb.py")
        preprocessors      = {"default": pkg_resources.resource_filename("bob.bio.htface", "configs/experiments/standard_facerec/facenet_preprocessor.py")}
        algorithm = "distance-cosine"

        self.baseline_type     = "Standard FaceRec"
        self.reuse_extractor   = True

        # train cnn
        self.estimator         = None
        self.preprocessed_data = None

        super(Inceptionv2_rgb, self).__init__(name, preprocessors, extractor, algorithm, **kwargs)

htface_idiap_msceleb_inception_v2_centerloss_rgb = Inceptionv2_rgb()

