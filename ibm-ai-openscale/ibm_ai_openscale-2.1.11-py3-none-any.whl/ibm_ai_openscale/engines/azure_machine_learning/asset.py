# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.assets import KnownServiceAsset
from ibm_ai_openscale.utils import validate_type, validate_enum
from ibm_ai_openscale.supporting_classes import InputDataType, ProblemType
from .consts import AzureConsts


class AzureMachineLearningAsset(KnownServiceAsset):
    """
    Describes Azure Machine Learning asset.

    :param source_uid: asset id
    :type source_uid: str
    :param binding_uid: binding_uid of asset (optional)
    :type binding_uid: str
    :param problem_type: type of model (problem)
    :type problem_type: str
    :param input_data_type: type of input data
    :type input_data_type: str
    :param training_data_reference: reference to training data (optional)
    :type training_data_reference: StorageReference or json
    :param label_column: the column/field name containing target/label values
    :type label_column: str
    :param prediction_column: the name of column/field with predicted values
    :type prediction_column: str
    :param probability_column: the name of column/field with prediction probability (optional)
    :type probability_column: str
    :param feature_columns: names of columns which contains features (optional)
    :type feature_columns: list of str
    :param categorical_columns: names of columns which contains categorical data (optional)
    :type categorical_columns: list of str

    A way you might use me is:

    >>> from ibm_ai_openscale.supporting_classes.enums import InputDataType, ProblemType
    >>>
    >>> AzureMachineLearningAsset(source_uid=uid, binding_uid=binding_uid, input_data_type=InputDataType.STRUCTURED,
    >>>         problem_type=ProblemType.BINARY_CLASSIFICATION, label_column='label', prediction_column='Scored Labels')
    """
    service_type = AzureConsts.SERVICE_TYPE

    def __init__(self, source_uid, binding_uid=None, problem_type=None, input_data_type=None,
                 training_data_reference=None, label_column=None, prediction_column=None, probability_column=None,
                 feature_columns=None, categorical_columns=None):

        validate_type(source_uid, 'source_uid', str, mandatory=True)
        validate_enum(input_data_type, 'input_data_type', InputDataType, mandatory=True)
        validate_enum(problem_type, 'problem_type', ProblemType, mandatory=True)
        validate_type(label_column, 'label_column', str, mandatory=True)
        validate_type(prediction_column, 'prediction_column', str, mandatory=True)
        validate_type(binding_uid, 'binding_uid', str, mandatory=False)
        validate_type(probability_column, 'probability_column', str, mandatory=False)

        KnownServiceAsset.__init__(self, source_uid=source_uid, binding_uid=binding_uid, problem_type=problem_type,
                                   input_data_type=input_data_type, training_data_reference=training_data_reference,
                                   label_column=label_column, prediction_column=prediction_column,
                                   probability_column=probability_column, feature_columns=feature_columns,
                                   categorical_columns=categorical_columns)
