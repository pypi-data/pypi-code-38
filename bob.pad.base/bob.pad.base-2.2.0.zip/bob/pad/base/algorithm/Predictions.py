from bob.pad.base.algorithm import Algorithm
import numpy


class Predictions(Algorithm):
    """An algorithm that takes the precomputed predictions and uses them for
    scoring."""

    def __init__(self, **kwargs):
        super(Predictions, self).__init__(**kwargs)

    def score(self, predictions):
        predictions = numpy.asarray(predictions)
        if predictions.size == 1:
            # output of a sigmoid binary layer
            return predictions
        # Assuming the predictions are the output of a softmax layer
        return [predictions[1]]


class VideoPredictions(Algorithm):
    """An algorithm that takes the precomputed predictions and uses them for
    scoring."""

    def __init__(self, axis=1, frame_level_scoring=False, **kwargs):
        super(VideoPredictions, self).__init__(**kwargs)
        self.frame_level_scoring = frame_level_scoring
        self.axis = axis

    def score(self, predictions):
        # Assuming the predictions are the output of a softmax layer
        predictions = predictions.as_array()[:, self.axis]

        if self.frame_level_scoring:
            return predictions
        else:
            return [numpy.mean(predictions)]
