from LabelmeUtils import LabelmePayload
import json

TEST_IMAGE = "./test.json"

if __name__ == "__main__":
    with open(TEST_IMAGE) as fp:
        # labelme_payload = json.load(fp)
        labelme_payload = LabelmePayload.LabelmePayload.from_json(json.load(fp))
    labelme_payload.get_image().show()

    cropped_images = labelme_payload.get_cropped_images(20)
    for image in cropped_images:
        image.show()

    drawn_image = labelme_payload.draw_shapes()
    labelme_payload.update_image(drawn_image)
    labelme_payload.get_image().show()

    payload_text = json.dumps(labelme_payload.to_dict())
    print(payload_text)
