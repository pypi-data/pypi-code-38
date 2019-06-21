#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.ip.tensorflow_extractor

from bob.learn.tensorflow.network import inception_resnet_v2_batch_norm
#from bob.bio.htface.architectures.inception_v2_batch_norm import inception_resnet_v2_adapt_first_head

from bob.bio.htface.architectures.inception_v2_batch_norm import inception_resnet_v2_adapt_layers_1_4_head
from bob.bio.htface.architectures.inception_v2_batch_norm import inception_resnet_v2_adapt_layers_1_5_head


import tensorflow as tf
from bob.extension import rc
from bob.bio.face_ongoing.extractor import TensorflowEmbedding
from bob.bio.htface.extractor import SiameseEmbeddingDumpFirstLayer
#model_filename = "/idiap/temp/tpereira/HTFace/cnn/siamese_inceptionv2_adapt_1_4_nonshared_batch_norm/pola_thermal/VIS-thermal-overall-split1/"

#model_filename = "/idiap/temp/tpereira/HTFace/cnn/siamese_inceptionv2_adapt_1_5_nonshared_batch_norm/cuhk_cufs/search_split1_p2s/"

#model_filename = "/idiap/temp/tpereira/HTFace/cnn/siamese_inceptionv2_adapt_1_5_nonshared_batch_norm/cuhk_cufsf/search_split1_p2s/"

#model_filename = "/idiap/temp/tpereira/HTFace/cnn/siamese_inceptionv2_adapt_1_4_nonshared_batch_norm_euclidean_loss/pola_thermal/VIS-thermal-overall-split1/"

#model_filename = "/idiap/temp/tpereira/HTFace/cnn/siamese_inceptionv2_adapt_1_4_nonshared_batch_norm_random_pairs/pola_thermal/VIS-thermal-overall-split1/"

model_filename = "/idiap/temp/tpereira/HTFace/cnn/styledsu_siamese_inceptionv2_adapt_1_4_betas_nonshared_batch_norm/pola_thermal/VIS-thermal-overall-split1/"

#model_filename = rc["bob.bio.face_ongoing.msceleb-inception-v2_batchnorm_gray"]

#########
# Extraction
#########

# regular net
#inputs = tf.placeholder(tf.float32, shape=(1, 160, 160, 1))

# Taking the embedding
#prelogits, end_points = inception_resnet_v2_batch_norm(tf.stack([tf.image.per_image_standardization(i) for i in tf.unstack(inputs)]), mode=tf.estimator.ModeKeys.PREDICT)

#import ipdb; ipdb.set_trace()
#embedding = tf.nn.l2_normalize(prelogits, dim=1, name="embedding")
#extractor = TensorflowEmbedding(bob.ip.tensorflow_extractor.Extractor(model_filename, inputs, embedding))

#extractor = TensorflowEmbedding(bob.ip.tensorflow_extractor.Extractor(model_filename, inputs, tf.nn.l2_normalize(end_points["Conv2d_1a_3x3"],dim=1)))

#extractor = TensorflowEmbedding(bob.ip.tensorflow_extractor.Extractor(model_filename, inputs, tf.nn.l2_normalize(end_points["Conv2d_3b_1x1"], dim=1)))

#extractor = TensorflowEmbedding(bob.ip.tensorflow_extractor.Extractor(model_filename, inputs, tf.nn.l2_normalize(end_points["Conv2d_4a_3x3"], dim=1)))


#extractor = TensorflowEmbedding(bob.ip.tensorflow_extractor.Extractor(model_filename, inputs, tf.nn.l2_normalize(end_points["Mixed_5b"], dim=1)))

#extractor = TensorflowEmbedding(bob.ip.tensorflow_extractor.Extractor(model_filename, inputs, tf.nn.l2_normalize(end_points["Mixed_6a"], dim=1)))

#extractor = TensorflowEmbedding(bob.ip.tensorflow_extractor.Extractor(model_filename, inputs, tf.nn.l2_normalize(end_points["Mixed_7a"], dim=1)))

#extractor = TensorflowEmbedding(bob.ip.tensorflow_extractor.Extractor(model_filename, inputs, tf.nn.l2_normalize(end_points["Conv2d_7b_1x1"], dim=1)))


#extractor = TensorflowEmbedding(bob.ip.tensorflow_extractor.Extractor(model_filename, inputs, tf.nn.l2_normalize(end_points["PreLogitsFlatten"], dim=1)))


#Mixed_5b

# DUMP FIRST
#architecture = inception_resnet_v2_adapt_first_head
architecture = inception_resnet_v2_adapt_layers_1_4_head

#architecture = inception_resnet_v2_adapt_layers_1_5_head

#import ipdb; ipdb.set_trace()
extractor = SiameseEmbeddingDumpFirstLayer(model_filename, architecture, shape=(1, 160, 160, 1))

