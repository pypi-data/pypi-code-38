# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""create a pipeline capable of supporting the operations like train, transform and predict."""
from typing import Any, Dict
from enum import Enum
from uuid import uuid4
import warnings

from sklearn.pipeline import Pipeline

from .forecasting_constants import Telemetry
from automl.client.core.common.forecasting_exception import (AzureMLForecastException,
                                                             PipelineException)
from automl.client.core.common.forecasting_verify import Messages
from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame

_can_use_core_telemetry = False  # TODO: enable client core logger


class AzureMLForecastPipelineExecutionType(Enum):
    """Enums representing execution types."""

    transforms = 1
    fit = 2
    fit_predict = 3
    fit_transform = 4
    predict = 5
    predict_proba = 6
    predict_log_proba = 7
    decision_function = 8
    score = 9


class AzureMLForecastPipeline:
    """
    Pipeline class for Azure Machine Learning Package For Forecasting.

    .. py:class:: AzureMLForecastPipeline
    Encapsulates the sklearn pipeline and exposes methods to execute
    pipeline steps and retrieve execution metrics.

    sklearn.pipeline.Pipeline: http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html

    :param steps:
        List of (name, transformer/estimator) tuples (implementing
        fit/transform) that are chained, in the order in which they are
        chained, with the last object an estimator.
        Transformers must be a subclass of
        :class:`ftk.transforms.sklearn_transformer_wrapper.AzureMLForecastTransformerBase`,
        Estimators must be a
        :class:`ftk.models.regression_forecaster.RegressionForecaster`, or a subclass of
        :class:`ftk.models.recursive_forecaster.RecursiveForecaster`.
    :type steps:
        list of (string, transformer/estimator)
    """

    def __init__(self, steps=None, **kwargs):
        """Create an AzureMLForecastPipeline."""
        # Hold a reference to the steps. We might
        # do something with these...
        self._steps = steps

        # Compose the sklearn pipeline.
        self._pipeline = Pipeline(self._steps)

        # Set all **kwargs on sklearn pipeline
        self._pipeline.set_params(**kwargs)

        # Do logging if we can use the common package
        self._logging_on = _can_use_core_telemetry

        self._pipeline_id = str(uuid4())

    def add_pipeline_step(self, name, step, prepend=False):
        """
        Add a pipeline step.

        .. py:method:: AzureMLForecastPipeline.add_pipeline_step
        Append a new step at the end of a pipeline or prepend a new step at
        the beginning if prepend is set to ```True```.

        :param name:
            Name of the new step.
        :type name: str

        :param step:
            New step, transformer or estimator, to add to the pipeline. An
            estimator can only be added when the pipeline doesn't contain an
            estimator already. If you want to have multiple estimators in
            one pipeline, use
            :class:`ftk.models.forecaster_union.ForecasterUnion`.
        :type step:
            :class:`ftk.transforms.sklearn_transformer_wrapper.AzureMLForecastTransformerBase`,
            :class:`ftk.models.regression_forecaster.RegressionForecaster`,
            or a subclass of :class:`ftk.models.recursive_forecaster.RecursiveForecaster`.

        :param prepend:
            If True, insert the new step at the beginning of the pipeline.
            Otherwise, append the new step at the end of the pipeline.
        :type prepend: boolean

        :return: None
        """
        if next((step for key, step in self._pipeline.steps if key == name),
                None) is None:
            if prepend:
                self._pipeline.steps.insert(0, (name, step))
            else:
                self._pipeline.steps.append((name, step))
            self.validate_pipeline()
        else:
            raise AzureMLForecastException(Messages.PIPELINE_STEP_ADD_INVALID)

    def remove_pipeline_step(self, name):
        """
        Remove an existing step from the pipeline.

        .. py:method:: AzureMLForecastPipeline.remove_pipeline_step

        :param name:
            Name of the step to remove.
        :type name: str

        :return: None
        """
        if next((step for key, step in self._pipeline.steps if key == name),
                None) is not None:
            self._pipeline.steps[:] = [(key, step) for key, step in
                                       self._pipeline.steps if not key == name]
            self.validate_pipeline()
        else:
            raise AzureMLForecastException(
                Messages.PIPELINE_STEP_REMOVE_INVALID)

    def get_pipeline_params(self, deep=True):
        """
        Get pipeline parameters.

        .. py:method:: AzureMLForecastPipeline.get_pipeline_params

        :param deep:
            If True, will return the parameters for transformers/estimators
            and contained subobjects that are transformers/estimators.
        :type deep: boolean

        :return: Parameter names mapped to their values.
        :rtype: mapping of string to any
        """
        return self._pipeline.get_params(deep)

    def get_params(self, deep=True):
        """
        Get pipeline parameters.

        .. py:method:: AzureMLForecastPipeline.get_params

        sklearn.pipeline.Pipeline.get_params:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline.get_params

        :param deep:
            If True, will return the parameters for transformers/estimators
            and contained subobjects that are transformers/estimators.
        :type deep: boolean

        :return: Parameter names mapped to their values.
        :rtype: mapping of string to any
        """
        return self.get_pipeline_params(deep=deep)

    def set_pipeline_params(self, **kwargs):
        """
        Set the parameters of transformers and estimators in the pipeline.

        .. py:method:: AzureMLForecastPipeline.set_pipeline_params

        sklearn.pipeline.Pipeline.set_params:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline.set_params

        """
        self._pipeline.set_params(**kwargs)

    def validate_pipeline(self):
        """
        Validate pipeline step names.

        .. py:method:: AzureMLForecastPipeline.validate_pipeline

        Check if the transformers and estimators in the pipeline implement
        the required fit and transform methods.
        """
        try:
            if self._steps is None:
                raise PipelineException(Messages.PIPELINE_INVALID)
            self._pipeline._validate_steps()
        except ValueError as val_error:
            raise PipelineException(Messages.PIPELINE_INVALID) from val_error
        except TypeError as type_error:
            raise PipelineException(Messages.PIPELINE_INVALID) from type_error

    def get_pipeline_step(self, name):
        """
        Return a pipeline step object by name.

        .. py:method:: AzureMLForecastPipeline.get_pipeline_step

        :param name: Name of the step to return.
        :type name: str

        :return: The step object corresponding the given step name.
        """
        # steps is a list containing a dictionary. The dictionary has a key that is the name and
        # and an object. We are returning an the step object's generator
        return next((step for key, step in self._pipeline.steps if key == name), None)

    def execute_pipeline_op(self, execution_type, X, y=None, sample_weight=None, **fit_params):
        """
        Execute the pipeline based on the execution type specified.

        1. Calling this method with a {fit*} execution type results in:
            a. Fit method invocation on all but last estimator step
            b. Invocation of a method with the same name as the execution_type
            on the last estimator step

        1. Calling this method with a {predict*} execution type results in:
            a. Transform method invocation on all but last estimator step
            b. Invocation of a method with the same name as the execution_type
            on the last estimator step

        :param execution_type:
            Pipeline operation to execute. Supports most operations of the
            sklearn pipeline.
        :type execution_type: AzureMLForecastPipelineExecutionType.

        :param X:
            Input data for training, prediction, or transformation,
            depending on the execution type.
        :type X:
            :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`,
            or :class:`ftk.forecast_data_frame.ForecastDataFrame`

        :param y:
            Target values for model training or scoring.
        :type y: Iterable

        :param sample_weight:
            If not None, this argument is passed as ```sample_weight```
            keyword argument to the ```score``` method of the final estimator.
        :type sample_weight: array-like

        :return:
            Fitted pipeline, transformed data, prediction result,
            or scoring result, depending on ```execution_type```
        """
        # Check execution type
        if execution_type is None or not isinstance(execution_type, AzureMLForecastPipelineExecutionType):
            raise PipelineException(Messages.PIPELINE_EXECUTION_TYPE_INVALID)

        # TODO: enable client core logger
        if self._logging_on:
            # Create local logger, but do not hardcode the logging level here
            # so that it inherits the global logging level from the root
            # logger, which is user-set
            # Setting the pipeline and run ID only make sense if logging is on.
            run_id = str(uuid4())
            self._set_run_id_maybe(run_id)
            self._set_pipeline_id_maybe()

            # program_name = 'pipeline {0}'.format(execution_type.name)
            # activity = 'pipeline.{}'.format(execution_type.name)
            telemetry_values = self._get_telemetry_values(execution_type, X, sample_weight, **fit_params)
            telemetry_values[Telemetry.TELEMETRY_RUN_ID] = run_id
            # start_time = logger.log_start(activity, program_name, telemetry_values)

        # Get hold of the last step.
        last_step = self._pipeline._final_estimator
        if last_step is None:
            raise PipelineException(Messages.PIPELINE_FINAL_ESTIMATOR_INVALID)

        # A compact if not giant chunck that models all pipeline execution types.
        if execution_type == AzureMLForecastPipelineExecutionType.fit:
            """ """
            Xt, fit_params = self.__execute_pipeline__preprocess_fit(X, y, **fit_params)
            if last_step is not None:
                last_step.fit(Xt, y, **fit_params)

            res = self

        elif execution_type == AzureMLForecastPipelineExecutionType.fit_transform:
            Xt, fit_params = self.__execute_pipeline__preprocess_fit(X, y, **fit_params)
            if last_step is not None:
                if hasattr(last_step, 'fit_transform'):
                    res = last_step.fit_transform(Xt, y, **fit_params)
                else:
                    res = last_step.fit(Xt, y, **fit_params).transform(Xt)
            else:
                res = Xt

        elif execution_type == AzureMLForecastPipelineExecutionType.predict:
            Xt = self.__execute_pipeline__preprocess_transforms(X)
            try:
                res = last_step.predict(Xt, **fit_params)
            except TypeError as e:
                warnings.warn('The estimator does not seem to like kwargs: ' + str(e))
                res = last_step.predict(Xt)

        elif execution_type == AzureMLForecastPipelineExecutionType.fit_predict:
            Xt, fit_params = self.__execute_pipeline__preprocess_fit(X, y, **fit_params)
            res = last_step.fit_predict(Xt, y, **fit_params)

        elif execution_type == AzureMLForecastPipelineExecutionType.predict_proba:
            Xt = self.__execute_pipeline__preprocess_transforms(X)
            res = last_step.predict_proba(Xt, **fit_params)

        elif execution_type == AzureMLForecastPipelineExecutionType.predict_log_proba:
            Xt = self.__execute_pipeline__preprocess_transforms(X)
            res = last_step.predict_log_proba(Xt, **fit_params)

        elif execution_type == AzureMLForecastPipelineExecutionType.decision_function:
            Xt = self.__execute_pipeline__preprocess_transforms(X)
            res = last_step.decision_function(Xt)

        elif execution_type == AzureMLForecastPipelineExecutionType.transforms:
            Xt = self.__execute_pipeline__preprocess_transforms(X)
            if last_step is not None:
                if hasattr(last_step, 'transform'):
                    Xt = last_step.transform(Xt)
            res = Xt

        elif execution_type == AzureMLForecastPipelineExecutionType.score:
            Xt = self.__execute_pipeline__preprocess_transforms(X)

            # Check if sample weight is present already
            if sample_weight is not None:
                last_step_name = self._steps[-1][0]   # -1 is the last step, the name is the 0th element of the tuple
                last_step_sample_weight = last_step_name + '__' + 'sample_weight'
                if last_step_sample_weight in fit_params:
                    warnings.warn("The scoring step already contains a sample_weight parameter")

            res = last_step.score(Xt, y, sample_weight)

        else:

            res = PipelineException(Messages.PIPELINE_INVALID)

        # TODO: enable client core logger
        if self._logging_on:
            telemetry_values = self._get_telemetry_values(execution_type, X, sample_weight, **fit_params)

        return res

    def __execute_pipeline__preprocess_transforms(self, X):
        """Private method that runs transform on all but last step in the pipeline."""
        Xt = X
        for name, transform in self._pipeline.steps[:-1]:
            if transform is not None:
                Xt = transform.transform(Xt)
        return Xt

    def __execute_pipeline__preprocess_fit(self, X, y=None, **fit_params):
        """Async method that runs fit on all but last step in the pipeline."""
        return self._pipeline._fit(X, y, **fit_params)

    # Executing pipeline functions by name

    def fit(self, X, y=None, **fit_params):
        """
        Fit the transformers then run fit.

        .. py:method:: AzureMLForecastPipeline.fit
        Fit all the transforms one after another and transform the data,
        then fit the transformed data using the final estimator.
        When y is ```None``` and X is a TimeSeriesDataFrame, the ```ts_vallue_colname```
        column of X is used as the target column.

        sklearn.pipeline.Pipeline.fit:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline.fit

        :param X:
            Training data. Must fulfill input requirements of the
            first step of the pipeline.
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :param y:
            Training target. Must fulfill label requirements for all steps of
            the pipeline.
        :type y: Iterable.

        :return: Fitted pipeline.
        :rtype: AzureMLForecastPipeline
        """
        if (y is None) and (isinstance(X, TimeSeriesDataFrame)):
            y = X[X.ts_value_colname]

        res = self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.fit,
                                       X, y, sample_weight=None, **fit_params)

        return res

    def fit_transform(self, X, y=None, **fit_params):
        """
        Fit the transformers then run fit_transform.

        .. py:method:: AzureMLForecastPipeline.fit_transform
        Fits all the transforms one after another and transforms the data,
        then applies the ```fit_transform``` method of the final estimator on
        transformed data.
        When y is ```None``` and X is a TimeSeriesDataFrame, the ```ts_vallue_colname```
        column of X is used as the target column.

        sklearn.pipeline.Pipeline.fit_transform:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline.fit_transform

        :param X:
            Training data. Must fulfill input requirements of the
            first step of the pipeline.
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :param y:
            Training target. Must fulfill label requirements for all steps of
            the pipeline.
        :type y: Iterable.

        :return: Transformed samples.
        :rtype: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        """
        if (y is None) and (isinstance(X, TimeSeriesDataFrame)):
            y = X.ts_value

        return self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.fit_transform,
                                        X, y, sample_weight=None, **fit_params)

    def fit_predict(self, X, y=None, **fit_params):
        """
        Fit the transformers then run fit_predict.

        .. py:method:: AzureMLForecastPipeline.fit_predict
        Applies ```fit_transforms``` of a pipeline to the data, followed by the
        ```fit_predict``` method of the final estimator in the pipeline.
        Valid only if the final estimator implements fit_predict.
        When y is ```None``` and X is a TimeSeriesDataFrame, the ```ts_vallue_colname```
        column of X is used as the target column.

        sklearn.pipeline.Pipeline.fit_predict:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline.fit_predict

        :param X:
            Training data. Must fulfill input requirements of the
            first step of the pipeline.
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :param y:
            Training target. Must fulfill label requirements for all steps of
            the pipeline. default=None.
        :type y: Iterable

        :return: Prediction result on training data.
        :rtype: :class:`ftk.forecast_data_frame.ForecastDataFrame`
        """
        if (y is None) and (isinstance(X, TimeSeriesDataFrame)):
            y = X.ts_value

        return self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.fit_predict,
                                        X, y, sample_weight=None, **fit_params)

    def predict(self, X, **predict_params):
        """
        Apply transforms to the data, and predict with the final estimator.

        .. py:method:: AzureMLForecastPipeline.predict

        sklearn.pipeline.Pipeline.predict:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline.predict

        :param X:
            Data to predict on. Must fulfill input requirements of first
            step of the pipeline.
        :type X:
            :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`,
            or :class:`ftk.forecast_data_frame.ForecastDataFrame`

        :return: Prediction results on input data.
        :rtype: :class:`ftk.forecast_data_frame.ForecastDataFrame`
        """
        return self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.predict,
                                        X, y=None, sample_weight=None, **predict_params)

    def predict_proba(self, X, **predict_params):
        """
        Apply transforms, and predict_proba of the final estimator.

        .. py:method:: AzureMLForecastPipeline.predict_proba

        sklearn.pipeline.Pipeline.predict_proba:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline.predict_proba

        :param X:
            Data to predict on. Must fulfill input requirements of first
            step of the pipeline.
        :type X:
            :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`,
            or :class:`ftk.forecast_data_frame.ForecastDataFrame`

        :return: Prediction results on input data.
        :rtype: :class:`ftk.forecast_data_frame.ForecastDataFrame`
        """
        return self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.predict_proba,
                                        X, y=None, sample_weight=None, **predict_params)

    def predict_log_proba(self, X, **predict_params):
        """
        Apply transforms, and predict_log_proba of the final estimator.

        .. py:method:: AzureMLForecastPipeline.predict_log_proba

        sklearn.pipeline.Pipeline.predict_log_proba:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline.predict_log_proba

        :param X:
            Data to predict on. Must fulfill input requirements of first
            step of the pipeline.
        :type X:
            :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`,
            or :class:`ftk.forecast_data_frame.ForecastDataFrame`

        :return: Prediction results on input data.
        :rtype: :class:`ftk.forecast_data_frame.ForecastDataFrame`
        """
        return self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.predict_log_proba,
                                        X, y=None, sample_weight=None, **predict_params)

    def score(self, X, y=None, sample_weight=None):
        """
        Apply transforms, and score with the final estimator.

        .. py:method:: AzureMLForecastPipeline.score

        sklearn.pipeline.Pipeline.score:
        http://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html#sklearn.pipeline.Pipeline.score

        :param X:
            Data to predict on. Must fulfill input requirements of first
            step of the pipeline.
        :type X:
            :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`,
            or :class:`ftk.forecast_data_frame.ForecastDataFrame`

        :param y:
            Targets used for scoring. Must fulfill label requirements
            of all steps in the pipeline.
        :type y: Iterable

        :param sample_weight:
            If not None, this argument is passed as ```sample_weight```
            keyword argument to the ```score``` method of the final estimator.
        :type sample_weight: array-like

        :return: Model scoring result.
        :rtype: float
        """
        return self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.score,
                                        X, y, sample_weight=sample_weight)

    def transform(self, X):
        """
        Apply transforms of all steps to the input data.

        .. py:method:: AzureMLForecastPipeline.transform

        :param X:
            Data to transform. Must fulfill input requirements of first
            step of the pipeline.
        :type X: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`

        :return: Transformed data.
        :rtype: :class:`ftk.time_series_data_frame.TimeSeriesDataFrame`
        """
        return self.execute_pipeline_op(AzureMLForecastPipelineExecutionType.transforms,
                                        X, y=None, sample_weight=None)

    def _get_telemetry_values(self, execution_type, X, sample_weight, **fit_params):
        telemetry_values = {}   # type: Dict[str, Any]
        telemetry_values[Telemetry.TELEMETRY_COMPONENT] = 'forecastingPipeline'
        telemetry_values[Telemetry.TELEMETRY_FUNCION] = execution_type.name
        telemetry_values[Telemetry.TELEMETRY_PIPELINE_STEPS] = [step[0] for step in self._steps]
        telemetry_values[Telemetry.TELEMETRY_PIPELINE_STEP_NUM] = len(self._steps)
        telemetry_values[Telemetry.TELEMETRY_PIPELINE_SAMPLE_WEIGHT] = sample_weight
        telemetry_values[Telemetry.TELEMETRY_PIPELINE_ID] = self._pipeline_id
        if X is not None:
            telemetry_values[Telemetry.TELEMETRY_NUM_ROWS] = X.shape[0]
        if isinstance(X, TimeSeriesDataFrame):
            telemetry_values[Telemetry.TELEMETRY_TIME_COLUMN] = X.time_colname
            if X.grain_colnames:
                telemetry_values[Telemetry.TELEMETRY_GRAIN_COLUMNS] = ', '.join(X.grain_colnames)
            if X.origin_time_colname:
                telemetry_values[Telemetry.TELEMETRY_ORIGIN_COLUMN] = X.origin_time_colname
            if X.ts_value_colname:
                telemetry_values[Telemetry.TELEMETRY_TARGET_COLUMN] = X.ts_value_colname
            if X.group_colnames:
                telemetry_values[Telemetry.TELEMETRY_GROUP_COLUMNS] = ', '.join(X.group_colnames)
            telemetry_values[Telemetry.TELEMETRY_DATA_COLUMNS] = ', '.join([X.time_colname] + list(X.columns.values))
        for key in dict(fit_params).keys():
            telemetry_values[key] = str(fit_params[key])
        return telemetry_values

    def _set_run_id_maybe(self, run_id):
        """
        Set the pipeline_run_id on all the pipeline steps of AzureMLForecastEstimatorBase type.

        :param run_id: The run ID.
        :type run_id: str
        """
        for step in self._steps:
            if hasattr(step[1], 'pipeline_run_id'):
                step[1].pipeline_run_id = run_id

    def _set_pipeline_id_maybe(self):
        """Set the pipeline_id on all the pipeline steps of AzureMLForecastEstimatorBase type."""
        for step in self._steps:
            if hasattr(step[1], 'pipeline_id'):
                step[1].pipeline_id = self._pipeline_id
