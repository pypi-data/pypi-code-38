# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""model_explanation.py, A file for model explanation classes."""


# TODO: Tell PowerBI to fix casing on their end
class FeatureNameFormats(object):
    """Feature name formats."""

    STRING = 'str'
    JSON = 'json'

    ALL = {STRING, JSON}


class AutoMLExplanation(object):
    """A wrapper class which contains all model explanation related information."""

    def __init__(self,
                 shap_values=None,
                 expected_values=None,
                 overall_summary=None,
                 overall_imp=None,
                 per_class_summary=None,
                 per_class_imp=None):
        """Init method for the Explanation class."""
        self.shap_values = shap_values
        self.expected_values = expected_values
        self.overall_summary = overall_summary
        self.overall_imp = overall_imp
        self.per_class_summary = per_class_summary
        self.per_class_imp = per_class_imp

    @classmethod
    def from_global_explanation(cls, global_explanation):
        """Create the explanation with factory method given a global_explanation.

        :param global_explanation: The Global Explanation
        :type global_explanation: azureml.explain.model.explanation.GlobalExplanation
        :return: An instance of AutoMLExplanation
        :rtype: AutoMLExplanation
        """
        explanation = _convert_explanation(global_explanation)

        return cls(explanation[0], explanation[1], explanation[2], explanation[3], explanation[4], explanation[5])

    def get_model_explanation(self,
                              feature_name_format=FeatureNameFormats.STRING,
                              transformer=None):
        """
        Get model explanation.

        :param feature_name_format: feature name's format, either str or json
        :param transformer: the DataTransformer used in preprocessing to
            generate features, if applicable
        :type transformer: DataTransformer or TimeSeriesTransformer
        :return: model explanations information with feature names in specified
            format
        """
        # TODO: Remove .lower() after PowerBI fixes casing
        if feature_name_format.lower() not in FeatureNameFormats.ALL:
            raise ValueError('Invalid feature name format specified. Value'
                             'must be in the set {}'
                             .format(FeatureNameFormats.ALL))

        if feature_name_format.lower() == FeatureNameFormats.STRING or \
                transformer is None:
            overall_imp_format = self.overall_imp
            per_class_imp_format = self.per_class_imp
        else:
            overall_imp_format = \
                transformer.get_json_strs_for_engineered_feature_names(
                    self.overall_imp)
            per_class_imp_format = None
            if self.per_class_imp is not None:
                per_class_imp_format = []
                for item in self.per_class_imp:
                    per_class_imp_format.append(
                        transformer.get_json_strs_for_engineered_feature_names(
                            item))
        return self.shap_values, self.expected_values, self.overall_summary, \
            overall_imp_format, self.per_class_summary, per_class_imp_format


def _convert_explanation(explanation, include_local_importance=True):
    """
    Convert the explanation tuple into a consistent six element tuple.

    :param explanation: a tuple of four or six elements
    :return: a tuple of six elements
    """
    if include_local_importance:
        local_importance_value = explanation.local_importance_values
    expected_value = None
    overall_summary = explanation.get_ranked_global_values()
    overall_imp = explanation.get_ranked_global_names()
    per_class_summary = None
    per_class_imp = None
    if hasattr(explanation, 'get_ranked_per_class_values'):
        per_class_summary = explanation.get_ranked_per_class_values()
    if hasattr(explanation, 'get_ranked_per_class_names'):
        per_class_imp = explanation.get_ranked_per_class_names()

    if include_local_importance:
        return (local_importance_value, expected_value, overall_summary, overall_imp, per_class_summary, per_class_imp)
    else:
        return (None, expected_value, overall_summary, overall_imp, per_class_summary, per_class_imp)
