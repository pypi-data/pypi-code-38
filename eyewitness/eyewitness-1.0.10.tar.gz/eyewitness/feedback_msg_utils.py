import json
import six
from abc import ABCMeta, abstractmethod

from eyewitness.config import (
    FEEDBACK_NO_OBJ,
    IMAGE_ID,
    AUDIENCE_ID,
    FEEDBACK_METHOD,
    FEEDBACK_MSG_OBJS,
    RECEIVE_TIME,
    FEEDBACK_META,
    FEEDBACK_OBJECT_TYPE_MAPPING,
)
from eyewitness.image_id import ImageId
from eyewitness.audience_id import AudienceId


class FeedbackMsg(object):
    """
    represent the Feedback msg
    """
    def __init__(self, feedback_dict):
        """
        Parameters
        -----------
        feedback_dict: dict
            - audience_id: AudienceId
                the audience who feedback the msg
            - feedback_method: str
                which kind of feedback
            - image_id: ImageId
                the ImageId related to feedback
            - feedback_meta: str
                misc feedback msg
            - feedback_msg_objs: List[tuple]
                feedback objs (e.g. bboxs)
            - receive_time: int
                the timestamp receive the msg
        """
        # get feedback method
        self.feedback_method = feedback_dict.get(FEEDBACK_METHOD, FEEDBACK_NO_OBJ)
        self.feedback_dict = feedback_dict

    @property
    def image_id(self):
        """ImageId: ImageId obj"""
        return self.feedback_dict.get(IMAGE_ID)

    @property
    def audience_id(self):
        """AudienceId: AudienceId obj"""
        return self.feedback_dict[AUDIENCE_ID]

    @property
    def receive_time(self):
        """int: received timestamp"""
        return self.feedback_dict[RECEIVE_TIME]

    @property
    def feedback_msg_objs(self):
        """List[tuples]: List of msg named tuple objs"""
        return self.feedback_dict.get(FEEDBACK_MSG_OBJS, [])

    @property
    def feedback_meta(self):
        """str: feedback_meta str"""
        return self.feedback_dict.get(FEEDBACK_META)

    @property
    def is_false_alert(self):
        """bool: is false_alert or not"""
        return self.feedback_dict.get('is_false_alert', True)

    @classmethod
    def from_json(cls, json_str):
        """
        Parameters
        ----------
        json_str: str
            feedback_msg json str

        Returns
        -------
        feedback_msg_obj: FeedbackMsg
            a feedback msg instance
        """
        feedback_json_dict = json.loads(json_str)
        feedback_json_dict[AUDIENCE_ID] = AudienceId.from_str(feedback_json_dict[AUDIENCE_ID])
        if feedback_json_dict[IMAGE_ID]:
            feedback_json_dict[IMAGE_ID] = ImageId.from_str(feedback_json_dict[IMAGE_ID])

        # serialization detected objs
        if FEEDBACK_MSG_OBJS in feedback_json_dict:
            feedback_method = feedback_json_dict.get(FEEDBACK_METHOD, FEEDBACK_NO_OBJ)
            feedback_obj_type = FEEDBACK_OBJECT_TYPE_MAPPING[feedback_method]
            # TODO: consider a more general way to initialize objs
            feedback_json_dict[FEEDBACK_MSG_OBJS] = [
                feedback_obj_type(*i) for i in feedback_json_dict[FEEDBACK_MSG_OBJS]]

        return cls(feedback_json_dict)

    def to_json_dict(self):
        """
        Returns
        -------
        image_dict: dict
            the dict repsentation of detection_result
        """
        json_dict = dict(self.feedback_json_dict)
        json_dict[AUDIENCE_ID] = str(json_dict[AUDIENCE_ID])
        if json_dict[IMAGE_ID]:
            json_dict[IMAGE_ID] = str(json_dict[IMAGE_ID])
        return json_dict


@six.add_metaclass(ABCMeta)
class FeedbackMsgHandler():
    """
    Abstract class for FeedbackMsgHandler

    with a abstract method *_handle(feedback_msg)* used to handle feedback msg
    """
    def handle(self, feedback_msg):
        """
        a wrapper for *_handle(feedback_msg)* and *feedback_method* check
        """
        assert self.feedback_method == feedback_msg.feedback_method
        return self._handle(feedback_msg)

    @abstractmethod
    def _handle(self, feedback_msg):
        """
        abstract method for handle feedback_msg

        Parameters
        ----------
        feedback_msg: FeedbackMsg
        """
        pass

    @property
    def feedback_method(self):
        """str: feedback_method"""
        raise NotImplementedError
