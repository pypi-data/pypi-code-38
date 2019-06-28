from .iai import _IAI


def split_data(*args, **kwargs):
    """Split the data (`X` and `y`) into a tuple of training and testing data,
    `(X_train, y_train), (X_test, y_test)`, for a problem of type `task`.

    Julia Equivalent:
    `IAI.split_data <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.split_data>`

    Examples
    --------
    >>> split_data(task, X, *y, **kwargs)
    """
    return _IAI.split_data_convert(*args, **kwargs)


def set_rich_output_param(*args, **kwargs):
    """Sets the global rich output parameter `key` to `value`.

    Julia Equivalent:
    `IAI.set_rich_output_param! <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.set_rich_output_param!>`

    Examples
    --------
    >>> set_rich_output_param(key, value)
    """
    return _IAI.set_rich_output_param_convert(*args, **kwargs)


def get_rich_output_params(*args, **kwargs):
    """Return the current global rich output parameter settings.

    Julia Equivalent:
    `IAI.get_rich_output_params <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.get_rich_output_params>`

    Examples
    --------
    >>> get_rich_output_params()
    """
    return _IAI.get_rich_output_params_convert(*args, **kwargs)


def delete_rich_output_param(*args, **kwargs):
    """Delete the global rich output parameter `key`.

    Julia Equivalent:
    `IAI.delete_rich_output_param! <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.delete_rich_output_param!>`

    Examples
    --------
    >>> delete_rich_output_param(key)
    """
    return _IAI.delete_rich_output_param_convert(*args, **kwargs)


class Learner(object):
    """Abstract type encompassing all learners"""
    def __init__(self, jl_obj):
        self._jl_obj = jl_obj

    def __repr__(self):
        return _IAI.string(self._jl_obj)

    def fit(self, *args, **kwargs):
        """Fits a model using the parameters in learner and the data `X` and
        `y`.

        Julia Equivalent:
        `IAI.fit! <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.fit!>`

        Examples
        --------
        >>> lnr.fit(X, *y, sample_weight=None)

        Parameters
        ----------
        Refer to the documentation on
        [data preparation](@ref Data-Preparation-Guide)
        for information on how to format and supply the data.
        """
        _IAI.fit_convert(self._jl_obj, *args, **kwargs)
        return self

    def write_json(self, filename, **kwargs):
        """Write learner to `filename` in JSON format.

        Julia Equivalent:
        `IAI.write_json <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.write_json>`

        Examples
        --------
        >>> lnr.write_json(filename, **kwargs)
        """
        return _IAI.write_json_convert(filename, self._jl_obj, **kwargs)

    def get_params(self):
        """Return the value of all learner parameters.

        Julia Equivalent:
        `IAI.get_params <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.get_params>`

        Examples
        --------
        >>> lnr.get_params()
        """
        return _IAI.get_params_convert(self._jl_obj)

    def set_params(self, **kwargs):
        """Set all supplied parameters on learner.

        Julia Equivalent:
        `IAI.set_params! <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.set_params!>`

        Examples
        --------
        >>> lnr.set_params(**kwargs)
        """
        _IAI.set_params_convert(self._jl_obj, **kwargs)
        return self

    def clone(self):
        """Return an unfitted copy of the learner with the same parameters.

        Julia Equivalent:
        `IAI.clone <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.clone>`

        Examples
        --------
        >>> lnr.clone()
        """
        # Copy the object
        import copy
        lnr = copy.copy(self)
        # Re-init with a cloned julia learner
        Learner.__init__(lnr, _IAI.clone(self._jl_obj))
        return lnr


class SupervisedLearner(Learner):
    """Abstract type encompassing all learners for supervised tasks"""

    def predict(self, *args, **kwargs):
        """Return the predictions made by the learner for each point in the
        features `X`.

        Julia Equivalent:
        `IAI.predict <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.predict>`

        Examples
        --------
        >>> lnr.predict(X)
        """
        return _IAI.predict_convert(self._jl_obj, *args, **kwargs)

    def score(self, *args, **kwargs):
        """Calculates the score for the learner on data `X` and `y`.

        Julia Equivalent:
        `IAI.score <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.score>`

        Examples
        --------
        >>> lnr.score(X, *y, **kwargs)
        """
        return _IAI.score_convert(self._jl_obj, *args, **kwargs)


class UnsupervisedLearner(Learner):
    """Abstract type encompassing all learners for unsupervised tasks"""
    pass


class ClassificationLearner(SupervisedLearner):
    """Abstract type encompassing all learners for classification tasks"""

    def predict_proba(self, *args, **kwargs):
        """Return the probabilities of class membership predicted by the
        learner for each point in the features `X`.

        Julia Equivalent:
        `IAI.predict_proba <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.predict_proba>`

        Examples
        --------
        >>> lnr.predict_proba(X)
        """
        return _IAI.predict_proba_convert(self._jl_obj, *args, **kwargs)


class RegressionLearner(SupervisedLearner):
    """Abstract type encompassing all learners for regression tasks"""
    pass


class SurvivalLearner(SupervisedLearner):
    """Abstract type encompassing all learners for survival tasks"""

    def predict(self, *args, **kwargs):
        jl_curves = _IAI.predict_convert(self._jl_obj, *args, **kwargs)
        return [SurvivalCurve(jl_curve) for jl_curve in jl_curves]


class PrescriptionLearner(SupervisedLearner):
    """Abstract type encompassing all learners for prescription tasks"""

    def predict_outcomes(self, *args, **kwargs):
        """Return the the predicted outcome for each treatment made by the
        learner for each point in the features `X`.

        Julia Equivalent:
        `IAI.predict_outcomes <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.predict_outcomes>`

        Examples
        --------
        >>> lnr.predict_outcomes(X)
        """
        return _IAI.predict_outcomes_convert(self._jl_obj, *args, **kwargs)


