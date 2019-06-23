import base64
import six


class BaseCallbackImages(object):
    @classmethod
    def _image_to_json(cls, img):
        # need to check for string types because we have keep_origin option
        if isinstance(img, six.string_types):
            if six.PY2:
                encoded = base64.b64encode(img)
            else:
                encoded = base64.b64encode(img.encode()).decode()
        else:
            encoded = base64.b64encode(img).decode()

        return encoded

    @classmethod
    def _prepare_images_payload(cls, image_objects, keep_origin, uri):
        first_entry = image_objects[0]
        if keep_origin:
            original_image = str(uri)
        else:
            original_image = first_entry["original_image"]

        heat_maps = []
        for i, img_obj in enumerate(image_objects):
            entry = {
                "number": i + 1,  # this should start from 1
                "heatmap_image": cls._image_to_json(img_obj["heatmap_image"]),
                "heatmap_image_key": img_obj["heatmap_image_key"],
                "meta": img_obj["meta"]
            }
            heat_maps.append(entry)

        images = {
            "original_image_key": first_entry["original_image_key"],
            "heatmaps": heat_maps,
            "original_image": cls._image_to_json(original_image)
        }

        return images
