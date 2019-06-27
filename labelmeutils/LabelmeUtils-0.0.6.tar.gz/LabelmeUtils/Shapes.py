import json
from PIL import ImageDraw
from math import ceil


class Shape:
    _IDENTIFIER = "unknown"

    def __init__(self,
                 label=None,
                 line_color=None,
                 fill_color=None,
                 points=None,
                 shape_type=None,
                 flags=None,
                 other_data=None):

        self.label = label
        self.line_color = line_color
        self.fill_color = fill_color
        self.points = [] if points is None else points
        self.shape_type = Shape._IDENTIFIER if shape_type is None else shape_type
        self.flags = {} if flags is None else flags
        self.other_data = {} if other_data is None else other_data

    def to_dict(self):
        return {"label": self.label,
                "line_color": self.line_color,
                "fill_color": self.fill_color,
                "points": self.points,
                "shape_type": self.shape_type,
                "flags": self.flags,
                **self.other_data}

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

        attribs = ["shape_type", "points", "line_color", "fill_color", "label", "flags"]
        for attrib in attribs:
            if attrib in json_payload:
                setattr(hold, attrib, json_payload[attrib])

        for key, value in json_payload.items():
            if key not in attribs:
                hold.other_data[key] = value

        return hold


class Rectangle(Shape):
    _IDENTIFIER = "rectangle"

    def __init__(self,
                 label=None,
                 line_color=None,
                 fill_color=None,
                 points=None,
                 shape_type=None,
                 flags=None,
                 other_data=None):

        Shape.__init__(
            self,
            label=label,
            line_color=line_color,
            fill_color=fill_color,
            points=points,
            shape_type=Rectangle._IDENTIFIER if shape_type is None else shape_type,
            flags=flags,
            other_data=other_data)

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