from bob.bio.htface.extractor import StyleTransfer
import bob.bio.base

#style_image_paths = ["/idiap/project/hface/databases/polimetric_thermal_database/Registered/Polarimetric/A45_R1_E_S0_f10.png",
#                     "/idiap/project/hface/databases/polimetric_thermal_database/Registered/Polarimetric/A46_R1_E_S0_f10.png",
#                     "/idiap/project/hface/databases/polimetric_thermal_database/Registered/Polarimetric/A47_R1_E_S0_f10.png",
#                     "/idiap/project/hface/databases/polimetric_thermal_database/Registered/Polarimetric/A48_R1_E_S0_f10.png",
#                     "/idiap/project/hface/databases/polimetric_thermal_database/Registered/Polarimetric/A49_R1_E_S0_f10.png",
#                     "/idiap/project/hface/databases/polimetric_thermal_database/Registered/Polarimetric/A50_R1_E_S0_f10.png",
#                     "/idiap/project/hface/databases/polimetric_thermal_database/Registered/Polarimetric/A51_R1_E_S0_f10.png",
#                     "/idiap/project/hface/databases/polimetric_thermal_database/Registered/Polarimetric/A52_R1_E_S0_f10.png",
#                     "/idiap/project/hface/databases/polimetric_thermal_database/Registered/Polarimetric/A53_R1_E_S0_f10.png",
#                     "/idiap/project/hface/databases/polimetric_thermal_database/Registered/Polarimetric/A54_R1_E_S0_f10.png"]

style_image_paths = ["/idiap/project/hface/databases/polimetric_thermal_database/Registered/Polarimetric/A45_R1_E_S0_f10.png"]
style_images = []

for path in style_image_paths:
    style_images.append(bob.io.base.load(path))


import tensorflow as tf

# -- architecture
from bob.learn.tensorflow.network import inception_resnet_v2_batch_norm
architecture = inception_resnet_v2_batch_norm


# --checkpoint-dir
from bob.extension import rc
checkpoint_dir = rc['bob.bio.face_ongoing.casia-webface-inception-v2_batchnorm_gray']


# --style-end-points and -- content-end-points
style_end_points = ["Conv2d_1a_3x3", "Conv2d_2a_3x3", "Conv2d_2b_3x3", "Conv2d_3b_1x1", "Conv2d_4a_3x3"]
content_end_points = ["Mixed_5b", "Block35", "Mixed_6a", "Block17", "Mixed_7a", "Block8"]



scopes = {"InceptionResnetV2/":"InceptionResnetV2/"}
preprocess_fn = tf.image.per_image_standardization

extractor = StyleTransfer(style_images, architecture, checkpoint_dir, scopes,
                                         content_end_points, style_end_points,
                                         preprocess_fn, 
                                         pure_noise=True,
                                         iterations=1000, learning_rate=0.1,
                                         content_weight=1,
                                         style_weight=0.,
                                         denoise_weight=0.)
