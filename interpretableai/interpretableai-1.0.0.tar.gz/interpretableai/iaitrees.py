from .iai import _IAI
from .iaibase import (SupervisedLearner, ClassificationLearner,
                      RegressionLearner, SurvivalLearner, PrescriptionLearner,
                      SurvivalCurve)


class TreeLearner(SupervisedLearner):
    """Abstract type encompassing all tree-based learners."""

    def _repr_html_(self):
        return _IAI.to_html(self._jl_obj)

    def get_num_nodes(self):
        """Return the number of nodes in the trained learner.

        Julia Equivalent:
        `IAI.get_num_nodes <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_num_nodes>`

        Examples
        --------
        >>> lnr.get_num_nodes(node_index)
        """
        return _IAI.get_num_nodes_convert(self._jl_obj)

    def is_leaf(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a leaf.

        Julia Equivalent:
        `IAI.is_leaf <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.is_leaf>`

        Examples
        --------
        >>> lnr.is_leaf(node_index)
        """
        return _IAI.is_leaf_convert(self._jl_obj, node_index)

    def get_depth(self, node_index):
        """Return the depth of node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_depth <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_depth>`

        Examples
        --------
        >>> lnr.get_depth(node_index)
        """
        return _IAI.get_depth_convert(self._jl_obj, node_index)

    def get_num_samples(self, node_index):
        """Return the number of training points contained in node `node_index`
        in the trained learner.

        Julia Equivalent:
        `IAI.get_num_samples <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_num_samples>`

        Examples
        --------
        >>> lnr.get_num_samples(node_index)
        """
        return _IAI.get_num_samples_convert(self._jl_obj, node_index)

    def get_lower_child(self, node_index):
        """Return the index of the lower child of node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_lower_child <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_lower_child>`

        Examples
        --------
        >>> lnr.get_lower_child(node_index)
        """
        return _IAI.get_lower_child_convert(self._jl_obj, node_index)

    def get_upper_child(self, node_index):
        """Return the index of the upper child of node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_upper_child <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_upper_child>`

        Examples
        --------
        >>> lnr.get_upper_child(node_index)
        """
        return _IAI.get_upper_child_convert(self._jl_obj, node_index)

    def is_parallel_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a
        parallel split.

        Julia Equivalent:
        `IAI.is_parallel_split <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.is_parallel_split>`

        Examples
        --------
        >>> lnr.is_parallel_split(node_index)
        """
        return _IAI.is_parallel_split_convert(self._jl_obj, node_index)

    def is_hyperplane_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a
        hyperplane split.

        Julia Equivalent:
        `IAI.is_hyperplane_split <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.is_hyperplane_split>`

        Examples
        --------
        >>> lnr.is_hyperplane_split(node_index)
        """
        return _IAI.is_hyperplane_split_convert(self._jl_obj, node_index)

    def is_categoric_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a
        categoric split.

        Julia Equivalent:
        `IAI.is_categoric_split <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.is_categoric_split>`

        Examples
        --------
        >>> lnr.is_categoric_split(node_index)
        """
        return _IAI.is_categoric_split_convert(self._jl_obj, node_index)

    def is_ordinal_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is an
        ordinal split.

        Julia Equivalent:
        `IAI.is_ordinal_split <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.is_ordinal_split>`

        Examples
        --------
        >>> lnr.is_ordinal_split(node_index)
        """
        return _IAI.is_ordinal_split_convert(self._jl_obj, node_index)

    def is_mixed_parallel_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a mixed
        categoric/parallel split.

        Julia Equivalent:
        `IAI.is_mixed_parallel_split <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.is_mixed_parallel_split>`

        Examples
        --------
        >>> lnr.is_mixed_parallel_split(node_index)
        """
        return _IAI.is_mixed_parallel_split_convert(self._jl_obj, node_index)

    def is_mixed_ordinal_split(self, node_index):
        """Return `True` if node `node_index` in the trained learner is a mixed
        categoric/ordinal split.

        Julia Equivalent:
        `IAI.is_mixed_ordinal_split <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.is_mixed_ordinal_split>`

        Examples
        --------
        >>> lnr.is_mixed_ordinal_split(node_index)
        """
        return _IAI.is_mixed_ordinal_split_convert(self._jl_obj, node_index)

    def missing_goes_lower(self, node_index):
        """Return `True` if missing values take the lower branch at node
        `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.missing_goes_lower <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.missing_goes_lower>`

        Examples
        --------
        >>> lnr.missing_goes_lower(node_index)
        """
        return _IAI.missing_goes_lower_convert(self._jl_obj, node_index)

    def get_split_feature(self, node_index):
        """Return the feature used in the split at node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_split_feature <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_split_feature>`

        Examples
        --------
        >>> lnr.get_split_feature(node_index)
        """
        return _IAI.get_split_feature_convert(self._jl_obj, node_index)

    def get_split_threshold(self, node_index):
        """Return the threshold used in the split at node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_split_threshold <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_split_threshold>`

        Examples
        --------
        >>> lnr.get_split_threshold(node_index)
        """
        return _IAI.get_split_threshold_convert(self._jl_obj, node_index)

    def get_split_categories(self, node_index):
        """Return the categoric/ordinal information used in the split at node
        `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_split_categories <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_split_categories>`

        Examples
        --------
        >>> lnr.get_split_categories(node_index)
        """
        return _IAI.get_split_categories_convert(self._jl_obj, node_index)

    def get_split_weights(self, node_index):
        """Return the weights for numeric and categoric features used in the
        hyperplane split at  node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_split_weights <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_split_weights>`

        Examples
        --------
        >>> lnr.get_split_weights(node_index)
        """
        return _IAI.get_split_weights_convert(self._jl_obj, node_index)

    def apply(self, *args, **kwargs):
        """Return the leaf index in the learner into which each point in the
        features `X` falls.

        Julia Equivalent:
        `IAI.apply <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.apply>`

        Examples
        --------
        >>> lnr.apply(X)
        """
        return _IAI.apply_convert(self._jl_obj, *args, **kwargs)

    def apply_nodes(self, *args, **kwargs):
        """Return the indices of the points in the features `X` that fall into
        each node in the learner.

        Julia Equivalent:
        `IAI.apply_nodes <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.apply_nodes>`

        Examples
        --------
        >>> lnr.apply_nodes(X)
        """
        return _IAI.apply_nodes_convert(self._jl_obj, *args, **kwargs)

    def decision_path(self, *args, **kwargs):
        """Return a matrix where entry `(i, j)` is `True` if the `i`th point in
        the features `X` passes through the `j`th node in the learner.

        Julia Equivalent:
        `IAI.decision_path <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.decision_path>`

        Examples
        --------
        >>> lnr.decision_path(X)
        """
        return _IAI.decision_path_convert(self._jl_obj, *args, **kwargs)

    def print_path(self, *args, **kwargs):
        """Print the decision path through the learner for each sample in the
        features `X`.

        Julia Equivalent:
        `IAI.print_path <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.print_path>`

        Examples
        --------
        >>> lnr.print_path(X)
        """
        return _IAI.print_path_convert(self._jl_obj, *args, **kwargs)

    def variable_importance(self):
        """Generate a ranking of the variables in the learner according to their importance when training the trees.

        Julia Equivalent:
        `IAI.variable_importance <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.variable_importance>`

        Examples
        --------
        >>> lnr.variable_importance()
        """
        return _IAI.variable_importance_convert(self._jl_obj)

    def write_png(self, filename, **kwargs):  # pragma: no cover
        """Write learner to `filename` as a PNG image.

        Requires
        [GraphViz](http://www.graphviz.org/)
        be installed and on the system `PATH`.

        Julia Equivalent:
        `IAI.write_png <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.write_png>`

        Examples
        --------
        >>> lnr.write_png(filename, **kwargs)
        """
        return _IAI.write_png_convert(filename, self._jl_obj, **kwargs)

    def write_dot(self, filename, **kwargs):
        """Write learner to `filename` in
        [.dot format](http://www.graphviz.org/content/dot-language/).

        Julia Equivalent:
        `IAI.write_dot <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.write_dot>`

        Examples
        --------
        >>> lnr.write_dot(filename, **kwargs)
        """
        return _IAI.write_dot_convert(filename, self._jl_obj, **kwargs)

    def write_html(self, filename, **kwargs):
        """Write interactive browser visualization of learner to `filename` as
        HTML.

        Julia Equivalent:
        `IAI.write_html <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.write_html>`

        Examples
        --------
        >>> lnr.write_html(filename, **kwargs)
        """
        return _IAI.write_html_convert(filename, self._jl_obj, **kwargs)

    def show_in_browser(self, **kwargs):  # pragma: no cover
        """Show interactive visualization of learner in default browser.

        Julia Equivalent:
        `IAI.show_in_browser <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.show_in_browser>`

        Examples
        --------
        >>> lnr.show_in_browser(**kwargs)
        """
        return _IAI.show_in_browser_convert(self._jl_obj, **kwargs)

    def write_questionnaire(self, filename, **kwargs):
        """Write interactive questionnaire based on learner to `filename` as
        HTML.

        Julia Equivalent:
        `IAI.write_questionnaire <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.write_questionnaire>`

        Examples
        --------
        >>> lnr.write_questionnaire(filename, **kwargs)
        """
        return _IAI.write_questionnaire_convert(filename, self._jl_obj,
                                                **kwargs)

    def show_questionnaire(self, **kwargs):  # pragma: no cover
        """Show interactive questionnaire based on learner in default browser.

        Julia Equivalent:
        `IAI.show_questionnaire <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.show_questionnaire>`

        Examples
        --------
        >>> lnr.show_questionnaire(**kwargs)
        """
        return _IAI.show_questionnaire_convert(self._jl_obj, **kwargs)


class ClassificationTreeLearner(ClassificationLearner):
    """Abstract type encompassing all tree-based learners with classification
    leaves.
    """

    def get_classification_label(self, node_index):
        """Return the predicted label at node `node_index` in the trained
        learner.

        Julia Equivalent:
        `IAI.get_classification_label <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_classification_label>`

        Examples
        --------
        >>> lnr.get_classification_label(node_index)
        """
        return _IAI.get_classification_label_convert(self._jl_obj, node_index)

    def get_classification_proba(self, node_index):
        """Return the predicted probabilities of class membership at node
        `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_classification_proba <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_classification_proba>`

        Examples
        --------
        >>> lnr.get_classification_proba(node_index)
        """
        return _IAI.get_classification_proba_convert(self._jl_obj, node_index)

    def set_threshold(self, *args, **kwargs):
        """For a binary classification problem, update the the predicted labels
        in the leaves of the learner to predict `label` only if the predicted
        probability is at least `threshold`. If `simplify` is `True`, the tree
        will be simplified after all changes have been made.

        Julia Equivalent:
        `IAI.set_threshold! <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.set_threshold!>`

        Examples
        --------
        >>> lnr.set_threshold(label, threshold, simplify=False)
        """
        _IAI.set_threshold_convert(self._jl_obj, *args, **kwargs)
        return self

    def set_display_label(self, *args, **kwargs):
        """Show the probability of `display_label` when visualizing learner.

        Julia Equivalent:
        `IAI.set_display_label! <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.set_display_label!>`

        Examples
        --------
        >>> lnr.set_display_label(display_label)
        """
        _IAI.set_display_label_convert(self._jl_obj, *args, **kwargs)
        return self

    def reset_display_label(self):
        """Reset the predicted probability displayed to be that of the
        predicted label when visualizing learner.

        Julia Equivalent:
        `IAI.reset_display_label! <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.reset_display_label!>`

        Examples
        --------
        >>> lnr.reset_display_label(display_label)
        """
        _IAI.reset_display_label_convert(self._jl_obj)
        return self


class RegressionTreeLearner(RegressionLearner):
    """Abstract type encompassing all tree-based learners with regression
    leaves.
    """

    def get_regression_constant(self, node_index):
        """Return the constant term in the regression prediction at node
        `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_regression_constant <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_regression_constant-Tuple%7BTreeLearner%7BIAIBase.RegressionTask%7D%2CInt64%7D>`

        Examples
        --------
        >>> lnr.get_regression_constant(node_index)
        """
        return _IAI.get_regression_constant_convert(self._jl_obj, node_index)

    def get_regression_weights(self, node_index):
        """Return the weights for each feature in the regression prediction at
        node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_regression_weights <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_regression_weights-Tuple%7BTreeLearner%7BIAIBase.RegressionTask%7D%2CInt64%7D>`

        Examples
        --------
        >>> lnr.get_regression_weights(node_index)
        """
        return _IAI.get_regression_weights_convert(self._jl_obj, node_index)


class SurvivalTreeLearner(SurvivalLearner):
    """Abstract type encompassing all tree-based learners with survival leaves.
    """

    def get_survival_curve(self, node_index):
        """Return the [`SurvivalCurve`](@ref) at node `node_index` in the
        trained learner.

        Julia Equivalent:
        `IAI.get_survival_curve <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_survival_curve>`

        Examples
        --------
        >>> lnr.get_survival_curve(node_index)
        """
        jl_curve = _IAI.get_survival_curve_convert(self._jl_obj, node_index)
        return SurvivalCurve(jl_curve)


class PrescriptionTreeLearner(PrescriptionLearner):
    """Abstract type encompassing all tree-based learners with prescription
    leaves.
    """

    def get_prescription_treatment_rank(self, node_index):
        """Return the treatments ordered from most effective to least effective
        at node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_prescription_treatment_rank <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_prescription_treatment_rank>`

        Examples
        --------
        >>> lnr.get_prescription_treatment_rank(node_index)
        """
        return _IAI.get_prescription_treatment_rank(self._jl_obj, node_index)

    def get_regression_constant(self, node_index, treatment):
        """Return the constant in the regression prediction for `treatment` at
        node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_regression_constant <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_regression_constant-Tuple%7BTreeLearner%7BIAIBase.PrescriptionTask%7BO%7D%7D%2520where%2520O%2CInt64%2CAny%7D>`

        Examples
        --------
        >>> lnr.get_regression_constant(node_index, treatment)
        """
        return _IAI.get_regression_constant_convert(self._jl_obj, node_index,
                                                    treatment)

    def get_regression_weights(self, node_index, treatment):
        """Return the weights for each feature in the regression prediction for
        `treatment` at node `node_index` in the trained learner.

        Julia Equivalent:
        `IAI.get_regression_weights <https://docs.interpretable.ai/IAITrees/stable/reference/#IAI.get_regression_weights-Tuple%7BTreeLearner%7BIAIBase.PrescriptionTask%7BO%7D%7D%2520where%2520O%2CInt64%2CAny%7D>`

        Examples
        --------
        >>> lnr.get_regression_weights(node_index, treatment)
        """
        return _IAI.get_regression_weights_convert(self._jl_obj, node_index,
                                                   treatment)
