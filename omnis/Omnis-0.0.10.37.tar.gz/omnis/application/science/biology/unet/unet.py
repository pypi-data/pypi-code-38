import os
import cv2
import numpy as np
from keras.utils import Sequence
from keras.optimizers import Adam
from .model import unet
from .....lib.general_lib import get_data_path_type
from ....application import Application


class Unet(Application):
    def __init__(self, weights_path=None):
        super().__init__()

        self.model = self.create_model()

        if weights_path is not None:
            self.load(weights_path)

    def train(self, data_path, epochs, learning_rate=1e-4, batch_size=1):
        data_gen = TrainGenerator()
        data_generator = data_gen.flow_from_directory(data_path,
                                                      image_shape=(512, 512),
                                                      batch_size=batch_size)

        self.compile_model(learning_rate)

        self.model.fit_generator(data_generator,
                                 steps_per_epoch=len(data_generator),
                                 epochs=epochs)

    def predict(self, data_path, batch_size=1, result_folder='results'):
        if not os.path.isdir(result_folder):
            os.makedirs(result_folder)

        data_type = get_data_path_type(data_path)
        if data_type == 'image':
            filename = os.path.basename(data_path)
            img = load_image_with_proper_format(data_path, (512, 512))
            img = np.reshape(img, (1,) + img.shape)
            result = self.model.predict(img)
            result = result * 255
            cv2.imwrite(os.path.join(result_folder, filename), result[0])
        elif data_type == 'directory':
            saved_folder = os.path.join(result_folder, data_path)
            if not os.path.isdir(saved_folder):
                os.makedirs(saved_folder)

            data_gen = PredictGenerator()
            data_generator = data_gen.flow_from_directory(data_path,
                                                          image_shape=(
                                                              512, 512),
                                                          batch_size=batch_size)
            results = self.model.predict_generator(data_generator,
                                                   steps=len(data_generator))
            for i, result in enumerate(results):
                filename = data_generator.predict_order_filenames[i]
                saved_path = os.path.join(saved_folder, filename)
                result = result * 255
                cv2.imwrite(saved_path, result)

    def save(self, weights_path):
        self.model.save_weights(weights_path)

    def load(self, weights_path):
        self.model.load_weights(weights_path)

    def create_model(self):
        return unet()

    def compile_model(self, learning_rate):
        self.model.compile(optimizer=Adam(lr=learning_rate),
                           loss='binary_crossentropy',
                           metrics=['accuracy'])


def load_image_with_proper_format(image_path, image_shape):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = img / 255
    img = cv2.resize(img, image_shape)
    img = np.reshape(img, img.shape + (1,))
    return img


class TrainGenerator(Sequence):
    def __init__(self, image_filenames=None, mask_filenames=None,
                 image_shape=None):
        self.image_filenames = image_filenames
        self.mask_filenames = mask_filenames
        self.image_shape = image_shape
        self.batch_size = 1

    def __len__(self):
        return int(np.ceil(len(self.image_filenames) / float(self.batch_size)))

    def __getitem__(self, idx):
        images_names = self.image_filenames[
            idx * self.batch_size:(idx + 1) * self.batch_size]
        masks_names = self.mask_filenames[
            idx * self.batch_size:(idx + 1) * self.batch_size]

        images = []
        masks = []
        for image_name in images_names:
            try:
                img = load_image_with_proper_format(image_name,
                                                    self.image_shape)
                images.append(img)
            except BaseException:
                pass
        for mask_name in masks_names:
            try:
                mask = load_image_with_proper_format(mask_name,
                                                     self.image_shape)
                masks.append(mask)
            except BaseException:
                pass

        return np.array(images), np.array(masks)

    def flow_from_directory(self, data_path, image_shape, batch_size=1):
        image_folder_path = os.path.join(data_path, 'image')
        mask_folder_path = os.path.join(data_path, 'mask')

        images = os.listdir(image_folder_path)
        masks = os.listdir(mask_folder_path)

        self.image_filenames = [
            f'{image_folder_path}/{image}' for image in images
        ]
        self.mask_filenames = [
            f'{mask_folder_path}/{mask}' for mask in masks
        ]
        self.batch_size = batch_size
        self.image_shape = image_shape

        return self


class PredictGenerator(Sequence):
    def __init__(self, image_filenames=None, image_shape=None):
        self.image_filenames = image_filenames
        self.image_shape = image_shape
        self.batch_size = 1
        self.predict_order_filenames = []

    def __len__(self):
        return int(np.ceil(len(self.image_filenames) / float(self.batch_size)))

    def __getitem__(self, idx):
        images_names = self.image_filenames[
            idx * self.batch_size:(idx + 1) * self.batch_size]

        images = []
        for image_name in images_names:
            try:
                _, only_file_name = os.path.split(image_name)
                image = load_image_with_proper_format(image_name,
                                                      self.image_shape)
                images.append(image)
                self.predict_order_filenames.append(only_file_name)
            except BaseException:
                pass

        return np.array(images)

    def flow_from_directory(self, data_path, image_shape, batch_size=1):
        images = os.listdir(data_path)

        self.image_filenames = [
            f'{data_path}/{image}' for image in images
        ]
        self.batch_size = batch_size
        self.image_shape = image_shape

        return self
