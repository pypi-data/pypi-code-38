# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_ai_openscale.base_classes.assets import Asset
from ibm_ai_openscale.utils import *
from ibm_ai_openscale.supporting_classes.enums import ProblemType, InputDataType
from ibm_ai_openscale.supporting_classes.storage_reference import StorageReference


class KnownServiceAsset(Asset):
    def __init__(self, source_uid, binding_uid=None, problem_type=None, input_data_type=None,
                 training_data_reference=None, label_column=None, prediction_column=None, probability_column=None,
                 class_probability_columns=None, feature_columns=None, categorical_columns=None):
        validate_type(source_uid, 'source_uid', str, True)
        validate_type(binding_uid, 'binding_uid', str, False)
        validate_enum(problem_type, 'problem_type', ProblemType, False)
        validate_enum(input_data_type, 'input_data_type', InputDataType, False)
        validate_type(training_data_reference, 'training_data_reference', [StorageReference, dict], False, subclass=True)
        validate_type(label_column, 'label_column', str, False)
        validate_type(prediction_column, 'prediction_column', str, False)
        validate_type(probability_column, 'probability_column', str, False)
        validate_type(class_probability_columns, 'class_probability_columns', list, False)
        validate_type(feature_columns, 'feature_columns', list, False)
        validate_type(categorical_columns, 'categorical_columns', list, False)

        Asset.__init__(self, binding_uid)
        self.source_uid = source_uid
        self.problem_type = problem_type
        self.input_data_type = input_data_type
        self.training_data_reference = training_data_reference
        self.label_column = label_column
        self.prediction_column = prediction_column
        self.probability_column = probability_column
        self.class_probability_columns = class_probability_columns
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns

