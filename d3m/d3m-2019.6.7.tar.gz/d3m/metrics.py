import abc
import itertools
import typing

import numpy  # type: ignore
import pandas  # type: ignore
from sklearn import metrics, preprocessing  # type: ignore

from d3m import container, exceptions, utils
from d3m.metadata import problem

__ALL__ = ('class_map',)

INDEX_COLUMN = 'd3mIndex'
CONFIDENCE_COLUMN = 'confidence'

Truth = typing.TypeVar('Truth', bound=container.DataFrame)
Predictions = typing.TypeVar('Predictions', bound=container.DataFrame)


class Metric(metaclass=utils.AbstractMetaclass):
    @abc.abstractmethod
    def score(self, truth: Truth, predictions: Predictions) -> typing.Any:
        raise NotImplementedError

    @classmethod
    def align(cls, truth: Truth, predictions: Predictions) -> Predictions:
        """
        Aligns columns and rows in ``predictions`` to match those in ``truth``.

        It requires that all index values in ``truth`` are present in ``predictions``
        and only those. It requires that any column name in ``truth`` is also
        present in ``predictions``. Any additional columns present in ``predictions``
        are pushed to the right.

        Parameters
        ----------
        truth : Truth
            Truth DataFrame.
        predictions : Predictions
            Predictions DataFrame.

        Returns
        -------
        Predictions
            Predictions with aligned rows.
        """

        truth_columns_set = set(truth.columns)
        predictions_columns_set = set(predictions.columns)

        if len(truth_columns_set) != len(truth.columns):
            raise exceptions.InvalidArgumentValueError("Duplicate column names in predictions.")
        if len(predictions_columns_set) != len(predictions.columns):
            raise exceptions.InvalidArgumentValueError("Duplicate column names in predictions.")

        columns_diff = truth_columns_set - predictions_columns_set
        if columns_diff:
            raise exceptions.InvalidArgumentValueError(f"Not all columns which exist in truth exist in predictions: {sorted(columns_diff)}")

        if INDEX_COLUMN not in truth.columns:
            raise exceptions.InvalidArgumentValueError(f"Index column '{INDEX_COLUMN}' is missing in truth.")
        if INDEX_COLUMN not in predictions.columns:
            raise exceptions.InvalidArgumentValueError(f"Index column '{INDEX_COLUMN}' is missing in predictions.")

        extra_predictions_columns = [column for column in predictions.columns if column not in truth_columns_set]

        # Reorder columns.
        predictions = predictions.reindex(columns=list(truth.columns) + extra_predictions_columns)

        truth_index_set = set(truth.loc[:, INDEX_COLUMN])
        predictions_index_set = set(predictions.loc[:, INDEX_COLUMN])

        if truth_index_set != predictions_index_set:
            raise exceptions.InvalidArgumentValueError(f"Predictions and truth do not have the same set of index values.")

        truth_index_map: typing.Dict = {}
        last_index = None
        for i, index in enumerate(truth.loc[:, INDEX_COLUMN]):
            if index in truth_index_map:
                if last_index != index:
                    raise exceptions.InvalidArgumentValueError(f"Truth does not have all rows with same index value grouped together.")
            else:
                truth_index_map[index] = i
                last_index = index

        predictions_index_order = []
        for index in predictions.loc[:, INDEX_COLUMN]:
            predictions_index_order.append(truth_index_map[index])

        # Reorder rows.
        # TODO: How to not use a special column name?
        #       Currently it will fail if "__row_order__" already exists. We could set "allow_duplicates", but that would just hide
        #       the fact that we have a duplicated column. How can we then control over which one we really sort and which one we drop?
        predictions.insert(0, '__row_order__', predictions_index_order)
        predictions.sort_values(['__row_order__'], axis=0, inplace=True, kind='mergesort')
        predictions.drop('__row_order__', axis=1, inplace=True)

        return predictions

    @classmethod
    def get_target_columns(cls, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Returns only target columns present in ``dataframe``.
        """

        columns = list(dataframe.columns)

        index_columns = columns.count(INDEX_COLUMN)
        if index_columns < 1:
            raise exceptions.InvalidArgumentValueError(f"Index column '{INDEX_COLUMN}' is missing in predictions.")
        elif index_columns > 1:
            raise exceptions.InvalidArgumentValueError(f"Predictions contain multiple index columns '{INDEX_COLUMN}': {index_columns}")

        dataframe = dataframe.drop(columns=[INDEX_COLUMN])

        confidence_columns = columns.count(CONFIDENCE_COLUMN)
        if confidence_columns > 1:
            raise exceptions.InvalidArgumentValueError(f"Predictions contain multiple confidence columns '{CONFIDENCE_COLUMN}': {confidence_columns}")
        elif confidence_columns:
            dataframe = dataframe.drop(columns=[CONFIDENCE_COLUMN])

        if not len(dataframe.columns):
            raise exceptions.InvalidArgumentValueError(f"Predictions do not contain any target columns.")

        return dataframe

    @classmethod
    def get_index_column(cls, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Returns only index column present in ``dataframe``.
        """

        columns = list(dataframe.columns)

        index_columns = columns.count(INDEX_COLUMN)
        if index_columns < 1:
            raise exceptions.InvalidArgumentValueError(f"Index column '{INDEX_COLUMN}' is missing in predictions.")
        elif index_columns > 1:
            raise exceptions.InvalidArgumentValueError(f"Predictions contain multiple index columns '{INDEX_COLUMN}': {index_columns}")

        return dataframe.loc[:, [INDEX_COLUMN]]

    @classmethod
    def get_confidence_column(cls, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        """
        Returns only confidence column present in ``dataframe``.
        """

        columns = list(dataframe.columns)

        confidence_columns = columns.count(CONFIDENCE_COLUMN)
        if confidence_columns < 1:
            raise exceptions.InvalidArgumentValueError(f"Confidence column '{CONFIDENCE_COLUMN}' is missing in predictions.")
        elif confidence_columns > 1:
            raise exceptions.InvalidArgumentValueError(f"Predictions contain multiple confidence columns '{CONFIDENCE_COLUMN}': {confidence_columns}")

        return dataframe.loc[:, [CONFIDENCE_COLUMN]]


class AccuracyMetric(Metric):
    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        return metrics.accuracy_score(truth, predictions)


class PrecisionMetric(Metric):
    def __init__(self, pos_label: str) -> None:
        self.pos_label = pos_label

    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        return metrics.precision_score(truth, predictions, pos_label=self.pos_label)


class RecallMetric(Metric):
    def __init__(self, pos_label: str) -> None:
        self.pos_label = pos_label

    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        return metrics.recall_score(truth, predictions, pos_label=self.pos_label)


class F1Metric(Metric):
    def __init__(self, pos_label: str) -> None:
        self.pos_label = pos_label

    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        return metrics.f1_score(truth, predictions, pos_label=self.pos_label)


class F1MicroMetric(Metric):
    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        return metrics.f1_score(truth, predictions, average='micro')


class F1MacroMetric(Metric):
    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        return metrics.f1_score(truth, predictions, average='macro')


class MeanSquareErrorMetric(Metric):
    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        return metrics.mean_squared_error(truth, predictions)


class RootMeanSquareErrorMetric(Metric):
    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        mean_squared_error = metrics.mean_squared_error(truth, predictions, multioutput='raw_values')

        return numpy.mean(numpy.sqrt(mean_squared_error))


class MeanAbsoluteErrorMetric(Metric):
    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        return metrics.mean_absolute_error(truth, predictions)


class RSquaredMetric(Metric):
    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        return metrics.r2_score(truth, predictions)


class NormalizeMutualInformationMetric(Metric):
    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        if len(truth.columns) != 1:
            raise exceptions.InvalidArgumentValueError("Only one target column is supported.")
        if len(predictions.columns) != 1:
            raise exceptions.InvalidArgumentValueError("Only one target column is supported.")

        return metrics.normalized_mutual_info_score(truth.iloc[:, 0].ravel(), predictions.iloc[:, 0].ravel(), average_method='geometric')


class JaccardSimilarityScoreMetric(Metric):
    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        return metrics.jaccard_similarity_score(truth, predictions)


class PrecisionAtTopKMetric(Metric):
    def __init__(self, k: int) -> None:
        self.k = k

    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth = self.get_target_columns(truth)
        predictions = self.get_target_columns(predictions)

        if len(truth.columns) != 1:
            raise exceptions.InvalidArgumentValueError("Only one target column is supported.")
        if len(predictions.columns) != 1:
            raise exceptions.InvalidArgumentValueError("Only one target column is supported.")

        truth = truth.values.ravel().astype(int)
        predictions = predictions.values.ravel().astype(int)

        truth = numpy.argsort(truth)[::-1]
        predictions = numpy.argsort(predictions)[::-1]

        truth = truth[0:self.k]
        predictions = predictions[0:self.k]

        return numpy.float(len(numpy.intersect1d(truth, predictions))) / self.k


class ObjectDetectionAveragePrecisionMetric(Metric):
    def _convert_bounding_polygon_to_box_coords(self, bounding_polygon: typing.List) -> typing.List:
        # box_coords = [x_min, y_min, x_max, y_max]
        if len(bounding_polygon) != 8:
            raise exceptions.NotSupportedError("Polygon must contain eight vertices for this metric.")

        if bounding_polygon[0] != bounding_polygon[2] or bounding_polygon[4] != bounding_polygon[6]:
            raise exceptions.NotSupportedError("X coordinates in bounding box do not match.")

        if bounding_polygon[1] != bounding_polygon[7] or bounding_polygon[3] != bounding_polygon[5]:
            raise exceptions.NotSupportedError("Y coordinates in bounding box do not match.")

        box_coords = [bounding_polygon[0], bounding_polygon[1],
                      bounding_polygon[4], bounding_polygon[5]]
        return box_coords

    def _group_gt_boxes_by_image_name(self, gt_boxes: typing.List) -> typing.Dict:
        gt_dict: typing.Dict = {}

        for box in gt_boxes:
            image_name = box[0]
            bounding_polygon = box[1:]
            bbox = self._convert_bounding_polygon_to_box_coords(bounding_polygon)

            if image_name not in gt_dict.keys():
                gt_dict[image_name] = []

            gt_dict[image_name].append({'bbox': bbox})

        return gt_dict

    def _voc_ap(self, rec: numpy.ndarray, prec: numpy.ndarray) -> float:
        # First append sentinel values at the end.
        mrec = numpy.concatenate(([0.], rec, [1.]))
        mpre = numpy.concatenate(([0.], prec, [0.]))

        # Compute the precision envelope.
        for i in range(mpre.size - 1, 0, -1):
            mpre[i - 1] = numpy.maximum(mpre[i - 1], mpre[i])

        # To calculate area under PR curve, look for points
        # where X axis (recall) changes value.
        i = numpy.where(mrec[1:] != mrec[:-1])[0]

        # And sum (\Delta recall) * prec.
        ap = numpy.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])

        return float(ap)

    def _object_detection_average_precision(self, y_true: typing.List, y_pred: typing.List) -> float:
        """
        This function takes a list of ground truth bounding polygons (rectangles in this case)
        and a list of detected bounding polygons (also rectangles) for a given class and
        computes the average precision of the detections with respect to the ground truth polygons.
        Parameters:
        -----------
        y_true: list
         List of ground truth polygons. Each polygon is represented as a list of
         vertices, starting in the upper-left corner going counter-clockwise.
         Since in this case, the polygons are rectangles, they will have the
         following format:
            [image_name, x_min, y_min, x_min, y_max, x_max, y_max, x_max, y_min].
        y_pred: list
         List of bounding box polygons with their corresponding confidence scores. Each
         polygon is represented as a list of vertices, starting in the upper-left corner
         going counter-clockwise. Since in this case, the polygons are rectangles, they
         will have the following format:
            [image_name, x_min, y_min, x_min, y_max, x_max, y_max, x_max, y_min, confidence_score].
        Returns:
        --------
        ap: float
         Average precision between detected polygons (rectangles) and the ground truth polylgons (rectangles).
         (it is also the area under the precision-recall curve).
        Example 1:
        >> predictions_list_1 = [['img_00001.png', 110, 110, 110, 210, 210, 210, 210, 110, 0.6],
                                 ['img_00002.png', 5, 10, 5, 20, 20, 20, 20, 10, 0.9],
                                 ['img_00002.png', 120, 130, 120, 200, 200, 200, 200, 130, 0.6]]
        >> ground_truth_list_1 = [['img_00001.png', 100, 100, 100, 200, 200, 200, 200, 100],
                                  ['img_00002.png', 10, 10, 10, 20, 20, 20, 20, 10],
                                  ['img_00002.png', 70, 80, 70, 150, 140, 150, 140, 80]]
        >> ap_1 = object_detection_average_precision(ground_truth_list_1, predictions_list_1)
        >> print(ap_1)
        0.667
        Example 2:
        >> predictions_list_2 = [['img_00285.png', 330, 463, 330, 505, 387, 505, 387, 463, 0.0739],
                                 ['img_00285.png', 420, 433, 420, 498, 451, 498, 451, 433, 0.0910],
                                 ['img_00285.png', 328, 465, 328, 540, 403, 540, 403, 465, 0.1008],
                                 ['img_00285.png', 480, 477, 480, 522, 508, 522, 508, 477, 0.1012],
                                 ['img_00285.png', 357, 460, 357, 537, 417, 537, 417, 460, 0.1058],
                                 ['img_00285.png', 356, 456, 356, 521, 391, 521, 391, 456, 0.0843],
                                 ['img_00225.png', 345, 460, 345, 547, 415, 547, 415, 460, 0.0539],
                                 ['img_00225.png', 381, 362, 381, 513, 455, 513, 455, 362, 0.0542],
                                 ['img_00225.png', 382, 366, 382, 422, 416, 422, 416, 366, 0.0559],
                                 ['img_00225.png', 730, 463, 730, 583, 763, 583, 763, 463, 0.0588]]
        >> ground_truth_list_2 = [['img_00285.png', 480, 457, 480, 529, 515, 529, 515, 457],
                                  ['img_00285.png', 480, 457, 480, 529, 515, 529, 515, 457],
                                  ['img_00225.png', 522, 540, 522, 660, 576, 660, 576, 540],
                                  ['img_00225.png', 739, 460, 739, 545, 768, 545, 768, 460]]
        >> ap_2 = object_detection_average_precision(ground_truth_list_2, predictions_list_2)
        >> print(ap_2)
        0.125
        Example 3:
        >> predictions_list_3 = [['img_00001.png', 110, 110, 110, 210, 210, 210, 210, 110, 0.6],
                                 ['img_00002.png', 120, 130, 120, 200, 200, 200, 200, 130, 0.6],
                                 ['img_00002.png', 5, 8, 5, 16, 15, 16, 15, 8, 0.9],
                                 ['img_00002.png', 11, 12, 11, 18, 21, 18, 21, 12, 0.9]]
        >> ground_truth_list_3 = [['img_00001.png', 100, 100, 100, 200, 200, 200, 200, 100],
                                  ['img_00002.png', 10, 10, 10, 20, 20, 20, 20, 10],
                                  ['img_00002.png', 70, 80, 70, 150, 140, 150, 140, 80]]
        >> ap_3 = object_detection_average_precision(ground_truth_list_3, predictions_list_3)
        >> print(ap_3)
        0.444
        Example 4:
        (Same as example 3 except the last two box predictions in img_00002.png are switched)
        >> predictions_list_4 = [['img_00001.png', 110, 110, 110, 210, 210, 210, 210, 110, 0.6],
                                 ['img_00002.png', 120, 130, 120, 200, 200, 200, 200, 130, 0.6],
                                 ['img_00002.png', 11, 12, 11, 18, 21, 18, 21, 12, 0.9],
                                 ['img_00002.png', 5, 8, 5, 16, 15, 16, 15, 8, 0.9]]
        >> ground_truth_list_4 = [['img_00001.png', 100, 100, 100, 200, 200, 200, 200, 100],
                                  ['img_00002.png', 10, 10, 10, 20, 20, 20, 20, 10],
                                  ['img_00002.png', 70, 80, 70, 150, 140, 150, 140, 80]]
        >> ap_4 = object_detection_average_precision(ground_truth_list_4, predictions_list_4)
        >> print(ap_4)
        0.444
        """

        ovthresh = 0.5

        # y_true = typing.cast(Truth, unvectorize(y_true))
        # y_pred = typing.cast(Predictions, unvectorize(y_pred))

        # Load ground truth.
        gt_dict = self._group_gt_boxes_by_image_name(y_true)

        # Extract gt objects for this class.
        recs = {}
        npos = 0

        imagenames = sorted(gt_dict.keys())
        for imagename in imagenames:
            Rlist = [obj for obj in gt_dict[imagename]]
            bbox = numpy.array([x['bbox'] for x in Rlist])
            det = [False] * len(Rlist)
            npos = npos + len(Rlist)
            recs[imagename] = {'bbox': bbox, 'det': det}

        # Load detections.
        det_length = len(y_pred[0])

        # Check that all boxes are the same size.
        for det in y_pred:
            assert len(det) == det_length, 'Not all boxes have the same dimensions.'

        image_ids = [x[0] for x in y_pred]
        BP = numpy.array([[float(z) for z in x[1:-1]] for x in y_pred])
        BB = numpy.array([self._convert_bounding_polygon_to_box_coords(x) for x in BP])

        confidence = numpy.array([float(x[-1]) for x in y_pred])
        boxes_w_confidences_list = numpy.hstack((BB, -1 * confidence[:, None]))
        boxes_w_confidences = numpy.empty(
            (boxes_w_confidences_list.shape[0],),
            dtype=[
                ('x_min', float), ('y_min', float),
                ('x_max', float), ('y_max', float),
                ('confidence', float),
            ],
        )
        boxes_w_confidences[:] = [tuple(i) for i in boxes_w_confidences_list]

        # Sort by confidence.
        sorted_ind = numpy.argsort(
            boxes_w_confidences, kind='mergesort',
            order=('confidence', 'x_min', 'y_min', 'x_max', 'y_max'))
        BB = BB[sorted_ind, :]
        image_ids = [image_ids[x] for x in sorted_ind]

        # Go down y_pred and mark TPs and FPs.
        nd = len(image_ids)
        tp = numpy.zeros(nd)
        fp = numpy.zeros(nd)
        for d in range(nd):
            R = recs[image_ids[d]]
            bb = BB[d, :].astype(float)
            ovmax = -numpy.inf
            BBGT = R['bbox'].astype(float)

            if BBGT.size > 0:
                # Compute overlaps.
                # Intersection.
                ixmin = numpy.maximum(BBGT[:, 0], bb[0])
                iymin = numpy.maximum(BBGT[:, 1], bb[1])
                ixmax = numpy.minimum(BBGT[:, 2], bb[2])
                iymax = numpy.minimum(BBGT[:, 3], bb[3])
                iw = numpy.maximum(ixmax - ixmin + 1., 0.)
                ih = numpy.maximum(iymax - iymin + 1., 0.)
                inters = iw * ih

                # Union.
                uni = ((bb[2] - bb[0] + 1.) * (bb[3] - bb[1] + 1.) +
                       (BBGT[:, 2] - BBGT[:, 0] + 1.) *
                       (BBGT[:, 3] - BBGT[:, 1] + 1.) - inters)

                overlaps = inters / uni
                ovmax = numpy.max(overlaps)
                jmax = numpy.argmax(overlaps)

            if ovmax > ovthresh:
                if not R['det'][jmax]:
                    tp[d] = 1.
                    R['det'][jmax] = 1
                else:
                    fp[d] = 1.
            else:
                fp[d] = 1.

        # Compute precision recall.
        fp = numpy.cumsum(fp)
        tp = numpy.cumsum(tp)
        rec = tp / float(npos)
        # Avoid divide by zero in case the first detection matches a difficult ground truth.
        prec = tp / numpy.maximum(tp + fp, numpy.finfo(numpy.float64).eps)
        ap = self._voc_ap(rec, prec)

        return ap

    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth_index = self.get_index_column(truth)
        truth_targets = self.get_target_columns(truth)

        if len(truth_targets.columns) != 1:
            raise NotImplementedError("Support for multiple target columns is not yet implemented.")

        truth_list = []
        for i, (index, target) in enumerate(pandas.concat([truth_index, truth_targets], axis=1).itertuples(index=False, name=None)):
            truth_list.append([index] + [float(v) for v in target.split(',')])

        predictions_index = self.get_index_column(predictions)
        predictions_targets = self.get_target_columns(predictions)
        predictions_confidence = self.get_confidence_column(predictions)

        if len(predictions_targets.columns) != 1:
            raise NotImplementedError("Support for multiple target columns is not yet implemented.")

        predictions_list = []
        for i, (index, target, confidence) in enumerate(pandas.concat([predictions_index, predictions_targets, predictions_confidence], axis=1).itertuples(index=False, name=None)):
            predictions_list.append([index] + [float(v) for v in target.split(',')] + [float(confidence)])

        return self._object_detection_average_precision(truth_list, predictions_list)


class HammingLossMetric(Metric):
    """
    Hamming loss gives the percentage of wrong labels to the total number of labels.
    Lower the hamming loss, better is the performance of the method used.
    Hamming loss is used as a performance metric for multi-label classification problems.
    """

    def _index_to_values(self, dataframe: pandas.DataFrame) -> typing.Tuple[typing.List, typing.List]:
        index_to_values: typing.Dict = {}

        for index, value in dataframe.itertuples(index=False, name=None):
            if index in index_to_values:
                index_to_values[index].append(value)
            else:
                index_to_values[index] = [value]

        return list(index_to_values.keys()), list(index_to_values.values())

    def score(self, truth: Truth, predictions: Predictions) -> float:
        predictions = self.align(truth, predictions)

        truth_index = self.get_index_column(truth)
        truth_targets = self.get_target_columns(truth)

        if len(truth_targets.columns) != 1:
            raise exceptions.NotSupportedError("Multiple target columns are not supported.")

        predictions_index = self.get_index_column(predictions)
        predictions_targets = self.get_target_columns(predictions)

        if len(predictions_targets.columns) != 1:
            raise exceptions.NotSupportedError("Multiple target columns are not supported.")

        (truth_keys, truth_values) = self._index_to_values(pandas.concat([truth_index, truth_targets], axis=1))
        (predictions_keys, predictions_values) = self._index_to_values(pandas.concat([predictions_index, predictions_targets], axis=1))

        # Dicts maintain insertion order, so the list of keys is list of indices which should be aligned.
        assert truth_keys == predictions_keys

        truth_classes = set(itertools.chain.from_iterable(truth_values))
        predictions_classes = set(itertools.chain.from_iterable(predictions_values))

        all_classes = sorted(truth_classes.union(predictions_classes))

        label_binarizer = preprocessing.MultiLabelBinarizer(classes=all_classes)

        truth_label_encoded = label_binarizer.fit_transform(truth_values)
        predictions_label_encoded = label_binarizer.transform(predictions_values)

        return metrics.hamming_loss(truth_label_encoded, predictions_label_encoded)