class GridSearch(Learner):
    """Controls grid search over parameter combinations in `params` for `lnr`.

    Julia Equivalent:
    `IAI.GridSearch <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.GridSearch>`

    Examples
    --------
    >>> GridSearch(lnr, params)
    """
    def __init__(self, lnr, *args, **kwargs):
        if not isinstance(lnr, Learner):
            raise TypeError("lnr is not a Learner")

        self._lnr_type = type(lnr)

        jl_obj = _IAI.GridSearch(lnr._jl_obj, *args, **kwargs)
        super(GridSearch, self).__init__(jl_obj)

    # Fallback to hitting learner methods if not defined on grid search
    def __getattr__(self, item):
        return getattr(self.get_learner(), item)

    def get_learner(self):
        """Return the fitted learner using the best parameter combination from
        the grid.

        Julia Equivalent:
        `IAI.get_learner <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.get_learner>`

        Examples
        --------
        >>> grid.get_learner()
        """
        lnr = self._lnr_type()
        jl_obj = _IAI.get_learner(self._jl_obj)
        Learner.__init__(lnr, jl_obj)
        return lnr

    def get_best_params(self):
        """Return the best parameter combination from the grid.

        Julia Equivalent:
        `IAI.get_best_params <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.get_best_params>`

        Examples
        --------
        >>> grid.get_best_params()
        """
        return _IAI.get_best_params_convert(self._jl_obj)

    def get_grid_results(self):
        """Return a summary of the results from the grid search.

        Julia Equivalent:
        `IAI.get_grid_results <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.get_grid_results>`

        Examples
        --------
        >>> grid.get_grid_results()
        """
        return _IAI.get_grid_results_convert(self._jl_obj)

    def fit_cv(self, *args, **kwargs):
        """Fit a grid with data `X` and `y` using k-fold cross-validation.

        Julia Equivalent:
        `IAI.fit_cv! <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.fit_cv!>`

        Examples
        --------
        >>> grid.fit_cv(X, *y, **kwargs)

        Parameters
        ----------
        Refer to the documentation on
        [data preparation](@ref Data-Preparation-Guide)
        for information on how to format and supply the data.
        """
        _IAI.fit_cv_convert(self._jl_obj, *args, **kwargs)
        return self

    def fit_transform_cv(self, *args, **kwargs):
        """For imputation learners, fit a grid with features `X` using k-fold
        cross-validation and impute missing values in `X`.

        Julia Equivalent:
        `IAI.fit_transform_cv! <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.fit_transform_cv!>`

        Examples
        --------
        >>> grid.fit_transform_cv(X, **kwargs)

        Parameters
        ----------
        Refer to the documentation on
        [data preparation](@ref Data-Preparation-Guide)
        for information on how to format and supply the data.
        """
        # TODO is this the best way to do it? Some way of adding the task mixin
        #      to the grid seems like it could be better
        if not getattr(self._lnr_type(), "fit_transform", None):
            raise TypeError("GridSearch over " + self._lnr_type.__name__ +
                            " does not support `fit_transform_cv`.")
        return _IAI.fit_transform_cv_convert(self._jl_obj, *args, **kwargs)


class ROCCurve(object):
    """Construct an ROC curve using trained `lnr` on the features `X` and labels
    `y`.

    Contains the following fields:

    - `coords`: a `dict` for each point on the curve with the following keys:
        - `'fpr'`: false positive rate at the given threshold
        - `'tpr'`: true positve rate at the given threshold
        - `'threshold'`: the threshold
    - `auc`: the area-under-the-curve (AUC)

    Julia Equivalent:
    `IAI.ROCCurve <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.ROCCurve>`

    Examples
    --------
    >>> ROCCurve(lnr, X, y)
    """
    def __init__(self, lnr, *args, **kwargs):
        if isinstance(lnr, GridSearch):
            lnr = lnr.get_learner()

        if not isinstance(lnr, ClassificationLearner):
            raise TypeError("lnr is not a ClassificationLearner")

        self._jl_obj = _IAI.ROCCurve_convert(lnr._jl_obj, *args, **kwargs)

    def __repr__(self):
        return _IAI.string(self._jl_obj)

    def _repr_html_(self):
        return _IAI.to_html(self._jl_obj)

    def show_in_browser(self, **kwargs):  # pragma: no cover
        """Visualize the ROC curve in the browser.

        Julia Equivalent:
        `IAI.show_in_browser <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.show_in_browser>`

        Examples
        --------
        >>> curve.show_in_browser()
        """
        return _IAI.show_in_browser_convert(self._jl_obj, **kwargs)


class SurvivalCurve(object):
    """Container for survival curve information.

    Use `curve[t]` to get the survival probability prediction from curve at
    time `t`.
    """
    def __init__(self, jl_curve):
        self._jl_obj = jl_curve

    def __getitem__(self, item):
        if not isinstance(item, (int, float)):
            raise TypeError("only supports scalar indexing")
        return _IAI.getindex(self._jl_obj, item)

    def __repr__(self):
        return _IAI.string(self._jl_obj)

    def get_data(self):
        """Extract the underlying data from the curve as a `dict` with two keys:
        - `'times'`: the time for each breakpoint on the curve
        - `'coefs'`: the probablility for each breakpoint on the curve

        Julia Equivalent:
        `IAI.get_survival_curve_data <https://docs.interpretable.ai/IAIBase/stable/reference/#IAI.get_survival_curve_data>`

        Examples
        --------
        >>> curve.get_data()
        """
        return _IAI.get_survival_curve_data_convert(self._jl_obj)
