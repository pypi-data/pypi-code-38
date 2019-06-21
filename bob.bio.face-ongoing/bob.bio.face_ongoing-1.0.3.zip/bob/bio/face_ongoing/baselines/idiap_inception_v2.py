#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import pkg_resources
from bob.bio.base.baseline import Baseline


# idiap_casia_inception_v2_centerloss_gray
preprocessors = dict()        
preprocessors["default"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/eyes_gray_crop.py")
preprocessors["ijbc"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/default_gray_crop.py")
preprocessors["ijba"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/default_gray_crop.py")

idiap_casia_inception_v2_centerloss_gray = Baseline(name = "idiap_casia_inception_v2_centerloss_gray",\
                                                    extractor = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/casiawebface/inception_resnet_v2/centerloss_gray.py"),\
                                                    algorithm = 'distance-cosine',\
                                                    preprocessors=preprocessors
)


# idiap_casia_inception_v2_centerloss_rgb
preprocessors = dict()
preprocessors["default"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/eyes_rgb_crop.py")
preprocessors["ijbc"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/default_rgb_crop.py")
preprocessors["ijba"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/default_rgb_crop.py")

idiap_casia_inception_v2_centerloss_rgb = Baseline(name = "idiap_casia_inception_v2_centerloss_rgb",\
                                                   extractor=pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/casiawebface/inception_resnet_v2/centerloss_rgb.py"),\
                                                   algorithm = 'distance-cosine',\
                                                   preprocessors=preprocessors)
                                                   
                                                   
                                                   
############# MS-CELEB

# idiap_casia_inception_v2_centerloss_rgb
preprocessors = dict()
preprocessors["default"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/eyes_rgb_crop.py")
preprocessors["ijbc"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/default_rgb_crop.py")
preprocessors["ijba"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/default_rgb_crop.py")

idiap_msceleb_inception_v2_centerloss_rgb = Baseline(name = "idiap_msceleb_inception_v2_centerloss_rgb",\
                                                   extractor=pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/msceleb/inception_resnet_v2/centerloss_rgb.py"),\
                                                   algorithm = 'distance-cosine',\
                                                   preprocessors=preprocessors)
                                                   

                                                   
preprocessors = dict()
preprocessors["default"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/eyes_gray_crop.py")
preprocessors["ijbc"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/default_gray_crop.py")
preprocessors["ijba"] = pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/inception_resnet_preprocessors/default_gray_crop.py")

idiap_msceleb_inception_v2_centerloss_gray = Baseline(name = "idiap_msceleb_inception_v2_centerloss_gray",\
                                                   extractor=pkg_resources.resource_filename("bob.bio.face_ongoing", "configs/baselines/msceleb/inception_resnet_v2/centerloss_gray.py"),\
                                                   algorithm = 'distance-cosine',\
                                                   preprocessors=preprocessors)
