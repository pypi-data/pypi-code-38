from .iai import _IAI
from .iaitrees import (TreeLearner, ClassificationTreeLearner,
                       RegressionTreeLearner, SurvivalTreeLearner,
                       PrescriptionTreeLearner)


class OptimalTreeLearner(TreeLearner):
    """Abstract type encompassing all optimal tree learners."""
    pass


class OptimalTreeClassifier(OptimalTreeLearner, ClassificationTreeLearner):
    """Learner for training Optimal Classification Trees.

    Julia Equivalent:
    `IAI.OptimalTreeClassifier <https://docs.interpretable.ai/OptimalTrees/stable/reference/#IAI.OptimalTreeClassifier>`

    Examples
    --------
    >>> OptimalTreeClassifier(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        jl_obj = _IAI.OptimalTreeClassifier(*args, **kwargs)
        super(OptimalTreeClassifier, self).__init__(jl_obj)


class OptimalTreeRegressor(OptimalTreeLearner, RegressionTreeLearner):
    """Learner for training Optimal Regression Trees.

    Julia Equivalent:
    `IAI.OptimalTreeRegressor <https://docs.interpretable.ai/OptimalTrees/stable/reference/#IAI.OptimalTreeRegressor>`

    Examples
    --------
    >>> OptimalTreeRegressor(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        jl_obj = _IAI.OptimalTreeRegressor(*args, **kwargs)
        super(OptimalTreeRegressor, self).__init__(jl_obj)


class OptimalTreeSurvivor(OptimalTreeLearner, SurvivalTreeLearner):
    """Learner for training Optimal Survival Trees.

    Julia Equivalent:
    `IAI.OptimalTreeSurvivor <https://docs.interpretable.ai/OptimalTrees/stable/reference/#IAI.OptimalTreeSurvivor>`

    Examples
    --------
    >>> OptimalTreeSurvivor(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        jl_obj = _IAI.OptimalTreeSurvivor(*args, **kwargs)
        super(OptimalTreeSurvivor, self).__init__(jl_obj)


class OptimalTreePrescriptionMinimizer(OptimalTreeLearner,
                                       PrescriptionTreeLearner):
    """Learner for training Optimal Prescriptive Trees where the prescriptions
    should aim to minimize outcomes.

    Julia Equivalent:
    `IAI.OptimalTreePrescriptionMinimizer <https://docs.interpretable.ai/OptimalTrees/stable/reference/#IAI.OptimalTreePrescriptionMinimizer>`

    Examples
    --------
    >>> OptimalTreePrescriptionMinimizer(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        jl_obj = _IAI.OptimalTreePrescriptionMinimizer(*args, **kwargs)
        super(OptimalTreePrescriptionMinimizer, self).__init__(jl_obj)


class OptimalTreePrescriptionMaximizer(OptimalTreeLearner,
                                       PrescriptionTreeLearner):
    """Learner for training Optimal Prescriptive Trees where the prescriptions
    should aim to maximize outcomes.

    Julia Equivalent:
    `IAI.OptimalTreePrescriptionMaximizer <https://docs.interpretable.ai/OptimalTrees/stable/reference/#IAI.OptimalTreePrescriptionMaximizer>`

    Examples
    --------
    >>> OptimalTreePrescriptionMaximizer(**kwargs)

    Parameters
    ----------
    Use keyword arguments to set parameters on the resulting learner. Refer to
    the Julia documentation for available parameters.
    """
    def __init__(self, *args, **kwargs):
        jl_obj = _IAI.OptimalTreePrescriptionMaximizer(*args, **kwargs)
        super(OptimalTreePrescriptionMaximizer, self).__init__(jl_obj)
