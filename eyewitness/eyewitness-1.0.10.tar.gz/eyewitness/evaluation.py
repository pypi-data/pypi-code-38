from abc import ABCMeta, abstractmethod
from collections import defaultdict

from eyewitness.config import (
    BBOX,
    DATASET_TEST_ONLY,
)
from eyewitness.utils import bbox_intersection_over_union
import logging
import six
import numpy as np

LOG = logging.getLogger(__name__)


@six.add_metaclass(ABCMeta)
class Evaluator():
    @property
    def evaluation_method(self):
        raise NotImplementedError

    def evaluate(self, detector, dataset):
        # do the type check.
        assert all(_type == self.evaluation_method
                   for _type in [detector.detection_method, dataset.dataset_type])
        return self._evaluate(detector, dataset)

    @abstractmethod
    def _evaluate(self, detector, dataset):
        pass


class BboxMAPEvaluator(Evaluator):
    """
    evaluate the bbox mAP score
    """
    def __init__(self, iou_threshold=0.5, dataset_mode=DATASET_TEST_ONLY, logging_frequency=100):
        self.iou_threshold = iou_threshold
        self.dataset_mode = dataset_mode
        self.logging_frequency = logging_frequency

    @property
    def evaluation_method(self):
        return BBOX

    def _evaluate(self, detector, dataset):
        """
        Parameters
        ----------
        detector: ObjectDetector
            object detector instance

        dataset: BboxDataSet
            BboxDataSet instance

        Returns
        -------
        eval_result: Dict
            - mAP: mAP score
            - ap_stats: ap_stats
        """
        # only calculate on overlapped labels
        valid_labels = detector.valid_labels.intersection(dataset.valid_labels)
        if not valid_labels:
            raise ValueError('no valid labels can used for evaluation')

        selected_images = dataset.get_selected_images(mode=self.dataset_mode)
        n_images = len(selected_images)

        # forward all images, and collect all ground truth from dataset
        detected_objs = defaultdict(list)
        gt_objs = defaultdict(lambda: defaultdict(list))
        gt_label_count = defaultdict(int)
        processed_image_count = 0
        for image_obj, image_gt_objs in dataset.dataset_iterator(mode=self.dataset_mode):
            processed_image_count += 1
            if processed_image_count % self.logging_frequency == 0:
                LOG.info('processed images %d/%d', processed_image_count, n_images)

            detection_result = detector.detect(image_obj)
            for obj in detection_result.detected_objects:
                if obj.label not in valid_labels:
                    continue
                detected_objs[obj.label].append((image_obj.image_id, obj))

            # stores gt information into gt_objs and gt_label_count
            image_gt_objs = [image_gt_obj for image_gt_obj in
                             image_gt_objs if image_gt_obj.label in valid_labels]
            for image_gt_obj in image_gt_objs:
                gt_objs[image_obj.image_id][image_gt_obj.label].append(image_gt_obj)
                gt_label_count[image_gt_obj.label] += 1

        ap_stats = self.calculate_label_ap(valid_labels, detected_objs, gt_objs, gt_label_count)
        mAP = np.mean(list(i['AP'] for i in ap_stats.values()))
        return {'mAP': mAP, 'ap_stats': ap_stats}

    def calculate_label_ap(self, valid_labels, detected_objs, gt_objs, gt_label_count):
        """
        refactor the evaluation from
        https://github.com/rafaelpadilla/Object-Detection-Metrics
        """
        ap_stat = {}

        for label in valid_labels:  # loop each label
            n_positives = gt_label_count[label]
            sorted_label_det_objs = sorted(
                detected_objs[label], key=lambda x: x[1].score, reverse=True)
            TP = np.zeros(len(sorted_label_det_objs))
            FP = np.zeros(len(sorted_label_det_objs))

            for det_idx, (image_id, label_obj) in enumerate(sorted_label_det_objs):
                # find label gt truth image obj
                if image_id not in gt_objs:
                    gt_label_objs = []
                else:
                    gt_label_objs = gt_objs[image_id][label]

                # get the max_iou
                best_iou = 0
                best_iou_gt_idx = -1
                for gt_idx, gt_label_obj in enumerate(gt_label_objs):
                    det_bbox = label_obj[:4]  # x1, y1, x2, y2
                    gt_bbox = gt_label_obj[:4]  # x1, y1, x2, y2
                    iou = bbox_intersection_over_union(det_bbox, gt_bbox)
                    if iou > best_iou:
                        best_iou_gt_idx = gt_idx
                        best_iou = iou

                if best_iou >= self.iou_threshold:
                    TP[det_idx] = 1
                    # remove the matched gt obj from this image
                    gt_objs[image_id][label] = (gt_label_objs[:best_iou_gt_idx]
                                                + gt_label_objs[(best_iou_gt_idx + 1):])
                else:
                    FP[det_idx] = 1

            acc_FP = np.cumsum(FP)
            acc_TP = np.cumsum(TP)
            recall = acc_TP / n_positives
            precision = np.divide(acc_TP, (acc_FP + acc_TP))
            ap, mpre, mrec, _ = BboxMAPEvaluator.calculate_average_precision(recall, precision)

            ap_stat[label] = {
                'precision': precision,
                'recall': recall,
                'AP': ap,
                'interpolated precision': mpre,
                'interpolated recall': mrec,
                'total positives': n_positives,
                'total TP': np.sum(TP),
                'total FP': np.sum(FP)
            }
            LOG.info('ap calculated for %s: %s', label, ap_stat[label]['AP'])
        return ap_stat

    @staticmethod
    def calculate_average_precision(recall, precision):
        mrec = []
        mrec.append(0)
        [mrec.append(e) for e in recall]
        mrec.append(1)
        mpre = []
        mpre.append(0)
        [mpre.append(e) for e in precision]
        mpre.append(0)
        for i in range(len(mpre) - 1, 0, -1):
            mpre[i - 1] = max(mpre[i - 1], mpre[i])
        ii = []
        for i in range(len(mrec) - 1):
            if mrec[1:][i] != mrec[0:-1][i]:
                ii.append(i + 1)
        ap = 0
        for i in ii:
            ap = ap + np.sum((mrec[i] - mrec[i - 1]) * mpre[i])
        # return [ap, mpre[1:len(mpre)-1], mrec[1:len(mpre)-1], ii]
        return [ap, mpre[0:len(mpre) - 1], mrec[0:len(mpre) - 1], ii]
