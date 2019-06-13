from __future__ import division
from __future__ import print_function

import keras

from keras.models import Sequential
from keras.preprocessing.image import ImageDataGenerator
from keras import regularizers, optimizers
import numpy as np
import csv
import json
import os
from math import ceil
from collections import OrderedDict
import pandas as pd

from ....lib.model_lib import multi_label_classification_model_2
from ....lib.config_lib import MultiLabelClassificationConfig
from ....lib.generators import PredictGenerator
from ....lib.general_lib import get_n_largest_index_and_probs, get_data_path_type
from ....lib.saving_lib import save_models_with_class_indices, load_models_with_class_indices
from ....lib.image_lib import reshape_data

from ...application import Application


class Multi_Label_Image_Classification(Application):
    def __init__(self, model_path=None):
        super().__init__()

        if not isinstance(model_path, type(None)):
            self.load(model_path)

    def train(self,
            annotation_path=None,
            image_directory_path="",
            validation_data_proportion = 0.1,
            batch_size = 32,
            epochs = 1):        
        class_list, data_num = self.get_dataset_info(annotation_path = annotation_path)

        train_generator, valid_generator = self.make_train_valid_generator(annotation_path=annotation_path,
                                                                        image_directory_path=image_directory_path,
                                                                        batch_size=batch_size,
                                                                        class_list=class_list,
                                                                        validation_data_proportion=validation_data_proportion,
                                                                        data_num = data_num)

        self.model = self.create_and_compile_model(class_list = class_list)

        steps_train = ceil(train_generator.n / train_generator.batch_size)
        steps_valid = ceil(valid_generator.n / valid_generator.batch_size)

        self.model.fit_generator(generator = train_generator,
                            steps_per_epoch = steps_train,
                            validation_data = valid_generator,
                            validation_steps = steps_valid,
                            epochs = epochs)

    def save(self, model_path):
        save_models_with_class_indices(self.model, model_path)
        

    def load(self, model_path):
        self.model = load_models_with_class_indices(model_path)


    def predict(self, 
            data_path,
            verbose = 0,
            batch_size = 32,
            top_n = 3):
        
        data_path_type = get_data_path_type(data_path)
        if data_path_type == "directory":
            pred_datagen = PredictGenerator()
            pred_generator = pred_datagen.flow_one_directory(
                directory_path = data_path,
                shuffle = False,
                image_shape=MultiLabelClassificationConfig.INPUT_SHAPE[0:2],
                batch_size=batch_size
            )

            steps_pred = ceil(len(pred_generator.image_filenames) / pred_generator.batch_size)
            probs = self.model.predict_generator(pred_generator,
                                            steps = steps_pred,
                                            verbose = 1)

            predicted_classes_top_n, probs_top_n = get_n_largest_index_and_probs(probs, top_n)
            predicted_order_filenames = pred_generator.predict_order_filenames

            pair_dict = OrderedDict()
            for i in range(len(predicted_classes_top_n)):
                result_dict = OrderedDict()
                for j in range(0, top_n):
                    result_dict[self.model.class_indices[str(predicted_classes_top_n[i]
                                                    [j])]] = probs_top_n[i][j]
                pair_dict[predicted_order_filenames[i]] = result_dict
            return json.dumps(pair_dict, ensure_ascii=False)
        elif data_path_type == 'image':
            _, only_file_name = os.path.split(data_path)
            img_to_predict = cv2.imread(data_path)
            img_array = np.expand_dims(img_to_predict, axis=0)
            reshaped_array = reshape_data(data_array = img_array,
                                        input_shape = self.model.input_shape)
            probs = self.model.predict(reshaped_array, batch_size=batch_size, verbose=verbose, steps=steps)
            predicted_classes_top_n, probs_top_n = get_n_largest_index_and_probs(probs, top_n)

            result_dict = OrderedDict()
            for j in range(0, top_n):
                result_dict[self.model.class_indices[str(predicted_classes_top_n[0][j])]] = probs_top_n[0][j]
            pair_dict[only_file_name] = result_dict

            return json.dumps(pair_dict, ensure_ascii=False)


    def make_train_valid_generator(self,
                                annotation_path,
                                image_directory_path, 
                                batch_size,
                                class_list,
                                validation_data_proportion,
                                data_num):
        dataframe = pd.read_csv(annotation_path)

        class_list, dataframe = self.get_class_list_and_data_frame_from_csv(annotation_path)
        datagen = ImageDataGenerator(rescale = 1./255.)
        valid_datagen = ImageDataGenerator(rescale= 1./255.)

        train_data_num = (int) (data_num*(1-validation_data_proportion))

        train_generator = datagen.flow_from_dataframe(
            dataframe = dataframe[:train_data_num],
            directory = image_directory_path,
            x_col = "Filenames",
            y_col = class_list,
            class_mode = "other",
            target_size =MultiLabelClassificationConfig.INPUT_SHAPE[0:2],
            batch_size = batch_size
        )

        valid_generator = valid_datagen.flow_from_dataframe(
            dataframe = dataframe[train_data_num:],
            directory = image_directory_path,
            x_col = "Filenames",
            y_col = class_list,
            class_mode = "other",
            target_size =MultiLabelClassificationConfig.INPUT_SHAPE[0:2],
            batch_size = batch_size
        )

        return train_generator, valid_generator

    def create_and_compile_model(self, class_list):
        model = multi_label_classification_model_2(len(class_list), gpu_num = self.gpu_num)
        model.compile(optimizers.rmsprop(lr=0.001, decay=1e-6),loss="binary_crossentropy",metrics=["accuracy"])
        model.class_indices = {}
        for i in range(len(class_list)):
            model.class_indices[str(i)] = class_list[i]

        return model

        
    def get_dataset_info(self, annotation_path):
        class_list = []
        num_data = 0
        f = open(annotation_path, 'r', encoding='utf-8')

        csv_reader = csv.reader(f)
        class_row = next(csv_reader)

        for class_name in class_row:
            if class_name != "Filenames":
                class_list.append(class_name)
        
        for line in csv_reader:
            num_data += 1
            
        return class_list, num_data

            
    def get_class_list_and_data_frame_from_csv(self, csv_file_path):
        class_list = []
        dataframe = []
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            class_row = next(csv_reader)

            for class_name in class_row:
                class_list.append(class_name)

            for line in csv_reader:
                probs_list = line[1:]
                dataframe.append(probs_list)

        dataframe = np.array(dataframe)
        return class_list, dataframe
            
            

