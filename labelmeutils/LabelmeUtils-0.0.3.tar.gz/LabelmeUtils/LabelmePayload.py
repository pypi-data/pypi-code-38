from .Shapes import ShapeFactory
import json
from PIL import Image
from io import BytesIO
import base64


class LabelmePayload:

    def __init__(self):
        self.version = "3.11.2"
        self.flags = {}
        self.shapes = []
        self.imagePath = ""
        self.imageData = ""
        self.imageHeight = 0
        self.imageWidth = 0
        self.lineColor = [0, 255, 0, 128]
        self.fillColor = [255, 0, 0, 128]
        self.otherData = {}

    @staticmethod
    def from_json(json_payload):
        hold = LabelmePayload()
        hold._set_data_from_json(json_payload)
        return hold

    def to_dict(self):
        return {
            "version": self.version,
            "flags": self.flags,
            "shapes": [shape.to_dict() for shape in self.shapes],
            "imagePath": self.imagePath,
            "imageData": self.imageData,
            "imageHeight": self.imageHeight,
            "imageWidth": self.imageWidth,
            "lineColor": self.lineColor,
            "fillColor": self.fillColor,
            **self.otherData,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def _set_data_from_json(self, json_payload):
        attrib_fields = ["version", "flags"]
        for field in attrib_fields:
            assert field in json_payload, "Json payload does not contain:" + field
            setattr(self, field, json_payload[field])

        required_fields = ["imagePath", "imageData", "imageHeight", "imageWidth", "lineColor", "fillColor"]
        for field in required_fields:
            assert field in json_payload, "Json payload does not contain:" + field
            setattr(self, field, json_payload[field])

        self._load_shapes_from_json(json_payload)

        for key, value in json_payload.items():
            if key not in required_fields and key not in required_fields and key != "shapes":
                self.otherData[key] = value

    def _load_shapes_from_json(self, json_payload):
        if "shapes" not in json_payload:
            return
        shapes = json_payload["shapes"]
        assert isinstance(shapes, (list,)), "Shapes object is not of type list"

        self.shapes = []
        for shape_json in shapes:
            self.shapes.append(ShapeFactory.from_json(shape_json))

    def get_image(self):
        return Image.open(BytesIO(base64.b64decode(self.imageData)))

    def draw_shapes(self):
        hold = self.get_image()
        for shape in self.shapes:
            shape.draw_shape(hold)
        return hold

    def get_cropped_images(self, padding=None):
        return list(self.cropped_image_generator(padding))

    def cropped_image_generator(self, padding=None):
        hold = self.get_image()
        for shape in self.shapes:
            yield shape.crop_image(hold, padding)

    def update_image(self, image):
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        b64str = base64.b64encode(buffered.getvalue())

        self.imageData = str(b64str, "utf-8")
        self.imageHeight = image.height
        self.imageWidth = image.width
