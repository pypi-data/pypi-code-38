# -*- coding: utf-8 -*-
"""
Class definition of YOLO_v3 style detection model on image and video
"""

from keras import backend as K
from keras.models import load_model, Model
from keras.layers import Input, Lambda
from keras.utils import multi_gpu_model
from keras.optimizers import Adam
from PIL import Image, ImageDraw
from timeit import default_timer as timer
import numpy as np
import cv2
import os

from ....lib.yolo_v3.model import yolo_eval, yolo_body, yolo_loss, preprocess_true_boxes, yolo_head
from ....lib.yolo_v3.utils import letterbox_image, get_random_data
from ....lib.config_lib import ObjectDetectionConfig
from ....lib.saving_lib import save_models_with_class_indices, load_models_with_class_indices
from ....lib.general_lib import get_data_path_type

from ...application import Application

class Object_Detection(Application):
    def __init__(self, weights_path = None, classes_path = None, model_type = 'yolo'):
        Application.__init__(self)

        self.model_type = model_type

        if not isinstance(weights_path, type(None)) and not isinstance(classes_path, type(None)):
            self.load(weights_path, classes_path)


    def train(self,
            data_path,
            classes_path,
            epochs = 50,
            batch_size = 32,
            learning_rate = 1e-3,
            validation_proportion = 0.1):

        self.class_names = self.get_classes(classes_path)
        num_classes = len(self.class_names)

        train_lines, valid_lines = self.get_train_valid_lines(data_path, validation_proportion)
        train_generator, valid_generator = self.make_train_valid_generator(train_lines,
                                                                        valid_lines,
                                                                        batch_size,
                                                                        num_classes,
                                                                        validation_proportion)

        if not hasattr(self, 'model'):
            self.model = self.create_model(ObjectDetectionConfig.INPUT_SHAPE,
                                           ObjectDetectionConfig.ANCHORS,
                                           num_classes,
                                           learning_rate=learning_rate)
        self.model.compile(optimizer=Adam(lr=learning_rate), loss='mean_squared_error')

        self.model.fit_generator(train_generator,
                                steps_per_epoch=(len(train_lines) // batch_size) + 1,
                                validation_data = valid_generator,
                                validation_steps=(len(valid_lines) // batch_size) + 1,
                                epochs=epochs,
                                callbacks=[])


    def get_train_valid_lines(self, data_path, validation_proportion):
        with open(data_path) as f:
            annotation_lines = f.readlines()

        num_val = int(len(annotation_lines) * validation_proportion)
        num_train = len(annotation_lines) - num_val

        return annotation_lines[:num_train], annotation_lines[num_train:]


    def make_train_valid_generator(self,
                                train_lines,
                                valid_lines,
                                batch_size,
                                num_classes,
                                validation_proportion):
        train_generator = self.data_generator(train_lines,
                                              batch_size,
                                              ObjectDetectionConfig.INPUT_SHAPE,
                                              ObjectDetectionConfig.ANCHORS,
                                              num_classes)
        valid_generator = self.data_generator(valid_lines,
                                              batch_size,
                                              ObjectDetectionConfig.INPUT_SHAPE,
                                              ObjectDetectionConfig.ANCHORS,
                                              num_classes)
        return train_generator, valid_generator


    def predict(self, data_path, result_path = ObjectDetectionConfig.RESULT_FOLDER):
        if not os.path.isdir(result_path):
            os.makedirs(result_path)

        self.sess = K.get_session()
        get_image_from = get_data_path_type(data_path)
        if get_image_from == 'image':
            image = Image.open(data_path)
            image = self._detect_image(image)
            opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv2.imwrite(os.path.join(result_path, os.path.basename(data_path)), opencvImage)
        elif get_image_from == 'directory':
            filenames = os.listdir(data_path)
            for filename in filenames:
                file_full_path = os.path.join(data_path, filename)
                image = Image.open(file_full_path)
                image = self._detect_image(image)
                opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                cv2.imwrite(os.path.join(result_path, filename), opencvImage)


    def save(self, weights_path):
        self.model.save_weights(weights_path)


    def load(self, weights_path, classes_path):
        self.class_names = self.get_classes(classes_path)
        num_classes = len(self.class_names)
        self.model = self.create_model(ObjectDetectionConfig.INPUT_SHAPE,
                                       ObjectDetectionConfig.ANCHORS,
                                       num_classes)
        self.model.load_weights(weights_path, by_name=True, skip_mismatch=True)


    def create_model_body(self,
                        anchors,
                        num_classes):
        image_input = Input(shape=(None, None, 3))
        num_anchors = len(anchors)

        model_body = yolo_body(image_input, num_anchors // 3, num_classes)

        # num = len(model_body.layers)-3
        # for i in range(num):
        #     model_body.layers[i].trainable = False

        return model_body


    def create_model(self,
                    input_shape,
                    anchors,
                    num_classes,
                    learning_rate = 1e-3):
        K.clear_session()  # get a new session

        self.model_body = self.create_model_body(anchors, num_classes)

        num_anchors = len(anchors)
        h, w = input_shape
        y_true = [Input(shape=(h // {0: 32, 1: 16, 2: 8}[l],
                               w // {0: 32, 1: 16, 2: 8}[l],
                               num_anchors // 3,
                               num_classes + 5)) for l in range(3)]

        model_loss = Lambda(
            yolo_loss,
            output_shape=(1,),
            name='yolo_loss',
            arguments={
                'anchors': anchors,
                'num_classes': num_classes,
                'ignore_thresh': 0.5})(
            [
                *self.model_body.output,
                *y_true])

        model = Model([self.model_body.input, *y_true], model_loss)

        if self.gpu_num > 1:
            model = multi_gpu_model(model, gpus=self.gpu_num)

        return model


    def data_generator(self, annotation_lines, batch_size,
                       input_shape, anchors, num_classes):
        '''data generator for fit_generator'''
        n = len(annotation_lines)
        i = 0
        while True:
            image_data = []
            box_data = []
            for b in range(batch_size):
                if i == 0:
                    np.random.shuffle(annotation_lines)
                image, box = get_random_data(
                    annotation_lines[i], input_shape, random=True)
                image_data.append(image)
                box_data.append(box)
                i = (i + 1) % n
            image_data = np.array(image_data)   # input of original yolo: image
            # output of original yolo: boxes
            box_data = np.array(box_data)
            # some kind of output description?!
            y_true = preprocess_true_boxes(
                box_data, input_shape, anchors, num_classes)
            yield [image_data, *y_true], np.zeros(batch_size)


    def get_classes(self, classes_path):
        '''loads the classes'''
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

    def _detect_image(self, image):
        input_image_shape = K.placeholder(shape=(2,))
        num_classes = len(self.class_names)

        self.boxes, self.scores, self.classes = yolo_eval(self.model_body.output, ObjectDetectionConfig.ANCHORS,
                                                          num_classes, input_image_shape,
                                                          score_threshold=0.3, iou_threshold=0.45)

        start = timer()

        boxed_image = letterbox_image(
            image, tuple(reversed(ObjectDetectionConfig.INPUT_SHAPE)))
        image_data = np.array(boxed_image, dtype='float32')

        image_data /= 255.
        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.

        out_boxes, out_scores, out_classes = self.sess.run(
            [self.boxes, self.scores, self.classes],
            feed_dict={
                self.model_body.input: image_data,
                input_image_shape: [image.size[1], image.size[0]],
                K.learning_phase(): 0
            })

        thickness = (image.size[0] + image.size[1]) // 300

        for i, c in reversed(list(enumerate(out_classes))):
            predicted_class = self.class_names[c]
            box = out_boxes[i]
            score = out_scores[i]

            label = '{} {:.2f}'.format(predicted_class, score)
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label)

            top, left, bottom, right = box
            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
            right = min(image.size[0], np.floor(right + 0.5).astype('int32'))

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            # My kingdom for a good redistributable image drawing library.
            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=ObjectDetectionConfig.RECTANGLE_COLOR)
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=ObjectDetectionConfig.RECTANGLE_COLOR)
            draw.text(list(text_origin), label, fill=ObjectDetectionConfig.TEXT_COLOR)
            del draw

        end = timer()

        return image

    def detect_video(self, video_path, output_path=""):
        vid = cv2.VideoCapture(video_path)
        print('vid: ', vid)
        print('output_path: ', output_path)
        if not vid.isOpened():
            raise IOError("Couldn't open webcam or video")
        video_FourCC = cv2.VideoWriter_fourcc(*"mp4v")
        video_fps = vid.get(cv2.CAP_PROP_FPS)
        video_size = (int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)),
                      int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        isOutput = True if output_path != "" else False
        if isOutput:
            print("!!! TYPE:", type(output_path), type(
                video_FourCC), type(video_fps), type(video_size))
            out = cv2.VideoWriter(
                output_path, video_FourCC, video_fps, video_size)
        accum_time = 0
        curr_fps = 0
        fps = "FPS: ??"
        prev_time = timer()
        while True:
            return_value, frame = vid.read()
            if not return_value:
                break
            image = Image.fromarray(frame)
            image = self._detect_image(image)
            result = np.asarray(image)
            curr_time = timer()
            exec_time = curr_time - prev_time
            prev_time = curr_time
            accum_time = accum_time + exec_time
            curr_fps = curr_fps + 1
            if accum_time > 1:
                accum_time = accum_time - 1
                fps = "FPS: " + str(curr_fps)
                curr_fps = 0
            cv2.putText(result, text=fps, org=(3, 15), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.50, color=(153, 204, 153), thickness=2)
            cv2.namedWindow("result", cv2.WINDOW_NORMAL)
            cv2.imshow("result", result)
            if isOutput:
                out.write(result)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break