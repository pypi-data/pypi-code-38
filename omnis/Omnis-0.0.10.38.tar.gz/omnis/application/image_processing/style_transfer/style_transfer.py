import os
import time

import cv2
import keras
from keras import backend as K
from keras.preprocessing.image import img_to_array, load_img
import numpy as np
from scipy.optimize import fmin_l_bfgs_b
import skimage

from ...application import Application


class StyleTransfer(Application):
    def __init__(self):
        super().__init__()

        self.loss_value = None
        self.grad_values = None
        self.get_content_image_from = None
        self.get_style_image_as = None
        self.content_image_path = None
        self.style_image_path = None
        self.content_image_array = None
        self.style_image_array = None

    def prepare_train_data(
            self,
            get_content_image_from='directory',
            content_image_path=None,
            content_image_array=None,
            get_style_image_as='filepath',
            style_image_path=None,
            style_image_array=None):
        assert get_content_image_from in ["directory", "argument"], \
            "get_content_image_from should be either 'directory' or 'argument'."
        assert get_style_image_as in ["filepath", "ndarray"], \
            "get_style_image_as should be either 'filepath' or 'ndarray'."

        self.get_content_image_from = get_content_image_from
        self.get_style_image_as = get_style_image_as
        self.content_image_path = content_image_path
        self.style_image_path = style_image_path
        self.content_image_array = content_image_array
        self.style_image_array = style_image_array

    def generate(
            self,
            iterations=10,
            output_type="file",
            output_path="result",
            total_variation_weight=1.0,
            style_weight=1.0,
            content_weight=0.025):
        self.total_variation_weight = total_variation_weight
        self.style_weight = style_weight
        self.content_weight = content_weight
        if self.get_style_image_as == 'filepath':
            try:
                load_img(self.style_image_path)
                style_image = self.style_image_path
            except Exception as e:
                raise e
        else:
            if self.style_image_array.ndim == 3:
                style_image_array = np.array([self.style_image_array])
            elif self.style_image_array.ndim < 4:
                raise ValueError("style_image_array.ndim is less than 3")
            style_image = style_image_array

        if self.get_content_image_from == "directory":
            if not os.path.isdir(self.content_image_path):
                raise FileNotFoundError(
                    self.content_image_path + " is not an existing directory.")
            parent = os.listdir(self.content_image_path)
        else:
            if self.content_image_array.ndim == 3:
                content_image_array = np.array([self.content_image_array])
            elif self.content_image_array.ndim < 4:
                raise ValueError("content_image_array.ndim is less than 3")
            parent = content_image_array

        assert output_type in ["file", "array"], \
            "output_type should be either 'file' or 'array'."

        self.result = None
        for child in parent:
            self.generate_one_image(self.content_image_path, child, style_image,
                                    iterations, output_type, output_path)

        if output_type == 'array':
            return self.result
        else:
            return

    def generate_one_image(self, content_image_path, child, style_image,
                           iterations, output_type, output_path):
        # dimensions of the generated picture.
        if self.get_content_image_from == 'directory':
            width, height = load_img(content_image_path + "/" + child).size
        elif self.get_content_image_from == 'argument':
            if K.image_data_format() == 'channels_last':
                width = child[0]
                height = child[1]
            else:
                width = child[1]
                height = child[2]
        img_nrows = 400
        img_ncols = int(width * img_nrows / height)

        x, model = self.create_model(img_nrows, img_ncols, content_image_path,
                                     child, style_image)

        loss = self.make_loss(model, img_nrows, img_ncols)

        self.set_f_outputs(loss)

        # run scipy-based optimization (L-BFGS) over the pixels of the generated image
        # so as to minimize the neural style loss
        for i in range(iterations):
            print('Start of iteration', i)
            start_time = time.time()
            x, min_val, _ = fmin_l_bfgs_b(self.loss, x.flatten(),
                                          args=(img_nrows, img_ncols),
                                          fprime=self.grads, maxfun=20)
            print('Current loss value:', min_val)
            end_time = time.time()
            print('Iteration %d completed in %ds' % (i, end_time - start_time))

        img = self.deprocess_image(x.copy(), img_nrows, img_ncols)
        if output_type == 'array':
            if self.result is None:
                img = cv2.resize(img, (224, 224))
                self.result = np.array([img])
            else:
                img = cv2.resize(img, (224, 224))
                img = np.array([img])
                self.result = np.concatenate((self.result, img))
        elif output_type == 'file':
            # save current generated image
            fname = os.getcwd() + "/" + output_path + "/" + child
            if not os.path.exists(os.path.dirname(fname)):
                os.makedirs(os.path.dirname(fname))
            skimage.io.imsave(fname, img)
            print('Image saved as', fname)

    def create_model(self, img_nrows, img_ncols, content_image_path, child,
                     style_image):
        model_type = keras.applications.vgg19

        # get tensor representations of our images
        if self.get_content_image_from == 'directory':
            x = self.preprocess_image(content_image_path + "/" + child,
                                      img_nrows, img_ncols, model_type)
        elif self.get_content_image_from == 'argument':
            x = self.preprocess_image(child, img_nrows, img_ncols, model_type)
        content_image = K.variable(x)
        style_image_tensor = K.variable(
            self.preprocess_image(style_image, img_nrows, img_ncols,
                                  model_type))

        # this will contain our generated image
        if K.image_data_format() == 'channels_first':
            self.combination_image = K.placeholder((1, 3, img_nrows, img_ncols))
        else:
            self.combination_image = K.placeholder((1, img_nrows, img_ncols, 3))

        # combine the 3 images into a single Keras tensor
        input_tensor = K.concatenate(
            [content_image, style_image_tensor, self.combination_image], axis=0)

        # build the VGG16 network with our 3 images as input
        # the model will be loaded with pre-trained ImageNet weights
        model = keras.applications.vgg19.VGG19(input_tensor=input_tensor,
                                               weights='imagenet',
                                               include_top=False)
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
            a = K.square(
                x[:, :, :img_nrows - 1, :img_ncols - 1]
                - x[:, :, 1:, :img_ncols - 1]
            )
            b = K.square(
                x[:, :, :img_nrows - 1, :img_ncols - 1]
                - x[:, :, :img_nrows - 1, 1:]
            )
        else:
            a = K.square(
                x[:, :img_nrows - 1, :img_ncols - 1, :]
                - x[:, 1:, :img_ncols - 1, :]
            )
            b = K.square(
                x[:, :img_nrows - 1, :img_ncols - 1, :]
                - x[:, :img_nrows - 1, 1:, :]
            )
        return K.sum(K.pow(a + b, 1.25))

    def make_loss(self, model, img_nrows, img_ncols):
        """
        get the symbolic outputs of each "key" layer
        (we gave them unique names).
        """
        outputs_dict = {layer.name: layer.output for layer in model.layers}

        # combine these loss functions into a single scalar
        loss = K.variable(0.)
        layer_features = outputs_dict['block5_conv2']
        content_image_features = layer_features[0, :, :, :]
        combination_features = layer_features[2, :, :, :]
        loss += self.content_weight * self.content_loss(content_image_features,
                                                        combination_features)

        feature_layers = ['block1_conv1', 'block2_conv1', 'block3_conv1',
                          'block4_conv1', 'block5_conv1']
        for layer_name in feature_layers:
            layer_features = outputs_dict[layer_name]
            style_reference_features = layer_features[1, :, :, :]
            combination_features = layer_features[2, :, :, :]
            sl = self.style_loss(style_reference_features, combination_features,
                                 img_nrows, img_ncols)
            loss += (self.style_weight / len(feature_layers)) * sl
        loss += self.total_variation_weight * self.total_variation_loss(
            self.combination_image, img_nrows, img_ncols)
        return loss

    def loss(self, x, img_nrows, img_ncols):
        assert self.loss_value is None
        loss_value, grad_values = self.eval_loss_and_grads(x, img_nrows,
                                                           img_ncols)
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
