import six
import logging
from abc import ABCMeta, abstractmethod
from collections import defaultdict

import arrow
from eyewitness.models.db_proxy import DATABASE_PROXY
from eyewitness.models.detection_models import BboxDetectionResult
from eyewitness.models.feedback_models import FalseAlertFeedback
from eyewitness.config import (
    BBOX,
    BoundedBoxObject,
    DETECTED_OBJECTS
)

from eyewitness.utils import bbox_intersection_over_union

LOG = logging.getLogger(__name__)


@six.add_metaclass(ABCMeta)
class DetectionResultFilter():
    @property
    def detection_method(self):
        raise NotImplementedError

    def apply(self, detection_result):
        assert self.detection_method == detection_result.detection_method
        return self._apply(detection_result)

    @abstractmethod
    def _apply(self, detection_result):
        """
        Parameters
        ----------
        detection_result: DetectionResult

        Retruns
        -------
        filtered_detection_result: DetectionResult
        """


class FeedbackBboxDeNoiseFilter(DetectionResultFilter):
    def __init__(self, database, decay=0.9, iou_threshold=0.7, collect_feedback_period=172800,
                 detection_threshold=0.5, time_check_period=None):
        """
        a Bbox DeNoise filter, which will read false alert bbox from tables:
        FalseAlertFeedback, BboxDetectionResult, and apply filter onto the detection result
        """
        self.database = database
        self.decay = decay
        self.iou_threshold = iou_threshold
        self.collect_feedback_period = collect_feedback_period
        if time_check_period is None:
            self.time_check_period = collect_feedback_period * 0.005
        else:
            self.time_check_period = time_check_period

        DATABASE_PROXY.initialize(self.database)
        # the FalseAlertFeedback, BboxDetectionResult table must exist in same database
        FalseAlertFeedback.create_table()
        BboxDetectionResult.create_table()

        # get the false alert feedbacks
        self.collect_feedback_water_mark = None
        self.update_false_alert_feedback_bbox()
        self.detection_threshold = detection_threshold

    @property
    def detection_method(self):
        """
        detection_method: String
            BBOX
        """
        return BBOX

    def _apply(self, detection_result):
        """
        using the false-alert feedback msgs to de-noise the detection result

        loop over false-alert objects related to (channel, classes),
        if any detected object matched false alert object with iou > iou_threshold:
            `object_score *= decay`
        """
        # try to collect latest false alert feedback
        self.update_false_alert_feedback_bbox()

        # verify if all detected objs having enough confidence.
        passed_objs = []
        channel = detection_result.image_id.channel
        detected_objs = detection_result.image_dict.get(DETECTED_OBJECTS, [])
        for detected_obj in detected_objs:
            (x1, y1, x2, y2, label, score, meta) = detected_obj
            bbox = (x1, y1, x2, y2)

            # loop over false_alert obj, decay the matched obj score
            false_alert_objs = self.false_alert_feedback_bbox.get((channel, label), [])
            for feedback_obj_bbox in false_alert_objs:
                if bbox_intersection_over_union(bbox, feedback_obj_bbox) > self.iou_threshold:
                    score *= self.decay
                    # TODO: meta should be a more flexible way
                    meta += 'decay_%s |' % (self.decay)

            if score > self.detection_threshold:
                passed_objs.append(BoundedBoxObject(x1, y1, x2, y2, label, score, meta))
        LOG.info('original: %s objs, filtered: %s objs', len(detected_objs), len(passed_objs))
        detection_result.image_dict[DETECTED_OBJECTS] = passed_objs
        return detection_result

    def update_false_alert_feedback_bbox(self):
        """
        collect_bbox_false_alert_information
        """
        self.check_proxy_db()

        now_timestamp = arrow.now().timestamp

        if self.collect_feedback_water_mark is None:
            do_update = True
        else:
            time_check = self.collect_feedback_water_mark + self.time_check_period
            do_update = now_timestamp > time_check

        if do_update:
            LOG.info('collecting latest false alert feedback')
            self.collect_feedback_water_mark = arrow.now().timestamp
            start_time = now_timestamp - self.collect_feedback_period
            query = FalseAlertFeedback.select().where(FalseAlertFeedback.receive_time > start_time)
            feedback_dict = defaultdict(list)
            for feedback in query:
                image_id = feedback.image_id
                channel = image_id.channel
                detected_objs = list(
                    BboxDetectionResult.select().where(BboxDetectionResult.image_id == image_id))
                for obj in detected_objs:
                    label = obj.label
                    bbox = (obj.x1, obj.y1, obj.x2, obj.y2)
                    feedback_dict[(channel, label)].append(bbox)

            self.false_alert_feedback_bbox = feedback_dict
            for key, values in feedback_dict.items():
                LOG.info('collecting %s objects from %s', len(values), key)

    def check_proxy_db(self):
        """check if the db proxy is correct one, if not initialize again.
        """
        if not (self.database is DATABASE_PROXY.obj):
            DATABASE_PROXY.initialize(self.database)
