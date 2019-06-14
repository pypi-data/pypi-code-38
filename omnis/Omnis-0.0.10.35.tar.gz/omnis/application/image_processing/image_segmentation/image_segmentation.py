import os
import json
import numpy as np
import random
import skimage.draw
import skimage.io
from matplotlib import pyplot as plt
import cv2
from ...application import Application

# Import Mask RCNN
from ....lib.mask_rcnn import model as modellib, utils, visualize
from ....lib.config_lib import MaskRCNNConfig
from ....lib.general_lib import get_data_path_type, divide_train_val_dataset
from ....lib.custom_callback import ImageClassificationCallback


class Image_Segmentation(Application):
    def __init__(self, class_list_path=None, weights_path=None, backbone=None, default_weights_path='coco.h5'):
        super().__init__()

        self.config = CustomConfig()
        self.weights_path = weights_path
        self.action = None
        self.default_weights_path = default_weights_path
        
        if not isinstance(backbone, type(None)):
            self.config.BACKBONE = backbone
        if not isinstance(weights_path, type(None)):
            if isinstance(class_list_path, type(None)):
                raise ValueError(
                    "you should write class list and weights_path both")
            else:
                self.load(class_list_path, weights_path)

    
    def train(self,
            data_path,
            annotation_path,
            learning_rate=0.01,
            epochs=10,
            layers='heads',
            callbacks=[],
            verbose=0):
        get_image_from = get_data_path_type(data_path)
        dataset_train, dataset_val = self.make_train_valid_dataset_and_set_class_list(data_path, annotation_path)

        if self.action != "train":
            self.create_model(mode="training")
            self.load_weights_for_train(self.weights_path)
            self.action = "train"

        if self.deepblock_log == True:
            log_dict = OrderedDict()
            log_dict[DeepblockLogConfig.LOG_TYPE] = DeepblockLogConfig.TRAIN_START
            return json.dumps(log_dict, ensure_ascii=False)

        if self.deepblock_log:
            callbacks += [ImageClassificationCallback(total_step=self.config.STEPS_PER_EPOCH, total_epoch=epochs)]

        self.model.train(dataset_train, dataset_val,
                    learning_rate=learning_rate,
                    epochs=epochs,
                    layers=layers,
                    custom_callbacks=callbacks,
                    verbose=verbose)

        if self.deepblock_log == True:
            log_dict = OrderedDict()
            log_dict[DeepblockLogConfig.LOG_TYPE] = DeepblockLogConfig.TRAIN_END
            return json.dumps(log_dict, ensure_ascii=False)


    def predict(
            self,
            data_array=None,
            data_path=None,
            predict_classes=True,
            verbose=0,
            steps=None,
            use_coco_config=False,
            result_path = MaskRCNNConfig.RESULT_FOLDER):
        if self.action != "predict":
            self.create_model(mode="inference")
            self.load_weights_for_predict(self.weights_path)
            self.action = "predict"
        
        get_image_from = get_data_path_type(data_path)

        if self.deepblock_log == True:
            log_dict = OrderedDict()
            log_dict[DeepblockLogConfig.LOG_TYPE] = DeepblockLogConfig.PREDICT_START
            return json.dumps(log_dict, ensure_ascii=False)
  
        if get_image_from == "directory":
            for image_file in os.listdir(data_path):
                self.save_after_detect_one_image(os.path.join(data_path, image_file), result_path)
        elif get_image_from == "image":
            self.save_after_detect_one_image(data_path, result_path)

        if self.deepblock_log == True:
            log_dict = OrderedDict()
            log_dict[DeepblockLogConfig.LOG_TYPE] = DeepblockLogConfig.PREDICT_END
            return json.dumps(log_dict, ensure_ascii=False)

    def save(self, class_list_path, weights_path):
        self.model.keras_model.save_weights(weights_path)
        with open(class_list_path, 'w') as f:
            for i in range(self.config.NUM_CLASSES):
                f.write("%s" % self.config.CLASS_NAMES[i])
                i += 1
                if i != self.config.NUM_CLASSES:
                    f.write("\n")


    def load(self, class_list_path=None, weights_path=None):
        if isinstance(class_list_path, type(None)):
            raise ValueError("Class names should be given")
        if isinstance(weights_path, type(None)):
            raise ValueError("Weights path should be given")

        class_file = open(class_list_path, 'r')
        class_objects = class_file.read()
        class_file.close()
        class_list = class_objects.split('\n')
        # remove last class_list
        self.setConfig(class_list=class_list)
        self.weights_path = weights_path

    def create_weights_folder(self, weights_path):
        weights_folder = os.path.dirname(weights_path)

        if weights_folder != '':
            if not os.path.exists(weights_folder):
                os.makedirs(weights_folder)

    def load_weights_for_train(self, weights_path):
        self.create_weights_folder(self.default_weights_path)

        if isinstance(self.weights_path, type(None)):
            self.weights_path = self.default_weights_path
            if not os.path.exists(self.default_weights_path):
                utils.download_trained_weights(self.weights_path)
        self.model.load_weights(self.weights_path, by_name=True, exclude=[
            "mrcnn_class_logits", "mrcnn_bbox_fc",
            "mrcnn_bbox", "mrcnn_mask"])


    def load_weights_for_predict(self, weights_path):
        self.create_weights_folder(self.default_weights_path)

        if isinstance(self.weights_path, type(None)):
            if not os.path.exists(self.default_weights_path):
                utils.download_trained_weights(self.weights_path)
        self.model.load_weights(self.weights_path, by_name=True)


    def evaluate(self, data_path, annotation_path="via_region_data.json"):
        if self.action != "predict":
            self.create_model(mode="inference")
            self.load_weights_for_predict(self.weights_path)
            self.action = "predict"
            
        get_image_from = get_data_path_type(data_path) 

        accuracy = 0
        num_files = 0
        if get_image_from == "directory":
            dataset_eval = ImageDataset()
            dataset_eval.load_class(self.val_dataset, annotation_path)
            image_info = dataset_eval.image_info
            for one_image_info in image_info:
                file_path = one_image_info['path']
                file_polygons = one_image_info['polygons']
                height = one_image_info['height']
                width = one_image_info['width']

                mask_by_polygons = self.fill_true_by_polygons(width, height, file_polygons)
 
                r, image_data = self.detect_one_image(file_path, verbose=0)
                masks = r['masks']
                mask_by_detection = self.fill_true_by_multiple_masks(width, height, masks)

                sum_area = np.logical_or(mask_by_detection, mask_by_polygons)
                overlapped_area = np.logical_and(mask_by_detection, mask_by_polygons)

                accuracy += np.count_nonzero(overlapped_area) / np.count_nonzero(sum_area)
                num_files += 1
        else:
            raise ValueError("You should give folder which have images and annotation for evaluate")
        print("%d files average accuracy : %f" % (num_files, accuracy/num_files))


    def create_model(self, mode="training"):
        self.config.GPU_COUNT = self.gpu_num
        self.config.BATCH_SIZE = self.config.GPU_COUNT * self.config.IMAGES_PER_GPU
        self.model = modellib.MaskRCNN(
            mode=mode, config=self.config, model_dir='.')
        self.model.config.display()


    def fill_true_by_multiple_masks(self, width, height, masks):
        total_board = np.zeros((height, width), dtype=bool)
        for i in range(masks.shape[-1]):
            mask = masks[:,:,i]
            total_board = np.bitwise_or(total_board, mask)
        return total_board


    def fill_true_by_polygons(self, width, height, file_polygons):
        total_board = np.zeros((height, width))
        for i in range(len(file_polygons)):
            one_polygon = file_polygons[i]
            all_points_x = np.asarray(one_polygon['all_points_x'])
            all_points_y = np.asarray(one_polygon['all_points_y'])
            pair_x_y = np.array(zip(all_points_x, all_points_y))

            total_board = cv2.fillPoly(total_board, pts=[pair_x_y], color=1)
        return total_board.astype(bool)

    
    def make_train_valid_dataset_and_set_class_list(self, data_path, annotation_path):
        self.train_dataset, self.val_dataset = divide_train_val_dataset(data_path)

        dataset_train = ImageDataset()
        dataset_train.load_class(self.train_dataset, annotation_path)
        dataset_train.prepare()
        print("Images: {}\nClasses: {}".format(
            len(dataset_train.image_ids), dataset_train.class_names))

        dataset_val = ImageDataset()
        dataset_val.load_class(self.val_dataset, annotation_path)
        dataset_val.prepare()
        print("Images: {}\nClasses: {}".format(
            len(dataset_val.image_ids), dataset_val.class_names))

        assert sorted(dataset_train.class_names) == sorted(
            dataset_val.class_names), "train classes have to be same with val classes"
        self.setConfig(class_list=dataset_train.class_names)

        return dataset_train, dataset_val

    def detect_one_image(self, file_path, verbose = 1):
        predict_image = skimage.io.imread(file_path)
        results = self.model.detect([predict_image], verbose=verbose)
        r = results[0]
        image_data = [predict_image]

        return r, image_data


    def save_after_detect_one_image(self, file_path, result_path):
        _, filename = os.path.split(file_path)
        r, image_data = self.detect_one_image(file_path)

        if not os.path.isdir(result_path):
            os.makedirs(result_path)

        plt = self.mask(image_data=image_data, r=r)
        plt.savefig(os.path.join(result_path, filename))


    def setConfig(self, class_list, detection_threshold=0.8,
                  backbone='resnet50'):
        self.config.CLASS_NAMES = class_list
        self.config.NUM_CLASSES = len(class_list)
        self.config.IMAGE_META_SIZE = 12 + self.config.NUM_CLASSES
        self.config.DETECTION_MIN_CONFIDENCE = detection_threshold
        self.config.BACKBONE = backbone

    def mask(self, image_data, r, show_mask=True):
        plt, mask = visualize.display_instances(image_data[0], r['rois'], r['masks'], r['class_ids'],
                                                self.config.CLASS_NAMES, r['scores'], show_mask=show_mask)
        return plt

    

