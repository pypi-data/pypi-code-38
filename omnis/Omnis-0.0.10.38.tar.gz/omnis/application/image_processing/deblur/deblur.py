import json
import os
from collections import OrderedDict

import cv2
import numpy as np
from keras.optimizers import Adam

from ...application import Application
from ....lib.config_lib import DeblurConfig, DeepblockLogConfig
from ....lib.general_lib import get_data_path_type
from ....lib.image_lib import (
    get_image_names_in_directory, merge_image, save_image, split_one_image,
)
from ....lib.loss_lib import perceptual_loss, wasserstein_loss
from ....lib.model_lib import (
    discriminator_model, generator_containing_discriminator_multiple_outputs,
    generator_model,
)


class Deblur_GAN(Application):
    def __init__(self, g_model_path=None, d_model_path=None):
        super().__init__()

        if not isinstance(g_model_path, type(None)):
            if not isinstance(d_model_path, type(None)):
                self.create_model()
                self.load(g_model_path=g_model_path, d_model_path=d_model_path)
            else:
                self.create_model()
                self.load_g_model(model_path=g_model_path)

    def train(self,
              data_path,
              epochs=1,
              batch_size=32,
              learning_rate=1E-4,
              metrics='accuracy'):
        if not isinstance(metrics, list):
            metrics = [metrics]

        blur_data_path = os.path.join(data_path, 'blur')
        sharp_data_path = os.path.join(data_path, 'sharp')

        blur_array = self.load_image_array(blur_data_path)
        sharp_array = self.load_image_array(sharp_data_path)

        self.create_and_compile_model(learning_rate=learning_rate)

        self._fit_gan(blur_array=blur_array,
                      sharp_array=sharp_array,
                      batch_size=batch_size,
                      epochs=epochs)

    def predict(self, data_path, batch_size=1,
                result_path=DeblurConfig.RESULT_FOLDER):
        image_data = self.load_predict_images_data(data_path)
        image_array = image_data['images']
        image_paths_list = image_data['images_paths']
        image_area_index = image_data['images_area_index']

        generated_images = self.g_model.predict(
            x=image_array, batch_size=batch_size)
        generated_images_array = np.array(
            [self.deprocess_image(img) for img in generated_images])

        image_list = []
        for i in range(generated_images.shape[0]):
            img = generated_images_array[i, :, :, :]
            image_list.append(img)

        now_image_path = image_paths_list[0]
        merge_image_list = []
        merge_image_area_list = []
        for i, image in enumerate(image_paths_list):
            if image != now_image_path:
                merged_image = merge_image(
                    merge_image_list, merge_image_area_list)
                self.save_merged_image(
                    merged_image, result_path, now_image_path)
                now_image_path = image
                merge_image_list = []
                merge_image_area_list = []
            merge_image_list.append(image_list[i])
            merge_image_area_list.append(image_area_index[i])

            if i == len(image_paths_list) - 1:
                merged_image = merge_image(
                    merge_image_list, merge_image_area_list)
                self.save_merged_image(
                    merged_image, result_path, now_image_path)

    def save(self, g_model_path, d_model_path):
        try:
            self.save_g_model(g_model_path)
            self.save_d_model(d_model_path)
        except Exception as e:
            raise e

    def load(self, g_model_path, d_model_path):
        try:
            self.load_g_model(g_model_path)
            self.load_d_model(d_model_path)
        except Exception as e:
            raise e

    def _fit_gan(self,
                 blur_array,
                 sharp_array,
                 batch_size,
                 epochs,
                 critic_updates=5):
        output_true_batch = np.ones((batch_size, 1))
        output_false_batch = -np.ones((batch_size, 1))

        for epoch in range(0, epochs):
            permutated_indexes = np.random.permutation(
                blur_array.shape[0])

            d_losses = []
            d_on_g_losses = []
            for index in range(int(blur_array.shape[0] / batch_size)):
                batch_indexes = permutated_indexes[
                    index * batch_size
                    :(index + 1) * batch_size
                ]
                image_blur_batch = blur_array[batch_indexes]
                image_full_batch = sharp_array[batch_indexes]

                generated_images = self.g_model.predict(
                    x=image_blur_batch, batch_size=batch_size)

                for _ in range(critic_updates):
                    d_loss_real = self.d_model.train_on_batch(
                        image_full_batch, output_true_batch)
                    d_loss_fake = self.d_model.train_on_batch(
                        generated_images, output_false_batch)
                    d_loss = 0.5 * np.add(d_loss_fake, d_loss_real)
                    d_losses.append(d_loss)

                self.d_model.trainable = False

                d_on_g_loss = self.d_on_g.train_on_batch(
                    image_blur_batch, [image_full_batch, output_true_batch])
                d_on_g_losses.append(d_on_g_loss)

                self.d_model.trainable = True

            if self.deepblock_log:
                log_json = OrderedDict()
                log_json[DeepblockLogConfig.LOG_TYPE] = "epochend"
                log_json['totalEpoch'] = epochs
                log_json['nowEpoch'] = epoch
                log_json['d_loss'] = str(np.mean(d_losses))
                log_json['d_on_g_loss'] = str(np.mean(d_on_g_losses))
                print(json.dumps(log_json, ensure_ascii=False))

    def create_and_compile_model(self,
                                 learning_rate):
        self.create_model()

        d_opt = Adam(lr=learning_rate, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
        d_on_g_opt = Adam(lr=learning_rate, beta_1=0.9, beta_2=0.999,
                          epsilon=1e-08)

        self.d_model.trainable = True
        self.d_model.compile(optimizer=d_opt,
                             loss=wasserstein_loss)
        self.d_model.trainable = False

        self.d_on_g.compile(d_on_g_opt,
                            loss=[perceptual_loss, wasserstein_loss],
                            loss_weights=[100, 1])
        self.d_model.trainable = False

    def create_model(self):
        self.g_model = self.create_g_model()
        self.d_model = self.create_d_model()
        self.d_on_g = generator_containing_discriminator_multiple_outputs(
            self.g_model, self.d_model)

    def create_g_model(self):
        g_model = generator_model()
        return g_model

    def create_d_model(self):
        d_model = discriminator_model()
        return d_model

    def load_g_model(self, model_path):
        self.g_model.load_weights(model_path)

    def load_d_model(self, model_path):
        self.d_model.load_weights(model_path)

    def save_g_model(self, model_path):
        self.g_model.save_weights(model_path)

    def save_d_model(self, model_path):
        self.d_model.save_weights(model_path)

    def save_merged_image(self, image, result_path, image_path):
        if not os.path.exists(result_path):
            os.makedirs(result_path)

        save_image(image, os.path.join(result_path, image_path))
        if self.deepblock_log:
            log_json = OrderedDict()
            log_json[DeepblockLogConfig.LOG_TYPE] = "fileGenerated"
            log_json['filename'] = image_path
            print(json.dumps(log_json, ensure_ascii=False))

    def load_image_array(self, data_path):
        data_path_type = get_data_path_type(data_path)

        if data_path_type == "image":
            all_image_paths = [data_path]
        elif data_path_type == "directory":
            all_image_paths = get_image_names_in_directory(data_path)
        else:
            raise ValueError("path should be image file or directory")

        images_all = []
        for path_image in all_image_paths:
            img = cv2.imread(path_image, cv2.IMREAD_COLOR)
            images_all.append(self.preprocess_image(img))

        return np.array(images_all)

    def load_predict_images_data(self, path):
        if os.path.isfile(path):
            all_image_paths = [path]
        elif os.path.isdir(path):
            all_image_paths = get_image_names_in_directory(path)
        else:
            raise ValueError("path should be file or directory")

        images_all = []
        images_all_paths = []
        images_all_area_index = []
        for path_image in all_image_paths:
            img = cv2.imread(path_image, cv2.IMREAD_COLOR)
            split_images, area_index = split_one_image(
                img, DeblurConfig.CELL_SHAPE[0], DeblurConfig.CELL_SHAPE[1])
            for i, image in enumerate(split_images):
                images_all.append(self.preprocess_image(image))
                images_all_paths.append(path_image)
                images_all_area_index.append(area_index[i])

        return {
            'images': np.array(images_all),
            'images_paths': images_all_paths,
            'images_area_index': images_all_area_index
        }

    def preprocess_image(self, img):
        resized_img = cv2.resize(img, DeblurConfig.CELL_SHAPE[:2])
        processed_img = (resized_img - 127.5) / 127.5
        return processed_img

    def deprocess_image(self, img):
        img = img * 127.5 + 127.5
        return img.astype('uint8')