class_map: typing.Dict[problem.PerformanceMetricBase, Metric] = {
    problem.PerformanceMetric.ACCURACY: AccuracyMetric,
    problem.PerformanceMetric.PRECISION: PrecisionMetric,
    problem.PerformanceMetric.RECALL: RecallMetric,
    problem.PerformanceMetric.F1: F1Metric,
    problem.PerformanceMetric.F1_MICRO: F1MicroMetric,
    problem.PerformanceMetric.F1_MACRO: F1MacroMetric,
    problem.PerformanceMetric.MEAN_SQUARED_ERROR: MeanSquareErrorMetric,
    problem.PerformanceMetric.ROOT_MEAN_SQUARED_ERROR: RootMeanSquareErrorMetric,
    problem.PerformanceMetric.MEAN_ABSOLUTE_ERROR: MeanAbsoluteErrorMetric,
    problem.PerformanceMetric.R_SQUARED: RSquaredMetric,
    problem.PerformanceMetric.NORMALIZED_MUTUAL_INFORMATION: NormalizeMutualInformationMetric,
    problem.PerformanceMetric.JACCARD_SIMILARITY_SCORE: JaccardSimilarityScoreMetric,
    problem.PerformanceMetric.PRECISION_AT_TOP_K: PrecisionAtTopKMetric,
    problem.PerformanceMetric.OBJECT_DETECTION_AVERAGE_PRECISION: ObjectDetectionAveragePrecisionMetric,
    problem.PerformanceMetric.HAMMING_LOSS: HammingLossMetric,
}