class ImageDataset(utils.Dataset):
    def image_reference(self, image_id):
        """Return the path of the image."""
        info = self.image_info[image_id]
        if info["source"] == "source":
            return info["path"]
        else:
            super(self.__class__, self).image_reference(image_id)

    def load_mask(self, image_id):
        """Generate instance masks for an image.
       Returns:
        masks: A bool array of shape [height, width, instance count] with
            one mask per instance.
        class_ids: a 1D array of class IDs of the instance masks.
        """
        image_info = self.image_info[image_id]
        if image_info["source"] != "source":
            return super(self.__class__, self).load_mask(image_id)

        info = self.image_info[image_id]
        mask = np.zeros([info["height"], info["width"], len(info["polygons"])],
                        dtype=np.uint8)
        for i, p in enumerate(info["polygons"]):
            rr, cc = skimage.draw.polygon(p['all_points_y'], p['all_points_x'])
            mask[rr, cc, i] = 1
        if info["class_ids"]:
            class_ids = np.array(info["class_ids"], dtype=np.int32)
            return mask.astype(np.bool), class_ids
        else:
            return super(self.__class__, self).load_mask(image_id)

    def load_class(self, dataset, annotation_path):
        """Load annotations of the dataset and add classes.
        dataset: List of the dataset.
        """
        dataset_dir = os.path.dirname(dataset[0])

        coco_json = json.load(open(annotation_path))
        classes = []
        for c in coco_json['categories']:
            if c['name'] not in classes:
                classes.append(c['name'])
        
        class_list = sorted(classes)
        j = 1
        for class_name in class_list:
            self.add_class("source", j, class_name)
            j += 1

        imageId = -1
        polygons = []
        annotations = {}
        class_ids = []
        j = 0
        for a in sorted(coco_json['annotations'], key=lambda ann: ann['imageId']):
            annotations = {'name': 'polygon'}
            x = []
            y = []
            for i, coordinate in enumerate(a['segmentation']):
                if i%2 == 0:
                    x.append(coordinate)
                else:
                    y.append(coordinate)
            annotations['all_points_x'] = x
            annotations['all_points_y'] = y
            cl = classes[a['categoryId']-1]
            if imageId == a['imageId']:
                polygons.append(annotations)
                class_ids.append(class_list.index(cl) + 1)
            else:
                if j != 0:
                    filename = coco_json['images'][j-1]['fileName']
                    image_path = os.path.join(dataset_dir, filename)
                    image = skimage.io.imread(image_path)
                    height, width = image.shape[:2]
                    self.add_image(
                        "source",
                        image_id=filename,  # use file name as a unique image id
                        path=image_path,
                        width=width, height=height,
                        polygons=polygons,
                        class_ids=class_ids)
                    class_ids = []
                class_ids.append(class_list.index(cl) + 1)
                imageId = a['imageId']
                polygons = [annotations]
                j += 1
        filename = coco_json['images'][j-1]['fileName']
        image_path = os.path.join(dataset_dir, filename)
        image = skimage.io.imread(image_path)
        height, width = image.shape[:2]
        self.add_image(
            "source",
            image_id=filename,  # use file name as a unique image id
            path=image_path,
            width=width, height=height,
            polygons=polygons,
            class_ids=class_ids)


############################################################
#  Configurations
############################################################


class CustomConfig(MaskRCNNConfig):
    """Configuration for training on the custom dataset.
    Derives from the base Config class and overrides some values.
    """
    # Give the configuration a recognizable name
    # TODO: have to change Name of config for log etc.
    NAME = "CUSTOMMRCNN"

    # Number of classes (including background)
    NUM_CLASSES = 1  # Background + classes

    # Number of training steps per epoch
    STEPS_PER_EPOCH = 50

    # Skip detections with < 60% confidence
    DETECTION_MIN_CONFIDENCE = 0.8

    # Names of classes
    CLASS_NAMES = []

    IMAGE_META_SIZE = 13

    BATCH_SIZE = 1

    # BACKBONE should be resnet 50 or resnet 101
    BACKBONE = "resnet50"

    # params to reduce memory
    TRAIN_ROIS_PER_IMAGE = 100
    IMAGES_PER_GPU = 1
    MAX_GT_INSTANCES = 30