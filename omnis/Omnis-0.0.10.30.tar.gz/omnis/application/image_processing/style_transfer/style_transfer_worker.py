from keras import backend as K
import keras

from keras.preprocessing.image import load_img, img_to_array
from multiprocessing import Queue, Process
import cv2
import numpy as np
import os
import time
import skimage

from scipy.optimize import fmin_l_bfgs_b
import skimage
import cv2

import json
from collections import OrderedDict


class Style_Transfer_Worker(Process):
    def __init__(
            self,
            gpuid,
            queue,
            get_content_image_from,
            get_style_image_as,
            content_image_path=None,
            style_image_path=None,
            content_image_array=None,
            style_image_array=None,
            content_weight=0.025,
            use_deepblock_log=False):
        Process.__init__(self, name='ModelProcessor')
        self._gpuid = gpuid
        self._queue = queue

        self._get_content_image_from = get_content_image_from
        self._get_style_image_as = get_style_image_as
        self._style_image = style_image_path
        self.loss_value = None
        self.deepblock_log = use_deepblock_log

    def run(self):
        # set enviornment
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVICES"] = str(self._gpuid)

        while True:
            xfile = self._queue.get()
            if xfile is None:
                self._queue.put(None)
                break
            templist = os.path.split(xfile)
            directory_path = templist[0]
            child = templist[1]
            self.generate_one_image(directory_path=directory_path, child=child)

    def generate_one_image(self, directory_path, child):
        # dimensions of the generated picture.
        if self._get_content_image_from == 'directory':
            width, height = load_img(os.path.join(directory_path, child)).size
        elif self._get_content_image_from == 'argument':
            if K.image_data_format() == 'channels_last':
                width = child[0]
                height = child[1]
            else:
                width = child[1]
                height = child[2]
        img_nrows = 400
        img_ncols = int(width * img_nrows / height)

        x, model = self.create_model(
            img_nrows, img_ncols, directory_path, child)

        loss = self.make_loss(model, img_nrows, img_ncols)

        self.set_f_outputs(loss)

        # run scipy-based optimization (L-BFGS) over the pixels of the generated image
        # so as to minimize the neural style loss
        for i in range(self.iterations):
            logJson = OrderedDict()
            logJson['logType'] = "iterate"
            logJson['iterateNum'] = i
            logJson['filename'] = child
            start_time = time.time()
            x, min_val, info = fmin_l_bfgs_b(self.loss, x.flatten(), args=(
                img_nrows, img_ncols), fprime=self.grads, maxfun=20)
            end_time = time.time()
            if self.deepblock_log:
                print(json.dumps(logJson, ensure_ascii=False))

        img = self.deprocess_image(x.copy(), img_nrows, img_ncols)
        if self.output_type == 'array':
            if isinstance(self.result, type(None)):
                img = cv2.resize(img, (224, 224))
                self.result = np.array([img])
                create_result = False
            else:
                img = cv2.resize(img, (224, 224))
                img = np.array([img])
                self.result = np.concatenate((self.result, img))
        elif self.output_type == 'file':
            # save current generated image
            fname = os.path.join(os.getcwd(), self.output_path, child)
            if not os.path.exists(os.path.dirname(fname)):
                os.makedirs(os.path.dirname(fname))
            skimage.io.imsave(fname, img)
            logJson = OrderedDict()
            logJson['logType'] = "fileGenerated"
            logJson['filename'] = child
            if self.deepblock_log:
                print(json.dumps(logJson, ensure_ascii=False))

    def create_model(self, img_nrows, img_ncols, content_image_path, child):
        model_type = keras.applications.vgg19

        # get tensor representations of our images
        if self._get_content_image_from == 'directory':
            x = self.preprocess_image(os.path.join(
                content_image_path, child), img_nrows, img_ncols, model_type)
        elif self._get_content_image_from == 'argument':
            x = self.preprocess_image(child, img_nrows, img_ncols, model_type)
        content_image = K.variable(x)
        style_image_tensor = K.variable(self.preprocess_image(
            self._style_image, img_nrows, img_ncols, model_type))

        # this will contain our generated image
        if K.image_data_format() == 'channels_first':
            self.combination_image = K.placeholder(
                (1, 3, img_nrows, img_ncols))
        else:
            self.combination_image = K.placeholder(
                (1, img_nrows, img_ncols, 3))

        # combine the 3 images into a single Keras tensor
        input_tensor = K.concatenate(
            [content_image, style_image_tensor, self.combination_image], axis=0)

        # build the VGG16 network with our 3 images as input
        # the model will be loaded with pre-trained ImageNet weights
        model = keras.applications.vgg19.VGG19(
            input_tensor=input_tensor, weights='imagenet', include_top=False)
        print('Model loaded.')

        return x, model

    def set_f_outputs(self, loss):
        # get the gradients of the generated image wrt the loss
        grads = K.gradients(loss, self.combination_image)

        outputs = [loss]
        if isinstance(grads, (list, tuple)):
            outputs += grads
        else:
            outputs.append(grads)

        self.f_outputs = K.function([self.combination_image], outputs)

    def preprocess_image(self, image_path, img_nrows, img_ncols, model_type):
        if not isinstance(image_path, np.ndarray):
            img = load_img(image_path, target_size=(img_nrows, img_ncols))
            img = img_to_array(img)
            img = np.expand_dims(img, axis=0)
        img = model_type.preprocess_input(img)
        return img

    def deprocess_image(self, x, img_nrows, img_ncols):
        if K.image_data_format() == 'channels_first':
            x = x.reshape((3, img_nrows, img_ncols))
            x = x.transpose((1, 2, 0))
        else:
            x = x.reshape((img_nrows, img_ncols, 3))
        # Remove zero-center by mean pixel
        x[:, :, 0] += 103.939
        x[:, :, 1] += 116.779
        x[:, :, 2] += 123.68
        # 'BGR'->'RGB'
        x = x[:, :, ::-1]
        x = np.clip(x, 0, 255).astype('uint8')
        return x

    # the gram matrix of an image tensor (feature-wise outer product)
    def gram_matrix(self, x):
        assert K.ndim(x) == 3
        if K.image_data_format() == 'channels_first':
            features = K.batch_flatten(x)
        else:
            features = K.batch_flatten(K.permute_dimensions(x, (2, 0, 1)))
        gram = K.dot(features, K.transpose(features))
        return gram

    # an auxiliary loss function
    # designed to maintain the "content" of the
    # content image in the generated image
    def content_loss(self, base, combination):
        return K.sum(K.square(combination - base))

    # the "style loss" is designed to maintain
    # the style of the style image in the generated image.
    # It is based on the gram matrices (which capture style) of
    # feature maps from the style style image
    # and from the generated image
    def style_loss(self, style, combination, img_nrows, img_ncols):
        assert K.ndim(style) == 3
        assert K.ndim(combination) == 3
        S = self.gram_matrix(style)
        C = self.gram_matrix(combination)
        channels = 3
        size = img_nrows * img_ncols
        return K.sum(K.square(S - C)) / (4. * (channels ** 2) * (size ** 2))

    # the 3rd loss function, total variation loss,
    # designed to keep the generated image locally coherent
    def total_variation_loss(self, x, img_nrows, img_ncols):
        assert K.ndim(x) == 4
        if K.image_data_format() == 'channels_first':
            a = K.square(x[:, :, :img_nrows - 1, :img_ncols -
                           1] - x[:, :, 1:, :img_ncols - 1])
            b = K.square(x[:, :, :img_nrows - 1, :img_ncols -
                           1] - x[:, :, :img_nrows - 1, 1:])
        else:
            a = K.square(x[:, :img_nrows - 1, :img_ncols -
                           1, :] - x[:, 1:, :img_ncols - 1, :])
            b = K.square(x[:, :img_nrows - 1, :img_ncols -
                           1, :] - x[:, :img_nrows - 1, 1:, :])
        return K.sum(K.pow(a + b, 1.25))

    def make_loss(self, model, img_nrows, img_ncols):
        # get the symbolic outputs of each "key" layer (we gave them unique
        # names).
        outputs_dict = dict([(layer.name, layer.output)
                             for layer in model.layers])

        # combine these loss functions into a single scalar
        loss = K.variable(0.)
        layer_features = outputs_dict['block5_conv2']
        content_image_features = layer_features[0, :, :, :]
        combination_features = layer_features[2, :, :, :]
        loss += self.content_weight * \
            self.content_loss(content_image_features, combination_features)

        feature_layers = ['block1_conv1', 'block2_conv1',
                          'block3_conv1', 'block4_conv1', 'block5_conv1']
        for layer_name in feature_layers:
            layer_features = outputs_dict[layer_name]
            style_reference_features = layer_features[1, :, :, :]
            combination_features = layer_features[2, :, :, :]
            sl = self.style_loss(style_reference_features,
                                 combination_features, img_nrows, img_ncols)
            loss += (self.style_weight / len(feature_layers)) * sl
        loss += self.total_variation_weight * \
            self.total_variation_loss(
                self.combination_image, img_nrows, img_ncols)
        return loss

    def loss(self, x, img_nrows, img_ncols):
        assert self.loss_value is None
        loss_value, grad_values = self.eval_loss_and_grads(
            x, img_nrows, img_ncols)
        self.loss_value = loss_value
        self.grad_values = grad_values
        return self.loss_value

    def grads(self, x, img_nrows, img_ncols):
        assert self.loss_value is not None
        grad_values = np.copy(self.grad_values)
        self.loss_value = None
        self.grad_values = None
        return grad_values

    def eval_loss_and_grads(self, x, img_nrows, img_ncols):
        if K.image_data_format() == 'channels_first':
            x = x.reshape((1, 3, img_nrows, img_ncols))
        else:
            x = x.reshape((1, img_nrows, img_ncols, 3))
        outs = self.f_outputs([x])
        loss_value = outs[0]
        if len(outs[1:]) == 1:
            grad_values = outs[1].flatten().astype('float64')
        else:
            grad_values = np.array(outs[1:]).flatten().astype('float64')
        return loss_value, grad_values
