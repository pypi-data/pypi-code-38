import six
from abc import ABCMeta, abstractmethod
from eyewitness.config import BBOX


@six.add_metaclass(ABCMeta)
class ObjectClassifier():
    """
    Abstract class used to wrapper object detector
    """
    @abstractmethod
    def detect(self, image_obj, bbox_objs=None):
        """
        [abstract method] need to implement detection method which return DetectionResult obj

        Parameters
        ----------
        image_obj: eyewitness.image_util.Image

        bbox_objs: Optional[List[BoundedBoxObject]]

        Returns
        -------
        DetectionResult: DetectionResult
            the detected result of given image

            if bbox_objs not given:
                -> classify whole image, and result in DETECTED_OBJECTS (length 1)
            if bbox_objs given:
                -> classify List of bbox_objs, and return valid label objs in DetectionResult

        # TODO: need to consider a more proper design
        """
        pass

    @property
    def detection_method(self):
        """
        detection_method for the ObjectDetector is BBOX

        Returns
        -------
        detection_method: String
        """
        return BBOX

    @property
    def valid_labels(self):
        """
        [abstract property] the valid_labels of this detector e.g. set(['person', 'pikachu' ...])
        this will be used while want to evaluation the detector

        Returns
        -------
        valid_labels: set[String]
        """
        raise NotImplementedError
