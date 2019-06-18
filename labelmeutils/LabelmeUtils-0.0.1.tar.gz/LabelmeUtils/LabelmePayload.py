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

    @staticmethod
    def from_json(json_payload):
        hold = LabelmePayload()
        hold._load_attrib_data_from_json(json_payload)
        hold._load_image_from_json(json_payload)
        hold._load_shapes_from_json(json_payload)
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
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def _load_attrib_data_from_json(self, json_payload):
        if "version" in json_payload:
            self.version = json_payload["version"]
        if "flags" in json_payload:
            self.flags = json_payload["flags"]

    def _load_image_from_json(self, json_payload):
        assert "imagePath" in json_payload, "Json payload does not contain an image path"
        assert "imageData" in json_payload, "Json payload does not contain an image payload"
        assert "imageHeight" in json_payload, "Json payload does not contain an imageHeight"
        assert "imageWidth" in json_payload, "Json payload does not contain an imageWidth"
        self.imagePath = json_payload["imagePath"]
        self.imageData = json_payload["imageData"]
        self.imageHeight = json_payload["imageHeight"]
        self.imageWidth = json_payload["imageWidth"]

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
