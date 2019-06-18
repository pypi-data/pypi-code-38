import json
from PIL import ImageDraw
from math import ceil


class Shape:

    def __init__(self):
        self.label = None
        self.line_color = None
        self.fill_color = None
        self.points = []
        self.shape_type = "unknown"

    def to_dict(self):
        return {"label": self.label,
                "line_color": self.line_color,
                "fill_color": self.fill_color,
                "points": self.points,
                "shape_type": self.shape_type}

    def to_json(self):
        return json.dumps(self.to_dict())

    def crop_image(self, image):
        raise Exception("Function not implemented for this shape")

    def draw_shape(self, image):
        raise Exception("Function not implemented for this shape")

    @staticmethod
    def from_json(json_payload, hold=None):
        if hold is None:
            hold = Shape()

        if "shape_type" in json_payload:
            hold.shape_type = json_payload["shape_type"]
        if "points" in json_payload:
            hold.points = json_payload["points"]
        if "line_color" in json_payload:
            hold.line_color = json_payload["line_color"]
        if "fill_color" in json_payload:
            hold.fill_color = json_payload["fill_color"]
        if "label" in json_payload:
            hold.label = json_payload["label"]
        return hold


class Rectangle(Shape):
    _IDENTIFIER = "rectangle"

    def __init__(self):
        Shape.__init__(self)

    @staticmethod
    def from_json(json_payload, hold=None):
        hold = Rectangle()
        Shape.from_json(json_payload, hold)
        assert hold.shape_type == __class__._IDENTIFIER, "Shape type must be a rectangle"
        return hold

    @classmethod
    def get_identifier(cls):
        return cls._IDENTIFIER

    def crop_image(self, image, padding=None):
        x1, y1, x2, y2 = self.points[0][0], self.points[0][1], self.points[1][0], self.points[1][1]
        if isinstance(padding, int):
            x1, y1, x2, y2 = \
                max(x1-padding, 0), max(y1-padding, 0), min(x2+padding, image.width), min(y2+padding, image.height)
        elif isinstance(padding, float):
            padding_x = int(ceil((x2-x1)*padding/2))
            padding_y = int(ceil((y2-y1)*padding/2))
            x1, y1, x2, y2 = max(x1-padding_x, 0), max(y1-padding_y, 0), \
                min(x2+padding_x, image.width), min(y2+padding_y, image.height)
        return image.crop((x1, y1, x2, y2))

    def draw_shape(self, image):
        x1, y1, x2, y2 = self.points[0][0], self.points[0][1], self.points[1][0], self.points[1][1]
        draw = ImageDraw.Draw(image)
        draw.line((x1, y1, x2, y1), fill=128, width=5)
        draw.line((x2, y1, x2, y2), fill=128, width=5)
        draw.line((x2, y2, x1, y2), fill=128, width=5)
        draw.line((x1, y2, x1, y1), fill=128, width=5)


class ShapeFactory:
    SUPPORTED_SHAPE_TYPES = {Rectangle.get_identifier(): Rectangle}
    @staticmethod
    def from_json(json_payload):
        assert "shape_type" in json_payload, "Json payload does not have a shape type"
        shape_type = json_payload["shape_type"]
        return __class__.SUPPORTED_SHAPE_TYPES.get(shape_type, Shape).from_json(json_payload)