import io

import flask_admin
from flask import Flask
from flask import request
from flask_admin.contrib.peewee import ModelView
from eyewitness.image_id import ImageId
from eyewitness.models.db_proxy import DATABASE_PROXY
from eyewitness.models.detection_models import (ImageInfo, BboxDetectionResult)
from eyewitness.image_utils import ImageHandler, Image
from eyewitness.config import (
    DRAWN_IMAGE_PATH,
    RAW_IMAGE_PATH,
    IMAGE_ID,
)


class BboxObjectDetectionFlaskWrapper(object):
    def __init__(self, obj_detector, image_register, detection_result_handlers,
                 database, with_admin=False, drawn_image_dir=None,
                 detection_result_filters=[]
                 ):
        app = Flask(__name__)
        self.app = app
        self.obj_detector = obj_detector
        self.detection_result_handlers = detection_result_handlers
        self.database = database
        self.image_register = image_register
        self.drawn_image_dir = drawn_image_dir
        self.detection_result_filters = detection_result_filters

        DATABASE_PROXY.initialize(self.database)
        ImageInfo.create_table()
        BboxDetectionResult.create_table()

        if with_admin:
            admin = flask_admin.Admin(app, name='Example: Eyewitness')
            admin.add_view(ModelView(ImageInfo))
            admin.add_view(ModelView(BboxDetectionResult))

        @app.route("/detect_post_bytes", methods=['POST'])
        def detect_image_bytes_objs():
            image_id = ImageId.from_str(request.headers[IMAGE_ID])
            raw_image_path = request.headers.get(RAW_IMAGE_PATH)
            self.image_register.register_image(image_id, {RAW_IMAGE_PATH: raw_image_path})

            # read data from Bytes
            data = request.data
            image_data_raw = io.BytesIO(bytearray(data))
            image_raw = ImageHandler.read_image_bytes(image_data_raw)

            if raw_image_path:
                ImageHandler.save(image_raw, raw_image_path)

            image_obj = Image(image_id, pil_image_obj=image_raw)
            self.detect_and_handling(image_obj)
            return "successfully detected"

        @app.route("/detect_post_path", methods=['POST'])
        def detect_image_file_objs():
            image_id = ImageId.from_str(request.headers[IMAGE_ID])
            raw_image_path = request.headers[RAW_IMAGE_PATH]
            self.image_register.register_image(image_id, {RAW_IMAGE_PATH: raw_image_path})

            image_obj = Image(image_id, raw_image_path=raw_image_path)
            self.detect_and_handling(image_obj)
            return "successfully detected"

    def detect_and_handling(self, image_obj):
        # detect objs
        detection_result = self.obj_detector.detect(image_obj)
        for detection_result_filter in self.detection_result_filters:
            detection_result = detection_result_filter.apply(detection_result)

        # draw and save image, as object detected update detection result
        if self.drawn_image_dir and len(detection_result.detected_objects) > 0:
            self.draw_bbox_for_detection_result(image_obj, detection_result)

        for detection_result_handler in self.detection_result_handlers:
            detection_result_handler.handle(detection_result)

    def draw_bbox_for_detection_result(self, image_obj, detection_result):
        """ write the detected_result image to <drawn_dr>/<channel>--<timestamp>.<file_format>

        Parameters
        ----------
        image_obj: eyewitness.image_util.Image
            eyewitness image obj
        detection_result: DetectionResult
            detection result
        """
        drawn_image_path = "%s/%s--%s.%s" % (
            self.drawn_image_dir, image_obj.image_id.channel, image_obj.image_id.timestamp,
            image_obj.image_id.file_format)
        ImageHandler.draw_bbox(image_obj.pil_image_obj, detection_result.detected_objects)
        ImageHandler.save(image_obj.pil_image_obj, drawn_image_path)
        detection_result.image_dict[DRAWN_IMAGE_PATH] = drawn_image_path
