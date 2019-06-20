from LabelmeUtils.LabelmePayload import LabelmePayload
import json
from random import randint

TEST_IMAGE = "./test.json"
TEST_OUT = "./test_out.json"

if __name__ == "__main__":
    with open(TEST_IMAGE) as fp:
        # labelme_payload = json.load(fp)
        labelme_payload = LabelmePayload.from_json(json.load(fp))
    labelme_payload.get_image().show()

    cropped_images = labelme_payload.get_cropped_images(20)
    for image in cropped_images:
        image.show()

    for shape in labelme_payload.shapes:
        shape.otherData["prob"] = randint(0, 100)/100.0
        shape.flags["prob"] = randint(0, 100)/100.0

    labelme_payload.otherData["test"] = "what to i do"
    labelme_payload.otherData["test2"] = True
    labelme_payload.flags["test2"] = "asdf"

    drawn_image = labelme_payload.draw_shapes()
    labelme_payload.update_image(drawn_image)
    labelme_payload.get_image().show()

    payload_text = json.dumps(labelme_payload.to_dict(), indent=1)
    print(payload_text)

    with open(TEST_OUT, "w") as fp:
        fp.write(payload_text)
