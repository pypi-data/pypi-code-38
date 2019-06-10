# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes and methods for generating engineered feature names for features extracted using pre-processing."""
from typing import Any, cast, Dict, List, Optional, Union
import copy
import re
from collections import defaultdict
from sklearn.pipeline import Pipeline, make_pipeline
from automl.client.core.common.types import FeaturizationSummaryType


class _GenerateEngineeredFeatureNames:
    """
    Transforms the transformed raw feature names into engineered feature names.

    The following schema design is followed for storing the engineered names:-

    {
        "FinalTransformerName": string,
        "Transformations": {
            "Transformer1":
            {
                    "Input": [
                                {"InputFeatureName":string},
                                {"InputFeatureName":string}
                            ]
                    "TransformationFunction": string.
                    "Operator": string
                    "FeatureType": string,
                    "ShouldOutput": bool
            },
            "Transformer2":
            {
                    "Input": [
                                {"InputFeatureName":string},
                                {"InputFeatureName":string}
                            ]
                    "TransformationFunction": string.
                    "Operator": string
                    "FeatureType": string,
                    "ShouldOutput": bool
            },
            .
            .
            .
            "TransformerN":
            {
                    "Input": [
                                {"InputFeatureName":string},
                                {"InputFeatureName":string}
                            ]
                    "TransformationFunction": string
                    "Operator": string
                    "FeatureType": string,
                    "ShouldOutput": bool
            }
        },

        "Value": string
    }
    """

    def __init__(self):
        """Initialize this feature name transformer."""
        # Maintain mapping between alias raw feature name and transformation
        # json objects
        self.alias_raw_feature_name_transformation_mapping = {}  # type: Dict[str, _FeatureTransformersAsJSONObject]
        # Maintain a list of string version of engineered feature names
        self._engineered_feature_names = []     # type: List[str]
        # Maintain a dictionary of JSON objects for engineered feature names
        self._engineered_feature_name_json_objects = {}  # type: Dict[str, Dict[str, Any]]

    def are_engineered_feature_names_available(self) -> bool:
        """
        Return 'True' if engineered feature names have already been created; 'False' otherwise.

        :return: bool
        """
        return len(self._engineered_feature_names) != 0

    def get_raw_feature_alias_name(self, transformation_json_obj: Any) -> str:
        """
        Take a list of transformations needed for a raw feature and return the resulting alias name.

        :param transformation_json_obj:
        :return: A number represented as string
        """
        # Add the json string for transformations into a dictionary which
        # maps the alias name to the json string
        self.alias_raw_feature_name_transformation_mapping[
            str(len(self.alias_raw_feature_name_transformation_mapping) + 1)] = transformation_json_obj
        alias_name = str(
            len(self.alias_raw_feature_name_transformation_mapping))

        # Return the alias name for the raw feature
        return alias_name

    def get_alias_name_from_pipeline_object(self, columns: List[str],
                                            pipeline_object: Pipeline, columntype: str) -> str:
        """
        Take a pipeline object and return the engineering feature name.

        :param pipeline_object:
        :return: A number represented as string
        """
        pipeline = pipeline_object
        transformers = []  # type: List[_Transformer]

        if pipeline:
            steps = pipeline.steps
            parent_feature_list = columns  # type: Union[List[str], List[int]]
            for index, (name, transform) in enumerate(steps):
                if transform:
                    if hasattr(transform, 'transformer_name'):
                        transformer_name = transform.transformer_name
                    else:
                        transformer_name = transform.__class__.__name__

                    if hasattr(transform, 'operator_name'):
                        operator = transform.operator_name
                    else:
                        operator = None

                    if index == 0:
                        parent_feature_list = columns
                    else:
                        parent_feature_list = [index]

                    if transformer_name == _TransformationFunctionNames.StringCast:
                        show_output = False
                    else:
                        show_output = True

                    tr = _Transformer(parent_feature_list, transformer_name, operator, columntype, show_output)
                    transformers.append(tr)
            if len(transformers) > 0:
                feature_transformers = _FeatureTransformers(transformers)
                json_obj = feature_transformers.encode_transformations_from_list()
                alias_column_name = self.get_raw_feature_alias_name(json_obj)
                return alias_column_name

        return ''

    def get_raw_features_featurization_summary(self) -> FeaturizationSummaryType:
        """
        Return the featurization summary for all the input features seen by this class.

        :return: List of featurization summary for each input feature.
        """
        return _RawFeatureFeaturizationInfo.get_coalesced_raw_feature_featurization_mapping(
            self.alias_raw_feature_name_transformation_mapping, self._engineered_feature_name_json_objects)

    def parse_raw_feature_names(self, transformed_raw_feature_names: List[str]) -> None:
        """
        Parse transformed raw feature names, compose engineered feature names and store as JSON for later use.

        :param transformed_raw_feature_names:
            A list of string which are the transformed feature names from sklearn transformations
        """
        # Get the regex for transformed feature names
        regex_transformed_feature_name = FeatureNamesHelper.get_regular_exp_for_parsing_raw_feature_names()

        for raw_feature_name in transformed_raw_feature_names:
            # Parse transformed feature name with the regex
            transformed_feature_match_obj = re.match(
                regex_transformed_feature_name, raw_feature_name)

            if transformed_feature_match_obj:
                # If there is a match, then extract the values out of
                # the match object
                raw_feature_alias = transformed_feature_match_obj.group(1)
                value_str = transformed_feature_match_obj.group(3)
            else:
                # If the transformed feature names doesn't match the
                # regular expression, then raise exception
                raise ValueError(
                    "Unrecognized transformed feature name passed")

            # Get JSON tranformation data for the raw feature alias name
            if raw_feature_alias not in self.alias_raw_feature_name_transformation_mapping:
                raise ValueError("Unrecognized raw feature alias name passed")

            transformation_json_data_obj = self.alias_raw_feature_name_transformation_mapping[
                raw_feature_alias]

            # Make a copy of the transformation
            transformation_json_data_obj_copy = copy.deepcopy(
                transformation_json_data_obj)

            # Get the raw feature type from the transformations
            feature_type = transformation_json_data_obj_copy.get_raw_feature_type()

            # Get the JSON object
            transformation_json_data = transformation_json_data_obj_copy._entire_transformation_json_data
            if feature_type == FeatureTypeRecognizer.DateTime:
                # If the raw feature type is Datetime, then get the
                # sub-feature and store it
                transformation_json_data[_FeatureNameJSONTag.Value] = \
                    DateTimeHelper.get_datetime_tranformation_name(
                        int(value_str))
            elif feature_type == FeatureTypeRecognizer.Categorical or \
                feature_type == FeatureTypeRecognizer.Text or \
                    feature_type == FeatureTypeRecognizer.CategoricalHash:
                # If the raw feature type is Text or Categorical or
                # Categorical Hash, then set the value_str in the JSON
                if value_str != '':
                    transformation_json_data[
                        _FeatureNameJSONTag.Value] = value_str

            # Create the string for the engineered feature from the
            # transformation json obj
            engineered_feature_str = \
                transformation_json_data_obj_copy.\
                get_engineered_feature_name_from_json()

            # Add engineered feature name into the list
            self._engineered_feature_names.append(engineered_feature_str)

            # Add the JSON object for the engineered feature name into
            # the dictionary
            self._engineered_feature_name_json_objects[
                engineered_feature_str] = transformation_json_data

    def get_json_object_for_engineered_feature_name(self,
                                                    engineered_feature_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the JSON object for the given engineered feature name.

        :param engineered_feature_name: Engineered feature name for whom JSON string is required
        :return: JSON object for engineered feature name
        """
        # Look up the disctionary to see if the engineered
        # feature name exists.
        if engineered_feature_name not in \
                self._engineered_feature_name_json_objects:
            return None

        # Get the JSON object from the dictionary and return it
        return self._engineered_feature_name_json_objects[
            engineered_feature_name]


class FeatureNamesHelper:
    """Helper class for feature names."""

    @classmethod
    def get_regular_exp_for_parsing_raw_feature_names(cls) -> str:
        """
        Return the regular expression required for parsing the transformed feature names.

        :return: regex as string
        """
        return r"(\d+)(_?)(.*)"

    @classmethod
    def get_transformer_name(cls, transformer_number: int) -> str:
        """
        Return a string for transformer name which is added in the json representation of the transformations.

        :param transformer_number:
        :return: string
        """
        if transformer_number is None:
            raise ValueError("No transformer number was provided")

        if not isinstance(transformer_number, int):
            raise ValueError("The transformer number is not integer")

        return _MiscConstants.Transformer + str(transformer_number)


class _FeatureTransformersAsJSONObject:
    """Class to hold the JSON representation of the engineered feature name."""

    AllTransformationsType = Dict[str, Union[str, List[str]]]
    EntireTransformationType = Dict[str, Dict[str, Union[str, List[str]]]]

    def __init__(self):
        self._entire_transformation_json_data = {
            _FeatureNameJSONTag.FinalTransformerName: None,
            _FeatureNameJSONTag.Transformations: None,
            _FeatureNameJSONTag.Value: None
        }   # type: Dict[str, Optional[Any]]

        self._number_transformers = 0
        self._transformer_as_json = {}  # type: Dict[str, Optional[Any]]

    def _set_value_tag(self, value: str) -> None:
        """
        Set value in the feature transformer JSON object.

        :param value: Value to be set inside the feature transformer JSON object.
        :type value: str
        """
        self._entire_transformation_json_data[_FeatureNameJSONTag.Value] = value

    def _add_transformer_to_json(self, parent_feature_list=None,
                                 transformation_fnc=None,
                                 operator=None, feature_type=None,
                                 should_output=None):
        """
        Add a transformer to the JSON object.

        :param parent_feature_list:
        :param transformation_fnc:
        :param operator:
        :param feature_type:
        :param should_output:
        :return:
        """
        self._number_transformers += 1

        # Get the name for the current transformer
        current_transformer_name = FeatureNamesHelper.get_transformer_name(
            self._number_transformers)

        # Form the dictionary for the transformation details
        transformer_json_data = {
            _FeatureNameJSONTag.Input: parent_feature_list,
            _FeatureNameJSONTag.TransformationFunction: transformation_fnc,
            _FeatureNameJSONTag.Operator: operator,
            _FeatureNameJSONTag.FeatureType: feature_type,
            _FeatureNameJSONTag.ShouldOutput: should_output,
        }

        self._transformer_as_json[current_transformer_name] = \
            transformer_json_data

    def _compose_feature_transformers_as_json_obj(self):
        """Compose the JSON object from all the known transformations."""
        self._entire_transformation_json_data[
            _FeatureNameJSONTag.FinalTransformerName] = \
            FeatureNamesHelper.get_transformer_name(
                self._number_transformers)

        self._entire_transformation_json_data[
            _FeatureNameJSONTag.Transformations] = \
            self._transformer_as_json

    def __str__(self):
        """Return an engineered feature name string for the feature."""
        return self.get_engineered_feature_name_from_json()

    def get_engineered_feature_name_from_json(self):
        """
        Return the '_' separated string representation of the engineered feature.

        :return: string having '_' separated engineered feature name
        """
        # Call helper fucntion to get the engineered feature name with the
        # final transformer name
        complete_engineered_feature_name = \
            self._get_engineered_feature_name_from_json_internal(
                self._entire_transformation_json_data,
                self._entire_transformation_json_data[
                    _FeatureNameJSONTag.FinalTransformerName])

        # If there is value present in the json object, then append
        # it to the engineered feature name
        if self._entire_transformation_json_data[
                _FeatureNameJSONTag.Value] is not None:
            complete_engineered_feature_name += \
                '_' + self._entire_transformation_json_data[
                    _FeatureNameJSONTag.Value]

        # Return the complete string representation
        return complete_engineered_feature_name

    def _get_engineered_feature_name_from_json_internal(
            self, json_data, current_transformer_name):
        """
        Form the '_' separated string representation of the engineered feature recursively.

        :param json_data: json object for the engineered feature name
        :current_transformer_name: The current transformer name which needs to
                                   added to the engineered feature name
        :return: string having '_' separated engineered feature name
        """
        if current_transformer_name not in json_data[
                _FeatureNameJSONTag.Transformations]:
            # The base care is when the raw feature name happens to the
            # current transformer name. Return the current transformer name
            # as is.
            return current_transformer_name
        else:
            # Read the current transformer from the json object
            current_transformer = json_data[
                _FeatureNameJSONTag.Transformations][
                    current_transformer_name]

            # Recursively get engineered feature name for first input feature
            first_input_engineered_feature_name = \
                self._get_engineered_feature_name_from_json_internal(
                    json_data,
                    current_transformer[_FeatureNameJSONTag.Input][0])

            # Recursively get engineereds feature name for second
            # input feature
            second_input_engineered_feature_name = None
            if len(current_transformer[_FeatureNameJSONTag.Input]) > 1:
                second_input_engineered_feature_name = \
                    self._get_engineered_feature_name_from_json_internal(
                        json_data,
                        current_transformer[_FeatureNameJSONTag.Input][1])

            # Compose the '_' separated engineered feature name from both
            # the input features
            engineered_feature_name = first_input_engineered_feature_name
            if second_input_engineered_feature_name is not None:
                engineered_feature_name += \
                    '_' + second_input_engineered_feature_name

            if current_transformer[_FeatureNameJSONTag.ShouldOutput]:
                # If this transformer's transformation functions and operators
                # need to be added into the engineered feature, then
                # append them to the engineered feature name
                engineered_feature_name += '_'

                if current_transformer[
                        _FeatureNameJSONTag.Operator] is not None:
                    engineered_feature_name += \
                        current_transformer[_FeatureNameJSONTag.Operator]

                engineered_feature_name += \
                    current_transformer[
                        _FeatureNameJSONTag.TransformationFunction]

            # Return the engineered feature name
            return engineered_feature_name

    def _validate_transformation_json_object(self) -> None:
        """Validate if the JSON object has a valid schema."""
        # If the json object is None, then throw an exception
        if self._entire_transformation_json_data is None:
            raise ValueError(
                "No json object having transformations provided")

        # If there is no transformations key in the json object then
        # throw an exception
        if _FeatureNameJSONTag.Transformations not in \
                self._entire_transformation_json_data:
            raise ValueError("No transformations found in the json object")

    def is_feature_dropped(self) -> bool:
        """
        Return 'True' if a raw feature was dropped and not featurized otherwise 'False'.

        return: bool
        """
        # Check if the raw feature type is in dropped list
        return self.get_raw_feature_type() in FeatureTypeRecognizer.DROP_SET

    def get_transformation_input_feature_name(self) -> Optional[str]:
        """
        Get the raw feature name from the JSON object.

        If the input feature list is set of input features, then concatenate them and return.
        return: str
        """
        # Validate the JSON object
        self._validate_transformation_json_object()

        # Create the first transformer name
        first_transformer_name = FeatureNamesHelper.get_transformer_name(1)
        transformations = cast(_FeatureTransformersAsJSONObject.EntireTransformationType,
                               self._entire_transformation_json_data[_FeatureNameJSONTag.Transformations])
        if first_transformer_name in transformations:
            # Join and return all the input feature names
            raw_feature_name_list = transformations[first_transformer_name][_FeatureNameJSONTag.Input]
            return '-'.join(raw_feature_name_list)
        else:
            # If there is no first transformer present return None
            return None

    def get_all_transformations_as_str(self) -> str:
        """
        Aggregate all the transformers as a '-' separated string.

        return: str
        """
        all_transformer_list = []  # type: List[str]
        for index in range(1, self._number_transformers + 1):
            # Get the name for the current transformer
            current_transformer_name = FeatureNamesHelper.get_transformer_name(
                index)
            transformations = cast(_FeatureTransformersAsJSONObject.AllTransformationsType,
                                   self._entire_transformation_json_data[_FeatureNameJSONTag.Transformations])
            if current_transformer_name in transformations:
                current_transformer = cast(_FeatureTransformersAsJSONObject.AllTransformationsType,
                                           transformations[current_transformer_name])
                transformation_function = cast(str, current_transformer[
                                               _FeatureNameJSONTag.TransformationFunction])
                operator = cast(
                    str, current_transformer[_FeatureNameJSONTag.Operator])

                if current_transformer[_FeatureNameJSONTag.Operator] is None:
                    transformer_str = transformation_function
                else:
                    transformer_str = operator + transformation_function

                # Add the current transformer name to the list
                all_transformer_list.append(transformer_str)

        # Join all transformer names and return
        return '-'.join(all_transformer_list)

    def get_raw_feature_type(self) -> str:
        """
        Return a string for the type of raw feature inside the JSON object.

        :return: A string having the raw feature name (numeric, categorical etc.)
        """
        self._validate_transformation_json_object()

        # Iterate over all the transformations to find the feature type of
        # the raw feature
        transformations = cast(_FeatureTransformersAsJSONObject.EntireTransformationType,
                               self._entire_transformation_json_data[
                                   _FeatureNameJSONTag.Transformations])
        for transformer_key in transformations:
            transformer = transformations[transformer_key]

            if transformer[_FeatureNameJSONTag.FeatureType] is not None:
                if transformer[_FeatureNameJSONTag.FeatureType] not in \
                        list(FeatureTypeRecognizer.FULL_SET):
                    # If the raw feature type is found but it is not a
                    # recognized raw feature type, then raise exception
                    raise ValueError(
                        cast(str, transformer[_FeatureNameJSONTag.FeatureType]) +
                        " is not a supported feature type")

                # Return the raw feature type
                return cast(str, transformer[_FeatureNameJSONTag.FeatureType])

        # If no raw feature was found, then throw an exception
        raise ValueError(
            "No raw feature type was found in transformations json object")


class _FeatureTransformers:
    """This class forms a JSON object from the graph of transformers."""

    def __init__(self, graph_of_transformers):
        """
        Initialize this graph serializer.

        :param graph_of_transformers:
        """
        self._graph_of_transformers = graph_of_transformers
        self._feature_as_json = _FeatureTransformersAsJSONObject()

    def encode_transformations_from_list(self) -> _FeatureTransformersAsJSONObject:
        """
        Create a JSON object from the graph of transformers.

        :return: list
        """
        # The starting transformer number
        transformer_number = 1

        # Dictionary to know parent transformer name
        transformer_name_dict = {}  # type: Dict[str, str]

        # Iterate over all the transformers in the list
        for transformer in self._graph_of_transformers:

            # Input list for inputs to the current transformer
            input_list = []
            for parent_feature in transformer._parent_feature_list:

                if isinstance(parent_feature, int):
                    # It parent feature is a number, then get the transformer
                    # name from the dictionary. This means that the transformer
                    # depends on the previous transformer.
                    transformer_name = \
                        FeatureNamesHelper.get_transformer_name(
                            int(parent_feature))

                    if transformer_name not in transformer_name_dict:
                        raise ValueError(
                            "The transformer name " + transformer_name +
                            " not found")

                    # Add the input transformer name in the list
                    input_list.append(transformer_name)
                else:
                    # This is the case for raw feature name
                    input_list.append(parent_feature)

            self._feature_as_json._add_transformer_to_json(
                input_list, transformer._transformation_function,
                transformer._operator, transformer._feature_type,
                transformer._should_output)

            # Get the name for the current transformer
            current_transformer_name = \
                FeatureNamesHelper.get_transformer_name(
                    transformer_number)

            # Add the current transformer name
            transformer_name_dict[current_transformer_name] = \
                current_transformer_name

            # Increment the transformer number
            transformer_number += 1

        self._feature_as_json._compose_feature_transformers_as_json_obj()
        return self._feature_as_json


class _Transformer:
    """Concrete class to keep track of transformer details and operators."""

    def __init__(self, parent_feature_list=None, transformation_fnc=None,
                 operator=None, feature_type=None, should_output=None):
        self._parent_feature_list = parent_feature_list
        self._transformation_function = transformation_fnc
        self._operator = operator
        self._feature_type = feature_type
        self._should_output = should_output


class _TransformationFunctionNames:
    """Class for storing the different type of transformations in pre-processor."""

    Imputer = 'Imputer'
    StringCast = 'StringCast'
    DateTime = 'DateTime'
    CountVec = 'CountVec'
    Tf = 'Tf'
    NaiveBayes = 'NB'
    ImputationMarker = 'ImputationMarker'
    LabelEncoder = 'LabelEncoder'
    OneHotEncoder = 'OneHotEncoder'
    HashOneHotEncode = 'HashOneHotEncode'
    GrainMarker = 'GrainMarker'
    Lag = 'Lag'
    RollingWindow = 'RollingWindow'
    STLFeaturizer = 'STLFeaturizer'
    WordEmbedding = 'WordEmbedding'
    MiniBatchKMeans = 'MiniBatchKMeans'
    MaxAbsScaler = 'MaxAbsScaler'
    Drop = ''
    TargetEncoding = 'TargetEncoding'
    WoETargetEncoding = 'WoETargetEncoding'

    FULL_SET = {Imputer,
                StringCast,
                DateTime,
                CountVec,
                Tf,
                ImputationMarker,
                LabelEncoder,
                OneHotEncoder,
                HashOneHotEncode,
                GrainMarker,
                RollingWindow,
                Lag,
                STLFeaturizer,
                NaiveBayes,
                WordEmbedding,
                MiniBatchKMeans,
                MaxAbsScaler,
                Drop,
                TargetEncoding,
                WoETargetEncoding}


class _OperatorNames:
    """Class storing operator names for various transformations."""

    CharGram = 'CharGram'
    WordGram = 'WordGram'
    Mean = 'Mean'
    Mode = 'Mode'

    FULL_SET = {CharGram, WordGram, Mean, Mode}


class FeatureTypeRecognizer:
    """Class for storing the feature types that the pre-processor recognizes."""

    Numeric = 'Numeric'
    DateTime = 'DateTime'
    Categorical = 'Categorical'
    OneHotEncoder = 'OneHotEncoder'
    CategoricalHash = 'CategoricalHash'
    Text = 'Text'
    Hashes = 'Hashes'
    Ignore = 'Ignore'
    AllNan = 'AllNan'

    FULL_SET = {Numeric, DateTime, Categorical,
                CategoricalHash, Text, Hashes, Ignore, AllNan}

    # List of features types that are dropped and not featurized
    DROP_SET = {Hashes, Ignore, AllNan}


class DateTimeHelper:
    """Helper class for Datetime engineered feature transformations."""

    # List of all date time sub-feature names
    _datetime_sub_feature_names = ['Year',
                                   'Month',
                                   'Day',
                                   'DayOfWeek',
                                   'DayOfYear',
                                   'QuarterOfYear',
                                   'WeekOfMonth',
                                   'Hour',
                                   'Minute',
                                   'Second']

    @classmethod
    def get_datetime_tranformation_name(cls, index):
        """
        Return the date time sub-feature given an index value.

        param index: An index value which can reference the list elements of
                     _datetime_sub_feature_names
        return: string for the date time sub-feature
        """
        if index < 0 or index >= len(cls._datetime_sub_feature_names):
            raise ValueError(
                "Unsupported index passed for datetime sub-featuere")

        return cls._datetime_sub_feature_names[index]


class _FeatureNameJSONTag:
    """Class for JSON tags for engineered feature names."""

    Input = 'Input'
    TransformationFunction = 'TransformationFunction'
    Transformations = 'Transformations'
    Operator = 'Operator'
    FeatureType = 'FeatureType'
    ShouldOutput = 'ShouldOutput'
    Value = 'Value'
    FinalTransformerName = 'FinalTransformerName'

    FULL_SET = {Input,
                TransformationFunction,
                Transformations,
                Operator, FeatureType, ShouldOutput,
                Value, FinalTransformerName}


class _MiscConstants:
    """Class for storing the miscellaneous constants."""

    Transformer = 'Transformer'


class _RawFeatureFeaturizationInfo:
    """
    Expose the following information for white-boxing AutoML featurization.

    - Raw feature name
    - Number of engineered features formed out of this raw feature
    - Type detected
    - If feature was dropped
    - List of feature transformations for the raw feature

    The following schema design is used for storing information to white-box featurization:-
    {
        "FeatureName": string,
        "TypeDetected": string,
        'EngineeredFeatureCount': integer,
        "Dropped": string,
        “Tranformations”: List of transformations as string
    }
    """

    @classmethod
    def get_coalesced_raw_feature_featurization_mapping(
            self, raw_feature_featurization_dict: Dict[str, Any],
            engineered_feature_name_json_dict: Optional[Any] = None) -> FeaturizationSummaryType:
        """
        Return a summary for raw feature names as per the class description.

        :param raw_feature_featurization_dict: Execution plan for individual raw features as JSON object
        :param engineered_feature_name_json_dict: Engineered feature names as JSON objects
        :return: Featurization summary for the input features
        """
        # Contants
        Tranformations = 'Tranformations'
        EngineeredFeatureCount = 'EngineeredFeatureCount'
        RawFeatureName = 'RawFeatureName'
        TypeDetected = 'TypeDetected'
        Dropped = 'Dropped'

        coalesced_raw_feature_featurization_list = []  # type: FeaturizationSummaryType
        temp_summary = dict()  # type: Dict[str, Optional[Any]]
        num_engineered_feature_per_raw_feature = None

        # If enginnered feature names as JSON objects are available, create the summary of number
        # of engineered features per raw feature
        if engineered_feature_name_json_dict is not None:
            num_engineered_feature_per_raw_feature = self.create_raw_features_num_engineered_features_mapping(
                engineered_feature_name_json_dict)

        # Walk all the execution plan for the raw features
        for raw_feature_transformation_info in raw_feature_featurization_dict.values():

            # Get the raw feature name
            raw_feature_name = raw_feature_transformation_info.get_transformation_input_feature_name()

            if raw_feature_name is None:
                continue

            if raw_feature_name in temp_summary:
                # If raw feature is already seen, then add the transformation summary
                coalesced_raw_feature_featurization_mapping = cast(Dict[str, Any], temp_summary[
                    raw_feature_name])
                coalesced_raw_feature_featurization_mapping[Tranformations].append(
                    raw_feature_transformation_info.get_all_transformations_as_str())

                if num_engineered_feature_per_raw_feature is None:
                    # If engineered names aren't available like in case of time series, update the
                    # count of number of engineered features seen for this raw feature
                    coalesced_raw_feature_featurization_mapping['EngineeredFeatureCount'] += 1
            else:
                # Create a new dictionary entry and populate it
                coalesced_raw_feature_featurization_mapping = \
                    {RawFeatureName: raw_feature_name,
                     TypeDetected: raw_feature_transformation_info.get_raw_feature_type(),
                     Dropped: 'Yes' if raw_feature_transformation_info.is_feature_dropped() else 'No'}

                if num_engineered_feature_per_raw_feature is not None:
                    # If the engineered names are available, then look up the number engineered feature from
                    # the pre-computed stats
                    if num_engineered_feature_per_raw_feature.get(raw_feature_name) is not None:
                        coalesced_raw_feature_featurization_mapping[EngineeredFeatureCount] = \
                            num_engineered_feature_per_raw_feature.get(
                                raw_feature_name)
                    else:
                        # If the stat summary doesn't exists, then set the engineered feature count
                        # to zero
                        coalesced_raw_feature_featurization_mapping[EngineeredFeatureCount] = 0
                else:
                    coalesced_raw_feature_featurization_mapping[EngineeredFeatureCount] = 1

                # Get the transformation summary
                coalesced_raw_feature_featurization_mapping[Tranformations] = \
                    [raw_feature_transformation_info.get_all_transformations_as_str()]

                temp_summary[raw_feature_name] = coalesced_raw_feature_featurization_mapping

        coalesced_raw_feature_featurization_list = cast(
            FeaturizationSummaryType, list(temp_summary.values()))

        return coalesced_raw_feature_featurization_list

    @classmethod
    def create_raw_features_num_engineered_features_mapping(
            self, engineered_feature_name_json_dict: Any) -> Dict[str, int]:
        """
        Return a summary of number of engineered features create out of a raw feature.

        Takes a list of JSON objects for engineered feature names and returns a dictionary containing the
        raw feature name and the number of engineered feature names generated out of the raw feature.
        :param engineered_feature_name_json_dict: List of engineered feature names as JSON objects
        :return: Dictionary containing the summary of raw feature name and the number of engineered
                 features generated out of it.
        """
        raw_features_num_engineered_features_count = defaultdict(
            int)  # type: Dict[str, int]
        for engineered_feature_json in engineered_feature_name_json_dict.values():
            first_transformer_name = FeatureNamesHelper.get_transformer_name(1)
            if first_transformer_name in engineered_feature_json[_FeatureNameJSONTag.Transformations]:
                for raw_feature_name in engineered_feature_json[_FeatureNameJSONTag.Transformations][
                        first_transformer_name][_FeatureNameJSONTag.Input]:
                    # Sum all the enigneered feature names that were generated out this raw features
                    raw_features_num_engineered_features_count[raw_feature_name] += 1

        return raw_features_num_engineered_features_count
