from keras.applications import (
    densenet, inception_v3, mobilenetv2, nasnet,
    resnet50, xception,
)
from keras.layers import (
    Activation, Add, Dropout, Input, MaxPooling2D,
    UpSampling2D,
)
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import Conv2D
from keras.layers.core import Dense, Flatten, Lambda
from keras.layers.normalization import BatchNormalization
from keras.models import Model, Sequential
from keras.utils import multi_gpu_model

from .config_lib import (
    DeblurConfig, ImageClassificationConfig,
    MultiLabelClassificationConfig,
)
from .layers_lib import ReflectionPadding2D, res_block


####################IMAGE_CLASSIFICATION_MODEL####################
def image_classification_model(num_classes, gpu_num, model_type):
    if model_type == 'densenet121':
        model = densenet.DenseNet121(weights=None, classes=num_classes,
                                     input_shape=ImageClassificationConfig.INPUT_SHAPE)
    elif model_type == 'inception_v3':
        model = inception_v3.InceptionV3(weights=None, classes=num_classes,
                                         input_shape=ImageClassificationConfig.INPUT_SHAPE)
    elif model_type == 'inception_resnet_v2':
        model = inception_v3.InceptionV3(weights=None, classes=num_classes,
                                         input_shape=ImageClassificationConfig.INPUT_SHAPE)
    elif model_type == 'mobilenet_v2':
        model = mobilenetv2.MobileNetV2(weights=None, classes=num_classes,
                                        input_shape=ImageClassificationConfig.INPUT_SHAPE)
    elif model_type == 'nasnet_large':
        model = nasnet.NASNetLarge(weights=None, classes=num_classes,
                                   input_shape=ImageClassificationConfig.INPUT_SHAPE)
    elif model_type == 'nasnet_mobile':
        model = nasnet.NASNetMobile(weights=None, classes=num_classes,
                                    input_shape=ImageClassificationConfig.INPUT_SHAPE)
    elif model_type == 'xception':
        model = xception.Xception(weights=None, classes=num_classes,
                                  input_shape=ImageClassificationConfig.INPUT_SHAPE)
    elif model_type == 'resnet50':
        model = resnet50.ResNet50(weights=None, classes=num_classes,
                                  input_shape=ImageClassificationConfig.INPUT_SHAPE)

    if gpu_num > 1:
        model = multi_gpu_model(model, gpus=gpu_num)

    return model


####################MULTI_LABEL_IMAGE_CLASSIFICATION_MODEL####################
def multi_label_classification_model(num_classes, gpu_num=1,
                                     learning_rate=0.0001):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding='same',
                     input_shape=MultiLabelClassificationConfig.INPUT_SHAPE))
    model.add(Activation('relu'))
    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Conv2D(64, (3, 3), padding='same'))
    model.add(Activation('relu'))
    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='sigmoid'))

    if gpu_num > 1:
        model = multi_gpu_model(model, gpus=gpu_num)

    return model


def multi_label_classification_model_2(num_classes, gpu_num=1,
                                       learning_rate=0.001):
    model = Sequential()
    model.add(Conv2D(32, (3, 3), padding="same",
                     input_shape=MultiLabelClassificationConfig.INPUT_SHAPE))
    model.add(Activation("relu"))
    model.add(BatchNormalization(axis=-1))
    model.add(MaxPooling2D(pool_size=(3, 3)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), padding="same"))
    model.add(Activation("relu"))
    model.add(BatchNormalization(axis=-1))
    model.add(Conv2D(64, (3, 3), padding="same"))
    model.add(Activation("relu"))
    model.add(BatchNormalization(axis=-1))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(1024))
    model.add(Activation("relu"))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))

    model.add(Dense(num_classes))
    model.add(Activation("sigmoid"))

    if gpu_num > 1:
        model = multi_gpu_model(model, gpus=gpu_num)

    return model


####################DEBLUR_GAN_MODELS####################
def generator_model():
    ngf = DeblurConfig.NGF
    n_blocks_gen = DeblurConfig.N_BLOCKS_GEN
    shape = DeblurConfig.CELL_SHAPE
    output_nc = DeblurConfig.OUTPUT_NC

    # Build generator architecture.
    # Current version : ResNet block
    inputs = Input(shape=shape)

    x = ReflectionPadding2D((3, 3))(inputs)
    x = Conv2D(filters=ngf, kernel_size=(7, 7), padding='valid')(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)

    n_downsampling = 2
    for i in range(n_downsampling):
        mult = 2 ** i
        x = Conv2D(filters=ngf * mult * 2, kernel_size=(3, 3),
                   strides=2, padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

    mult = 2 ** n_downsampling
    for i in range(n_blocks_gen):
        x = res_block(x, ngf * mult, use_dropout=True)

    for i in range(n_downsampling):
        mult = 2 ** (n_downsampling - i)
        # x = Conv2DTranspose(filters=int(ngf * mult / 2), kernel_size=(3, 3), strides=2, padding='same')(x)
        x = UpSampling2D()(x)
        x = Conv2D(filters=int(ngf * mult / 2),
                   kernel_size=(3, 3), padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

    x = ReflectionPadding2D((3, 3))(x)
    x = Conv2D(filters=output_nc, kernel_size=(7, 7), padding='valid')(x)
    x = Activation('tanh')(x)

    outputs = Add()([x, inputs])
    # outputs = Lambda(lambda z: K.clip(z, -1, 1))(x)
    outputs = Lambda(lambda z: z / 2)(outputs)

    model = Model(inputs=inputs, outputs=outputs, name='Generator')
    return model


def discriminator_model():
    ndf = DeblurConfig.NDF
    shape = DeblurConfig.CELL_SHAPE
    # Build discriminator architecture.
    n_layers, use_sigmoid = 3, False
    inputs = Input(shape=shape)

    x = Conv2D(filters=ndf, kernel_size=(4, 4),
               strides=2, padding='same')(inputs)
    x = LeakyReLU(0.2)(x)

    nf_mult, nf_mult_prev = 1, 1
    for n in range(n_layers):
        nf_mult_prev, nf_mult = nf_mult, min(2 ** n, 8)
        x = Conv2D(filters=ndf * nf_mult, kernel_size=(4, 4),
                   strides=2, padding='same')(x)
        x = BatchNormalization()(x)
        x = LeakyReLU(0.2)(x)

    nf_mult_prev, nf_mult = nf_mult, min(2 ** n_layers, 8)
    x = Conv2D(filters=ndf * nf_mult, kernel_size=(4, 4),
               strides=1, padding='same')(x)
    x = BatchNormalization()(x)
    x = LeakyReLU(0.2)(x)

    x = Conv2D(filters=1, kernel_size=(4, 4), strides=1, padding='same')(x)
    if use_sigmoid:
        x = Activation('sigmoid')(x)

    x = Flatten()(x)
    x = Dense(1024, activation='tanh')(x)
    x = Dense(1, activation='sigmoid')(x)

    model = Model(inputs=inputs, outputs=x, name='Discriminator')
    return model


def generator_containing_discriminator(generator, discriminator):
    image_shape = DeblurConfig.CELL_SHAPE
    inputs = Input(shape=image_shape)
    generated_image = generator(inputs)
    outputs = discriminator(generated_image)
    model = Model(inputs=inputs, outputs=outputs)
    return model


def generator_containing_discriminator_multiple_outputs(
        generator, discriminator):
    image_shape = DeblurConfig.CELL_SHAPE
    inputs = Input(shape=image_shape)
    generated_image = generator(inputs)
    outputs = discriminator(generated_image)
    model = Model(inputs=inputs, outputs=[generated_image, outputs])
    return model
