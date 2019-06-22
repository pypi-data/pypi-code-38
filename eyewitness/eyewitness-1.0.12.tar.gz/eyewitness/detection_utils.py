import json
import six
from abc import ABCMeta, abstractmethod

from eyewitness.config import (
    BBOX,
    DETECTED_OBJECTS,
    DETECTION_METHOD,
    DETECTED_OBJECT_TYPE_MAPPING,
    DRAWN_IMAGE_PATH,
    IMAGE_ID,
)
from eyewitness.image_id import ImageId


class DetectionResult(object):
    """
    represent detection result of a image.
    """

    def __init__(self, image_dict):
        """
        Parameters
        ----------
        image_dict: dict
            - detection_method: detection_method str

            - detected_objects: List[tuple], list of detected obj (optional)

            - drawn_image_path: str, path of drawn image (optional)

            - image_id: image_id obj
        """
        # get detection method
        self.detection_method = image_dict.get(DETECTION_METHOD, BBOX)
        self.image_dict = image_dict

    @property
    def image_id(self):
        """ImageId: image_id obj"""
        return self.image_dict[IMAGE_ID]

    @property
    def drawn_image_path(self):
        """str: drawn_image_path"""
        return self.image_dict.get(DRAWN_IMAGE_PATH, '')

    @property
    def detected_objects(self):
        """List[object]: List of detected objects in the image"""
        return self.image_dict.get(DETECTED_OBJECTS, [])

    @classmethod
    def from_json(cls, json_str):
        img_json_dict = json.loads(json_str)
        img_json_dict[IMAGE_ID] = ImageId.from_str(img_json_dict[IMAGE_ID])

        # serialization detected objs
        detection_method = img_json_dict.get(DETECTION_METHOD, BBOX)
        object_type = DETECTED_OBJECT_TYPE_MAPPING[detection_method]
        # TODO: consider a more general way to initialize objs
        img_json_dict[DETECTED_OBJECTS] = [
            object_type(*i) for i in img_json_dict.get(DETECTED_OBJECTS, [])]
        return cls(img_json_dict)

    def to_json_dict(self):
        """
        Returns
        -------
        image_dict: dict
            the dict repsentation of detection_result
        """
        json_dict = dict(self.image_dict)
        json_dict[IMAGE_ID] = str(json_dict[IMAGE_ID])
        return json_dict


@six.add_metaclass(ABCMeta)
class DetectionResultHandler():
    """a abstract class design to handle detection result
    need to implement:

    - function: _handle(self, detection_result)

    - property: detection_method
    """
    @abstractmethod
    def _handle(self, detection_result):
        """abstract method for handle DetectionResult

        Parameters
        ----------
        detection_result: DetectionResult
        """
        pass

    def handle(self, detection_result):
        """wrapper of _handle function with the check of detection_method with detection_result.

        Parameters
        ----------
        detection_result: DetectionResult
        """
        assert self.detection_method == detection_result.detection_method
        self._handle(detection_result)

    @property
    def detection_method(self):
        raise NotImplementedError
