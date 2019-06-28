import numpy as np


class DeepblockLogConfig:
    NAME = "DEEPBLOCK_LOG"
    LOG_TYPE = "logType"
    PREDICT_START = "predictStarted"
    PREDICT_END = "predictFinished"
    SAVE_START = "startSavingModel"
    SAVE_END = "finishSavingModel"
    RESULT = "result"
    SUCCESS = "success"
    TRAIN_START = "trainStarted"
    TRAIN_END = "trainFinished"


class ImageClassificationConfig:
    NAME = "IMAGE_CLASSIFICATION"
    INPUT_SHAPE = (224, 224, 3)


class MultiLabelClassificationConfig:
    NAME = "MULTI_LABEL_CLASSIFICATION"
    INPUT_SHAPE = (224, 224, 3)


class DeblurConfig:
    NAME = 'CONFIG_DEBLUR'
    RESULT_FOLDER = "results/deblur"
    NGF = 64
    NDF = 64
    OUTPUT_NC = 3
    N_BLOCKS_GEN = 9
    CELL_SHAPE = (512, 512, 3)


class ObjectDetectionConfig:
    NAME = "OBJECT_DETECTION"
    RESULT_FOLDER = "results/object_detection"
    INPUT_SHAPE = (416, 416)
    RECTANGLE_COLOR = (153, 204, 153)
    TEXT_COLOR = (51, 204, 204)
    ANCHORS = np.array([10.0, 13.0,
                        16.0, 30.0,
                        33.0, 23.0,
                        30.0, 61.0,
                        62.0, 45.0,
                        59.0, 119.0,
                        116.0, 90.0,
                        156.0, 198.0,
                        373.0, 326.0]).reshape(-1, 2)


class MaskRCNNConfig:
    NAME = 'MASK_RCNN'
    RESULT_FOLDER = "results/segmentation"
    GPU_COUNT = 1
    IMAGES_PER_GPU = 2
    STEPS_PER_EPOCH = 1000
    VALIDATION_STEPS = 50
    BACKBONE = "resnet101"
    COMPUTE_BACKBONE_SHAPE = None
    BACKBONE_STRIDES = [4, 8, 16, 32, 64]
    FPN_CLASSIF_FC_LAYERS_SIZE = 1024
    TOP_DOWN_PYRAMID_SIZE = 256
    NUM_CLASSES = 1  # Override in sub-classes
    RPN_ANCHOR_SCALES = (32, 64, 128, 256, 512)
    RPN_ANCHOR_RATIOS = [0.5, 1, 2]
    RPN_ANCHOR_STRIDE = 1
    RPN_NMS_THRESHOLD = 0.7
    RPN_TRAIN_ANCHORS_PER_IMAGE = 256
    PRE_NMS_LIMIT = 6000
    POST_NMS_ROIS_TRAINING = 2000
    POST_NMS_ROIS_INFERENCE = 1000
    USE_MINI_MASK = True
    MINI_MASK_SHAPE = (56, 56)  # (height, width) of the mini-mask
    IMAGE_RESIZE_MODE = "square"
    IMAGE_MIN_DIM = 800
    IMAGE_MAX_DIM = 1024
    IMAGE_MIN_SCALE = 0
    IMAGE_CHANNEL_COUNT = 3
    MEAN_PIXEL = np.array([123.7, 116.8, 103.9])
    TRAIN_ROIS_PER_IMAGE = 200
    ROI_POSITIVE_RATIO = 0.33
    POOL_SIZE = 7
    MASK_POOL_SIZE = 14
    MASK_SHAPE = [28, 28]
    MAX_GT_INSTANCES = 100
    RPN_BBOX_STD_DEV = np.array([0.1, 0.1, 0.2, 0.2])
    BBOX_STD_DEV = np.array([0.1, 0.1, 0.2, 0.2])
    DETECTION_MAX_INSTANCES = 100
    DETECTION_MIN_CONFIDENCE = 0.7
    DETECTION_NMS_THRESHOLD = 0.3
    LEARNING_RATE = 0.001
    LEARNING_MOMENTUM = 0.9
    WEIGHT_DECAY = 0.0001
    LOSS_WEIGHTS = {
        "rpn_class_loss": 1.,
        "rpn_bbox_loss": 1.,
        "mrcnn_class_loss": 1.,
        "mrcnn_bbox_loss": 1.,
        "mrcnn_mask_loss": 1.
    }
    USE_RPN_ROIS = True
    TRAIN_BN = False  # Defaulting to False since batch size is often small

    # Gradient norm clipping
    GRADIENT_CLIP_NORM = 5.0

    def __init__(self):
        """Set values of computed attributes."""
        # Effective batch size
        self.BATCH_SIZE = self.IMAGES_PER_GPU * self.GPU_COUNT

        # Input image size
        if self.IMAGE_RESIZE_MODE == "crop":
            self.IMAGE_SHAPE = np.array([self.IMAGE_MIN_DIM, self.IMAGE_MIN_DIM,
                                         self.IMAGE_CHANNEL_COUNT])
        else:
            self.IMAGE_SHAPE = np.array([self.IMAGE_MAX_DIM, self.IMAGE_MAX_DIM,
                                         self.IMAGE_CHANNEL_COUNT])

        # Image meta data length
        # See compose_image_meta() for details
        self.IMAGE_META_SIZE = 1 + 3 + 3 + 4 + 1 + self.NUM_CLASSES

    def display(self):
        """Display Configuration values."""
        print("\nConfigurations:")
        for a in dir(self):
            if not a.startswith("__") and not callable(getattr(self, a)):
                print("{:30} {}".format(a, getattr(self, a)))
        print("\n")


class SuperResolutionConfig:
    NAME = 'SUPER_RESOLUTION'
    RESULT_FOLDER = "results/super_resolution"
    IMAGES_FOLDER = "cropped_images"
    LR_FOLDER = "lr"
    SR_FOLDER = "sr"
    NUM_FILTERS = 64
    NUM_RES_BLOCKS = 16
    IMAGE_WIDTH = 8
    IMAGE_HEIGHT = 8
    IMAGE_CHANNELS = 3
    SCALE = 2
