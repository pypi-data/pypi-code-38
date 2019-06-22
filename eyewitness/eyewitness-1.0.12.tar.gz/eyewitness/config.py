from collections import namedtuple

# detection type
BBOX = 'bbox'

# Feedback obj type
FEEDBACK_BBOX_OBJ = 'feedback_bbox'
FEEDBACK_NO_OBJ = 'feedback_no_obj'

# image producer type
POST_PATH = 'post_path'
POST_BYTES = 'post_bytes'
IN_MEMORY = 'in_memory'

# Line false_alert msg template
LINE_FALSE_ALERT_MSG_TEMPLATE = "false_alert_{image_id}_{meta}"
LINE_FALSE_ALERT_ANNOTATION_PATTERN = (
    r"false_alert_(?P<channel>.*)--(?P<timestamp>\d*)--(?P<file_format>.*)_(?P<meta>.*)")

# audience_platfrom
LINE_PLATFROM = 'line'

# image_info fields
RAW_IMAGE_PATH = 'raw_image_path'
IMAGE_ID = 'image_id'
IMAGE_ID_STR_TEMPLATE = '{channel}--{timestamp}--{file_format}'
IMAGE_ID_STR_PATTERN = r'(?P<channel>.*)--(?P<timestamp>\d*)--(?P<file_format>.*)'

# detected_result fields
DRAWN_IMAGE_PATH = 'drawn_image_path'
DETECTED_OBJECTS = 'detected_objects'
DETECTION_METHOD = 'detection_method'

# audience_info fields
AUDIENCE_ID = 'audience_id'
RECEIVE_TIME = 'receive_time'
AUDIENCE_ID_STR_TEMPLATE = '{platform_id}--{user_id}'
AUDIENCE_ID_STR_PATTERN = r'(?P<platform_id>.*)--(?P<user_id>.*)'

# feedback infomation
FEEDBACK_METHOD = 'feedback_method'
FEEDBACK_MSG_OBJS = 'feedback_msg_objs'
FEEDBACK_META = 'feedback_meta'
IS_FALSE_ALERT = 'is_false_alert'


# detected object types:
BoundedBoxObject = namedtuple(
    'BoundedBoxObject', ['x1', 'y1', 'x2', 'y2', 'label', 'score', 'meta'])

DETECTED_OBJECT_TYPE_MAPPING = {BBOX: BoundedBoxObject}


# feedback object types:
BboxObjectFeedback = namedtuple('BboxObjectFeedback', ['x1', 'y1', 'x2', 'y2', 'label', 'meta'])
FEEDBACK_OBJECT_TYPE_MAPPING = {
    FEEDBACK_BBOX_OBJ: BboxObjectFeedback,
    FEEDBACK_NO_OBJ: None,  # this kind of feedback
}

# dataset config
DATASET_TRAIN_AND_VALID = 'TRAIN_AND_VALID'
DATASET_TEST_ONLY = 'TEST_ONLY'
DATASET_ALL = 'ALL'
