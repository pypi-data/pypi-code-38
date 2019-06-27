from LabelmeUtils.LabelmePayload import LabelmePayload
from LabelmeUtils.Shapes import Rectangle
import json
from random import randint

TEST_IMAGE = "./test.json"
TEST_OUT = "./test_out.json"

if __name__ == "__main__":
    with open(TEST_IMAGE) as fp:
        # labelme_payload = json.load(fp)
        labelme_payload = LabelmePayload.from_json(json.load(fp))

    new_labelme_payload = LabelmePayload()
    new_labelme_payload.update_image(labelme_payload.get_image())
    for shape in labelme_payload.shapes:
        new_labelme_payload.shapes.append(Rectangle(points = shape.points))

    with open(TEST_OUT, "w") as fp:
        fp.write(new_labelme_payload.to_json())