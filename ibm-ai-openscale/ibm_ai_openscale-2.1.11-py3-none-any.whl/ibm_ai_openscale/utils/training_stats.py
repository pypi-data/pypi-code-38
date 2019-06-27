# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2019
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import types
import numpy as np
import pandas as pd
import collections
from collections import Counter
import math
import random
import numpy
import math
import datetime
import copy
import ast
import re
import logging

import traceback

from ibm_ai_openscale.utils import install_package

class TrainingStats():
    """
        Class to generate statistics related to training data. Following is the example on how the training_data_info param looks like
        :param training_data_frame: Dataframe comprising of input training data
        :type training_data_frame: DataFrame

        :param training_data_info: Input parameters needed for generating stats
        :type training_data_info:dict 

        Example:
        training_data_info = {
            "label_column": "Action",
            "feature_columns": ['Gender', 'Status', 'Children', 'Age', 'Customer_Status', 'Car_Owner', 'Customer_Service', 'Satisfaction', 'Business_Area'],
            "categorical_columns": ['Gender', 'Status', 'Customer_Status', 'Car_Owner', 'Customer_Service','Business_Area'],
            "fairness_inputs": {
                "fairness_attributes": [{
                                       "feature": "Gender",
                                       "majority": ['Male'],
                                       "minority": ['Female'],
                                       "threshold": 0.6
                                   },
                                   {
                                       "feature": "Children",
                                       "majority": [[0,1]],
                                       "minority": [[2,61]],
                                       "threshold": 0.6
                                   }
                                   ],
                "min_records" : 1000,
                "favourable_class" :  [ 'Voucher' ],
                "unfavourable_class": ['Free Upgrade', 'Premium features']
            },
            "problem_type" :"multiclass"
        }

        :param explain: Flag to enable or disable stats generation for explainability
        :param explain: Boolean (True by default)

        :param fairness: Flag to enable or disable stats generation for fairness
        :param fairness: Boolean (True by default)

        :param drop_na: Flag to drop NA values from input training data
        :param drop_na: Boolean (True by default)

    """

    def __init__(self, training_data_frame, training_data_info, explain = True, fairness = True, drop_na = True):
        initial_level = logging.getLogger().getEffectiveLevel()

        install_package("pyspark")
        install_package("sklearn")
        install_package("lime")
        updated_level = logging.getLogger().getEffectiveLevel()

        if initial_level != updated_level:
            logging.basicConfig(level=initial_level)
        
        self.training_data_frame = training_data_frame
        self.training_data_info = training_data_info
        self.compute_explain = explain
        self.compute_fairness = fairness
        self.drop_na = drop_na
        self.__validate_parameters()

        if self.drop_na:
            self.__drop_na_from_data_frame()


    def __drop_na_from_data_frame(self):
        self.training_data_frame.dropna(inplace=True)
        self.training_data_frame.reset_index(drop=True,inplace=True)

        
    def __validate_parameters(self):
        # Valudate training data frame
        if self.training_data_frame is None:
            raise Exception("training_data_frame cannot be None or empty")

        if self.training_data_info is None or self.training_data_info == {}:
            raise Exception("Missing training_data_info")

        self.__validate_training_data_info()
        return


    def __validate_training_data_info(self):
        """
            Validate input params to training stats method
        """
        self.fairness_inputs = None
        self.feature_columns = []
        self.categorical_columns = []
        
        #Set problem_type(aka model_type)
        self.problem_type = self.training_data_info.get("problem_type")
        accepted_problem_types = ["regression", "binary", "multiclass"]
        if self.problem_type not in accepted_problem_types:
            raise Exception(
                "Invalid/Missing problem type. Accepted values are:" + str(accepted_problem_types))

        # Set label column (aka class_label)
        self.label_column = self.training_data_info.get("label_column")
        if self.label_column is None or len(self.label_column) == 0:
            raise Exception("'label_column' cannot be empty")

        if self.compute_explain:    
            # Feature column checks
            self.feature_columns = self.training_data_info.get("feature_columns")
            if self.feature_columns is None or type(self.feature_columns) is not list or len(self.feature_columns) == 0:
                raise Exception("'feature_columns should be a non empty list")
    
            # Verify existence of feature columns in training data
            columns_from_data_frame = list(self.training_data_frame.columns.values)
            check_feature_column_existence = list(
                set(self.feature_columns) - set(columns_from_data_frame))
            if len(check_feature_column_existence) > 0:
                raise Exception("Feature columns missing in training data.Details:{}".format(
                    check_feature_column_existence))
    
            # Verify existence of label column in training data
            if self.label_column not in columns_from_data_frame:
                raise Exception("Label column '{}' is missing in training data.".format(self.label_column))

            # Categorical column checks
            self.categorical_columns = self.training_data_info.get("categorical_columns")
            if self.categorical_columns is not None and type(self.categorical_columns) is not list:
                raise Exception("'categorical_columns' should be a list of values")
    
            # Verify existence of  categorical columns in feature columns
            if self.categorical_columns is not None and len(self.categorical_columns) > 0:
                check_cat_col_existence = list(
                    set(self.categorical_columns) - set(self.feature_columns))
                if len(check_cat_col_existence) > 0:
                    raise Exception("'categorical_columns' should be subset of feature columns.Details:{}".format(
                        check_cat_col_existence))

        if self.compute_fairness:        
            # fairness_inputs Parameter check
            self.fairness_inputs = self.training_data_info.get("fairness_inputs")
            if self.fairness_inputs is None:
                raise Exception("'fairness_inputs' attribute is missing in the input")
    
            self.__validate_fairness_inputs()


   
    def __validate_fairness_inputs(self):
        """
           Validate fairness attributes
        """
        fairness_attributes = self.fairness_inputs.get("fairness_attributes")
        if fairness_attributes is None or len(fairness_attributes) == 0:
            raise Exception(
                "'fairness_attributes' attribute is either missing or has empty value under fairness_inputs")

        if self.problem_type != "regression":
            favourable_class = self.fairness_inputs.get("favourable_class")
            if (favourable_class is not None):
                if not (isinstance(favourable_class, (list, tuple))):
                    raise Exception("'favourable_class' in fairness_inputs must be a list of values")
                if isinstance(favourable_class[0], (list, tuple)):
                    raise Exception(
                        "'favourable_class' in fairness_inputs should not be a list of lists. It should be a list of values.")
            else:
                raise Exception("'favourable_class' attribute is required in fairness_inputs")

            unfavourable_class = self.fairness_inputs.get("unfavourable_class")
            if (unfavourable_class is not None):
                if not (isinstance(unfavourable_class, (list, tuple))):
                    raise Exception("'unfavourable_class' in fairness_inputs must be a list of values")
                if isinstance(unfavourable_class[0], (list, tuple)):
                    raise Exception(
                        "'unfavourable_class' in fairness_inputs should not be a list of lists. It should be a list of values.")
            else:
                raise Exception("'unfavourable_class' attribute is required in fairness_inputs")

        else:
            favourable_class = self.fairness_inputs.get("favourable_class")
            if (favourable_class is None):
                raise Exception(
                    "'favourable_class' attribute is required in fairness_inputs in case of regression model.")
            else:
                if not (isinstance(favourable_class[0], (list, tuple))):
                    raise Exception("'favourable class' in parametrs must be a list of lists")

            unfavourable_class = self.fairness_inputs.get("unfavourable_class")
            if (unfavourable_class is None):
                raise Exception(
                    "'unfavourable_class' attribute is required in fairness_inputs in case of regression model.")
            else:
                if not (isinstance(unfavourable_class[0], (list, tuple))):
                    raise Exception("'unfavourable class' in parametrs must be a list of lists")

        # Input validations
        fairness_attributes = self.fairness_inputs.get("fairness_attributes")
        if fairness_attributes is None:
            raise Exception("'fairness_attributes' attribute is missing under fairness_inputs")
        for fea in fairness_attributes:
            if "feature" not in fea:
                raise Exception("'feature' attributes is missing in 'fairness_attributes' input")
            if "majority" not in fea:
                raise Exception("'majority' attributes is missing in 'fairness_attributes' input")
            if "minority" not in fea:
                raise Exception("'minority' attributes is missing in 'fairness_attributes' input")

            self.__validate_feature(fea)


    

    def __validate_feature(self, feature):
        """
            Validate features for proper majorrity and majority values
        """
        feature_name = feature.get('feature')
        if feature_name is None or feature_name == '':
            error_msg = "Missing required field: You haven't specified the feature name."
            raise Exception(error_msg)
        majority = feature.get('majority')
        self.__validate_maj_min(feature_name, majority, 'majority')
        minority = feature.get('minority')
        self.__validate_maj_min(feature_name, minority, 'minority')
        for min_value in minority:
            # if attribute is categorical, same value can not be specified in both majority and minority
            if type(min_value) != type(majority[0]):
                error_msg = "Type mismatch: The data types of majority and minority for feature '{0}' are not matching.".format(
                    feature_name)
                raise Exception(error_msg)
            if isinstance(min_value, str):
                if min_value in majority:
                    error_msg = "Same value can not be specified as both majority and minority."
                    raise Exception(error_msg)
            else:
                min_start = min_value[0]
                min_end = min_value[1]
                for maj_value in majority:
                    maj_start = maj_value[0]
                    maj_end = maj_value[1]
                    if (min_start >= maj_start and min_start <= maj_end) or (
                            min_end >= maj_start and min_end <= maj_end) or (
                            maj_start >= min_start and maj_start <= min_end) or (
                            maj_end >= min_start and maj_end <= min_end):
                        error_msg = "The ranges you specified for the minority and majority values overlap."
                        raise Exception(error_msg)
        threshold = feature.get('threshold')
        self.__validate_threshold(feature_name, threshold)



    def __validate_numeric_attr(self, value, type, feature):
        """
            Validate ranges values
        """
        invalid_value = False
        if len(value) != 2:
            invalid_value = True
        if not invalid_value:
            for val in value:
                start = value[0]
                end = value[1]
                if start > end:
                    raise Exception(
                        "Invalid range: The numerical range for {0} value of the attribute '{1}' is incorrect, start value of range must be less than the end value.".format(
                            type, feature["feature"]))
        if invalid_value:
            error_msg = "Invalid syntax: The {0} value for the numerical attribute '{1}' must be specified as a list of ranges. Range format: [<begin_value>,<end_value>], Example: [[25,50],[60,75]]".format(
                type, feature)
            raise Exception(error_msg)

    def __validate_maj_min(self, feature_name, maj_min, type):
        if maj_min is None or maj_min == '' or maj_min == []:
            error_msg = "Missing required field: You haven't specified {0} value for the feature '{1}'.".format(type,
                                                                                                                feature_name)
            raise Exception(error_msg)
        if not isinstance(maj_min, list):
            error_msg = "Invalid syntax: The {0} value for feature '{1}' must be specified as a list of categorical values or numerical ranges.".format(
                type, feature_name)
            raise Exception(error_msg)
        for value in maj_min:
            if isinstance(value, list):
                self.__validate_numeric_attr(value, type, feature_name)
            elif not isinstance(value, str):
                error_msg = "Invalid syntax: The {0} value for feature '{1}' must be specified as a list of categorical values or numerical ranges.".format(
                    type, feature_name)
                raise Exception(error_msg)
            else:
                if value.strip() == '':
                    error_msg = "Value of {0} can not be empty.".format(type)
                    raise Exception(error_msg)

    def __validate_threshold(self, feature, threshold):
        if threshold is None or threshold == '':
            error_msg = "Missing required field: You haven't specified any threshold value for the feature '{0}'.".format(
                feature)
            raise Exception(error_msg)
        if not isinstance(threshold, float) and not isinstance(threshold, int):
            error_msg = "Invalid type: only numerical values are supported for threshold."
            raise Exception(error_msg)
        if threshold <= 0 or threshold > 1:
            error_msg = "The threshold value provided is invalid, it must be in range 0 < threshold <=1"
            raise Exception(error_msg)


    def __get_common_configuration(self):
        """
            Get common configuration details
        """
        common_configuration = {}
        common_configuration["problem_type"] = self.problem_type
        common_configuration["label_column"] = self.label_column
        
        try:
            input_data_schema = self.__generate_input_data_schema()
        except Exception as ex:
            raise Exception("Error generating input_data_schema.Reason:%s" %ex)

        common_configuration["input_data_schema"] = input_data_schema

        if self.compute_explain:
            common_configuration["feature_fields"] = self.feature_columns
            common_configuration["categorical_fields"] = self.categorical_columns
        return common_configuration

    # Generate training schema in spark structure
    def __generate_input_data_schema(self):
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.appName('pandasToSparkDF').getOrCreate()
        df = spark.createDataFrame(self.training_data_frame)
        sc = df.schema
        fields = []
        for f in sc:
            field = f.jsonValue()
            column = field["name"]

            if column in self.feature_columns:
                field["metadata"]["modeling_role"] = "feature"

                #Check for type and add to  categorical columns if not set by user
                if field["type"] == "string":
                    if self.categorical_columns is None:
                        self.categorical_columns = []

                    #Add entry to categorical column
                    if column not in self.categorical_columns and column != self.label_column:
                        self.categorical_columns.append(column)

                # Set categorical column in input schema
                if self.categorical_columns is not None:
                    if column in self.categorical_columns:
                        field["metadata"]["measure"] = "discrete"

            fields.append(field)

        training_data_schema = {}
        training_data_schema["type"] = "struct"
        training_data_schema["fields"] = fields

        return training_data_schema

    def __get_data_types(self, val):
        is_numeric = False
        is_int = False
        is_float = False
        try:
            float(val)
            is_numeric = True
            is_float = True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(val)
            is_numeric = True
            is_float = True
        except (TypeError, ValueError):
            pass

        try:
            int(val)
            is_numeric = True
            is_int = True
        except ValueError:
            pass

        return is_numeric, is_float, is_int

    def __getFrequencyTable(self, protected_attr_col, class_col):
        # Example:{Male: { class_outcome_1:28,class_outcome_2:29,class_outcome_3:50 }, Female: {class_outcome_1:28,class_outcome_2:29,class_outcome_3:50}}
        frequency_map = {}
        str_flag = False
        other_flag = False
        nan_num = 0
        for index, protected_attr_value in enumerate(protected_attr_col):

            # remove initial whitespaces
            if type(protected_attr_value) is str:
                protected_attr_value = protected_attr_value.lstrip()
            else:
                # remove nan
                if math.isnan(protected_attr_value):
                    nan_num = nan_num + 1
                    continue

            class_value = class_col[index]
            if type(class_value) is str:
                class_value = class_value.lstrip()
                if class_value.isdigit():
                    other_flag = True
                else:
                    str_flag = True
            else:
                # remove nan
                if math.isnan(class_value):
                    nan_num = nan_num + 1
                    continue
                else:
                    other_flag = True
            # Example is Yes
            # Update frequency table
            # checking if frequency map has value for this protected_attribute value. If Male already exists in the freq map
            if protected_attr_value in frequency_map:

                # get the dictionary for counts for different class values for this protected attribute value
                freq_count_dict = frequency_map[protected_attr_value]

                # check if this particular  counts for this particular class_value already exists: Example {Yes:50}
                if class_value in freq_count_dict:
                    counts_for_class_value = freq_count_dict[class_value]
                    counts_for_class_value = counts_for_class_value + 1

                    # Update counts for this particular class in the frequency count
                    freq_count_dict.update({class_value: counts_for_class_value})
                    # Update the final map of freq
                    frequency_map.update({protected_attr_value: freq_count_dict})
                else:
                    counts_for_class_value = 1
                    freq_count_dict.update({class_value: counts_for_class_value})
                    frequency_map.update({protected_attr_value: freq_count_dict})

            else:
                # This protected attribute does not exist in frequency map
                counts_for_class_value = 1
                freq_count_dict = {class_value: 1}
                frequency_map.update({protected_attr_value: freq_count_dict})

        return frequency_map

    def __modify_distribution(self, attributes_dataset, protected_attribute, class_dataset):

        extracted_column = attributes_dataset[protected_attribute].tolist()
        labels = class_dataset.tolist()
        frequency_map = self.__getFrequencyTable(extracted_column, labels)
        return frequency_map

    def __getDistribution(self, dataset, inputs):
        distribution_map = {}
        attributes_dataset = dataset[inputs['fairness_attributes']]
        class_dataset = dataset[inputs['class_label']]

        # Check if the class_label column is numerical or categorical
        class_labels = sorted(class_dataset.tolist())
        is_column_numeric = False
        count_numeric = 0
        row_num = class_dataset.shape[0]

        if row_num < 1000:
            sample_size = row_num
        else:
            sample_size = 1000

        for i in range(sample_size):
            class_label = class_labels[random.randint(0, row_num - 1)]
            is_numeric, is_float, is_int = self.__get_data_types(class_label)
            if is_numeric or is_float or is_int:
                count_numeric += 1

        if count_numeric > (sample_size - count_numeric):
            is_column_numeric = True

        # Get the additional info for class_label
        if is_numeric:
            min = class_labels[0]
            for pos in range(1, row_num):
                is_numeric, is_float, is_int = self.__get_data_types(class_labels[-pos])
                if is_numeric or is_float or is_int:
                    max = class_labels[-pos]
                    break
            distinct_class_label_list = [min, max]

        else:
            distinct_class_label_values = set()
            for class_label in class_labels:
                is_numeric, is_float, is_int = self.__get_data_types(class_label)
                if not (is_numeric or is_float or is_int):
                    distinct_class_label_values.add(class_label)
            distinct_class_label_list = list(distinct_class_label_values)

        for protected_attribute in inputs['fairness_attributes']:
            distribution_map[protected_attribute] = self.__modify_distribution(attributes_dataset, protected_attribute,
                                                                               class_dataset)

        return distribution_map, distinct_class_label_list

    # Compute BIAS training distribution
    def __computeTrainingDataDistribution(self):

        try:
            class_label = self.label_column
            fairness_attributes_list = []
            fairness_attributes = self.fairness_inputs.get("fairness_attributes")
            for fea in fairness_attributes:
                fairness_attributes_list.append(fea["feature"])

            fairness_params = {"class_label": class_label,
                               "fairness_attributes": fairness_attributes_list}
            data, distinct_class_label_values = self.__getDistribution(self.training_data_frame, fairness_params)

            data_frame, feature_data_types = self.__cleanPayloadData(self.training_data_frame, fairness_params)

            total_rows = data_frame.shape[0]
            
            distribution_data = []
            favourable_unfavourable_class = []
            if self.problem_type is not None and self.problem_type == "regression":

                favourable_class = self.fairness_inputs["favourable_class"]
                unfavourable_class = self.fairness_inputs["unfavourable_class"]
                # Combine the favourable and unfavourable ranges
                favourable_unfavourable_class.extend(self.fairness_inputs['favourable_class'])
                favourable_unfavourable_class.extend(self.fairness_inputs['unfavourable_class'])
                bucket_summation_data = self.get_buckets_for_training(data_frame,data,fairness_attributes,fairness_attributes_list,feature_data_types)
                distribution_data = self.__compute_regression_training_distribution(data, bucket_summation_data,fairness_attributes_list,
                                                                                    favourable_unfavourable_class,
                                                                                    feature_data_types)
            else:
                bucket_summation_data = self.get_buckets_for_training(data_frame,data,fairness_attributes,fairness_attributes_list,feature_data_types)
                distribution_data = self.__compute_training_distribution(data,bucket_summation_data,
                                                                         fairness_attributes, feature_data_types)

            distinct_class_label_feature = {}
            distinct_class_label_feature["attribute"] = fairness_params["class_label"]
            distinct_class_label_feature["is_class_label"] = True
            if self.problem_type is None or self.problem_type != "regression":
                temp = distinct_class_label_values[0]
                if type(temp) is int or type(temp) is float:
                    if (distinct_class_label_values[0] > distinct_class_label_values[1]):
                        distinct_class_label_feature["min"] = distinct_class_label_values[1]
                        distinct_class_label_feature["max"] = distinct_class_label_values[0]
                    else:
                        distinct_class_label_feature["min"] = distinct_class_label_values[0]
                        distinct_class_label_feature["max"] = distinct_class_label_values[1]
                else:
                    distinct_class_label_feature["distinct_values"] = distinct_class_label_values
            else:
                vList = []
                vList.extend(favourable_unfavourable_class)
                distinct_class_label_feature["distinct_values"] = vList

            distribution_data.append(distinct_class_label_feature)

            return distribution_data

        except Exception as exc:
            raise exc

    def __cleanPayloadData(self, payload_df, fairness_params):

        # Get the numerical/categorical percentage
        attributes_dataset = payload_df[fairness_params['fairness_attributes']]
        total_rows = payload_df.shape[0]
        feature_data_types = {}

        for protected_attribute in fairness_params['fairness_attributes']:
            row_num = payload_df.shape[0]
            protected_attribute_column = payload_df[protected_attribute].tolist()
            is_column_numeric = False
            count_numeric = 0

            for idx in range(row_num - 1):
                protected_attribute_column_value = protected_attribute_column[idx]
                is_numeric, is_float, is_int = self.__get_data_types(protected_attribute_column_value)
                if is_numeric or is_float or is_int:
                    count_numeric += 1

            # Clean the data
            if count_numeric >= (.98 * total_rows):
                indexes_to_drop = []
                for idx in range(row_num):
                    protected_attribute_column_value = attributes_dataset[protected_attribute][idx]
                    is_numeric, is_float, is_int = self.__get_data_types(protected_attribute_column_value)
                    if not (is_numeric or is_float or is_int):
                        indexes_to_drop.append(idx)

                feature_data_types[protected_attribute] = "numerical"
                payload_df = payload_df.drop(payload_df.index[indexes_to_drop])

            elif count_numeric <= (.02 * total_rows):
                indexes_to_drop = []
                for idx in range(row_num - 1):
                    protected_attribute_column_value = protected_attribute_column[idx]
                    is_numeric, is_float, is_int = self.__get_data_types(protected_attribute_column_value)
                    if is_numeric or is_float or is_int:
                        indexes_to_drop.append(idx)

                feature_data_types[protected_attribute] = "categorical"
                payload_df = payload_df.drop(payload_df.index[indexes_to_drop])

            else:
                raise Exception("Improper input data provided in " + protected_attribute + " column")

        return payload_df, feature_data_types

    
    # Compute training distribution regression model
    def __compute_regression_training_distribution(self, data,bucket_summation_data,fairness_attributes, favourable_classes,
                                                   feature_data_types):

        class_label = self.label_column
        fairness_params = {"class_label": self.label_column,
                           "fairness_attributes": fairness_attributes}
        sorted_data = {}
        bucket_size = 45 
        
        distribution_data = []
        distinct_data = {}
        for fairness_attribute in fairness_attributes[:]:
            keys = sorted(data[fairness_attribute].keys())
            is_numeric, is_float, is_int = self.__get_data_types(keys[0])

            if (feature_data_types[fairness_attribute] == "categorical"):
                is_float = is_int = is_numeric = False

            key_values = None
            min_value = None
            max_value = None
            if len(keys) > 0:
                if is_numeric:
                    if is_float:
                        key_values = sorted(list(map(float, keys)))
                    else:
                        key_values = sorted(list(map(int, keys)))

                    min_value = key_values[0]
                    max_value = key_values[len(key_values) - 1]

            if not is_numeric:
                distinct_data[fairness_attribute] = keys

            feature = {}
            feature["attribute"] = fairness_attribute
            if is_numeric is True:
                feature["min"] = min_value
                feature["max"] = max_value
            else:
                feature["distinct_values"] = keys

            class_label_values = []

            if not is_numeric:
                for key1, value1 in sorted(data[fairness_attribute].items()):
                    value_array = {}
                    value_array["label"] = key1
                    sortedValues = sorted(value1.items())
                    ranges = {}
                    for listValue in favourable_classes[:]:
                        ranges[tuple(listValue)] = 0

                    for key2, value2 in sortedValues:
                        for rKey, rValue in ranges.items():
                            range_start = rKey[0]
                            range_end = rKey[1]
                            if key2 >= range_start and key2 <= range_end:
                                ranges[rKey] = ranges[rKey] + 1
                                break
                    range_items = ranges.items()
                    range_to_delete = []
                    for k, v in range_items:
                        if ranges[k] == 0:
                            range_to_delete.append(k)
                    for x in range_to_delete[:]:
                        del ranges[x]
                    a = []
                    for rng, cnt in ranges.items():
                        b = {}
                        b["class_value"] = str(list(rng))
                        b["count"] = cnt
                        a.append(b)
                    value_array["counts"] = a
                    class_label_values.append(value_array) 
            else:
                    bucket_data = None
                    if fairness_attribute in bucket_summation_data and len(keys) > bucket_size:
                        bucket_data = bucket_summation_data[fairness_attribute]
                    else:
                        bucket_data = data[fairness_attribute]

                    for key, value in bucket_data.items():
                        value_array = {}
                        # value_array["label"] = key
                        value_array["label"] = key
                        a = []
                        for key2, value2 in sorted(value.items()):
                            b = {}
                            b["class_value"] = key2
                            b["count"] = value2
                            a.append(b)
                        value_array["counts"] = a
                        class_label_values.append(value_array)
            feature["class_labels"] = class_label_values
            distribution_data.append(feature)

        return distribution_data

    # Compute 50 buckets based on the majority and minority
    def __get_boundaries(self, majority, minority, data_type, bucket_size, feature_min, feature_max, round_value):
        values = {}
        boundaries = []
        if data_type is not None:
            for major in majority[:]:
                for maj in major[:]:
                    values[maj] = maj
            for minor in minority[:]:
                for min in minor[:]:
                    values[min] = min
            
            values[feature_min] = feature_min
            values[feature_max] = feature_max        
            sorted_values = sorted(values.values())

            min = sorted_values[0]
            max = sorted_values[-1]
            diff = max - min

            range_cnt = diff / bucket_size
            range = None

            if not data_type is None and data_type == "int":
                range = math.ceil(range_cnt)
            else:
                range = self.__truncate(range_cnt, round_value)
                
            # IF individual bucket range is 0 (should be atleast 1) then return empty boundaries    
            if range == 0:
                return boundaries    
            temp = min
            distribution = {}
            output = {}
            start = min
            end = max

            # Create the initial boundaries
            length_sorted_values = len(sorted_values)
            idx = 0

            if not data_type is None and data_type == "int":
                next_start = temp
            else:
                next_start = self.__truncate(temp, round_value)

            while temp <= max:
                # start = round(temp,1)
                if not data_type is None and data_type == "int":
                    start = next_start
                    end = temp + range

                    if (idx < (length_sorted_values)):

                        if (sorted_values[idx] == end):
                            idx += 1
                            next_start = temp + range
                            boundary = [start, end]
                            boundaries.append(boundary)
                            temp = temp + range

                        elif (sorted_values[idx] == start):
                            idx += 1
                            while (sorted_values[idx] < end):
                                boundary = [start, sorted_values[idx]]
                                boundaries.append(boundary)
                                start = sorted_values[idx]
                                idx += 1

                            next_start = temp + range
                            temp = temp + range
                            boundary = [start, end]
                            boundaries.append(boundary)

                        elif (sorted_values[idx] >= start and sorted_values[idx] <= end):
                            while (idx < len(sorted_values) and sorted_values[idx] < end):
                                start_diff = sorted_values[idx] - start
                                end_diff = end - sorted_values[idx]

                                if start_diff > end_diff:
                                    boundary = [start, sorted_values[idx]]
                                    boundaries.append(boundary)
                                    start = sorted_values[idx]
                                    idx += 1

                                else:
                                    boundary = [start, sorted_values[idx]]
                                    boundaries.append(boundary)
                                    start = sorted_values[idx]
                                    idx += 1

                            next_start = temp + range
                            temp = temp + range
                            boundary = [start, end]
                            boundaries.append(boundary)

                        else:
                            next_start = temp + range
                            boundary = [start, end]
                            boundaries.append(boundary)
                            temp = temp + range

                    else:
                        next_start = temp + range
                        boundary = [start, end]
                        boundaries.append(boundary)
                        temp = temp + range

                else:
                    start = next_start
                    end = self.__truncate(temp + range, round_value)

                    if (idx < (length_sorted_values)):
                        sorted_value = self.__truncate(sorted_values[idx], round_value)

                        if (sorted_value == end):
                            idx += 1
                            next_start = self.__truncate(temp + range, round_value)
                            boundary = [start, end]
                            boundaries.append(boundary)
                            temp = temp + range

                        elif (sorted_value == start):
                            idx += 1
                            if (idx < length_sorted_values):
                                sorted_value = self.__truncate(sorted_values[idx], round_value)
                                while (sorted_value < end and idx < len(sorted_values)):
                                    boundary = [start, sorted_value]
                                    boundaries.append(boundary)
                                    start = sorted_value
                                    idx += 1
                                    if (idx < length_sorted_values):
                                        sorted_value = self.__truncate(sorted_values[idx], round_value)

                            next_start = self.__truncate(temp + range, round_value)
                            temp = temp + range
                            boundary = [start, end]
                            boundaries.append(boundary)

                        elif (sorted_value >= start and sorted_value <= end):
                            while (sorted_value < end and idx < len(sorted_values)):
                                start_diff = sorted_value - start
                                end_diff = end - sorted_value

                                if start_diff > end_diff:
                                    boundary = [start, sorted_value]
                                    boundaries.append(boundary)
                                    start = sorted_value
                                    idx += 1
                                    if (idx < length_sorted_values):
                                        sorted_value = self.__truncate(sorted_values[idx], round_value)

                                else:
                                    boundary = [start, sorted_value]
                                    boundaries.append(boundary)
                                    start = sorted_value
                                    idx += 1
                                    if (idx < len(sorted_values)):
                                        sorted_value = self.__truncate(sorted_values[idx], round_value)

                            next_start = self.__truncate(temp + range, round_value)
                            temp = temp + range
                            boundary = [start, end]
                            boundaries.append(boundary)

                        else:
                            next_start = self.__truncate(temp + range, round_value)
                            boundary = [start, end]
                            boundaries.append(boundary)
                            temp = temp + range

                    else:
                        next_start = self.__truncate(temp + range, round_value)
                        boundary = [start, end]
                        boundaries.append(boundary)
                        temp = temp + range

        return boundaries

    def __getDistinctValues(self, dataset, inputs):

        distinct_values_sync = {}
        attributes_dataset = dataset[inputs['fairness_attributes']]

        for protected_attribute in inputs['fairness_attributes']:

            protected_attribute_column = attributes_dataset[protected_attribute].tolist()
            is_column_numeric = False
            count_numeric = 0
            row_num = attributes_dataset[protected_attribute].shape[0]

            if row_num < 1000:
                sample_size = row_num
            else:
                sample_size = 1000

            for i in range(sample_size):
                protected_attribute_column_value = protected_attribute_column[random.randint(0, row_num - 1)]
                is_numeric, is_float, is_int = self.__get_data_types(protected_attribute_column_value)
                if is_numeric or is_float or is_int:
                    count_numeric += 1

            if count_numeric > sample_size / 2:
                is_column_numeric = True

            protected_attribute_column_sorted = self.__custom_sorted(protected_attribute_column)

            if is_column_numeric:
                min = protected_attribute_column_sorted[0]
                for pos in range(1, row_num):
                    is_numeric, is_float, is_int = self.__get_data_types(protected_attribute_column_sorted[-pos])
                    if is_numeric or is_float or is_int:
                        max = protected_attribute_column_sorted[-pos]
                        break
                distinct_protected_attribute_column = [min, max]
                distinct_values_sync[protected_attribute] = distinct_protected_attribute_column

            else:
                distinct_protected_attribute_column = set()
                for attribute_value in protected_attribute_column_sorted:
                    is_numeric, is_float, is_int = self.__get_data_types(attribute_value)
                    if not (is_numeric or is_float or is_int):
                        distinct_protected_attribute_column.add(attribute_value)

                distinct_values_sync[protected_attribute] = list(distinct_protected_attribute_column)

        return distinct_values_sync

    def __truncate(self, float_value, number_of_digits):
        return math.floor(float_value * 10 ** number_of_digits) / 10 ** number_of_digits

    def __custom_sorted(self, l):
        try:
            convert = lambda text: int(text) if text.isdigit() else text
            alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
            return sorted(l, key=alphanum_key)
        except:
            return sorted(l)

            # Compute training distribution for binary and multiclass model

    def __compute_training_distribution(self,data,bucket_summation_data,fairness_attribute,feature_data_types):

        class_label = self.label_column
        fairness_attributes_list = []
        fairness_attributes = self.fairness_inputs.get("fairness_attributes")
        for fea in fairness_attributes:
            fairness_attributes_list.append(fea["feature"])

        fairness_params = {"class_label": self.label_column,
                           "fairness_attributes": fairness_attributes_list}

        sorted_data = {}
        # For each feature (if available) generate the initial set of boundaries
        bucket_size = 45 # Will nnd up creating max of 50 buckets or based on the adjustment we do to handle majority/minority ranges in the bucket.
        
        distribution_data = []
        distinct_data = {}

        # Build the json
        for fairness_attribute in fairness_params["fairness_attributes"]:

            keys = sorted(data[fairness_attribute].keys())

            min = None
            max = None

            is_numeric, is_float, is_int = self.__get_data_types(keys[0])

            if (feature_data_types[fairness_attribute] == "categorical"):
                is_float = is_int = is_numeric = False

            key_values = None
            if len(keys) > 0:
                if is_numeric:
                    if is_float:
                        key_values = sorted(list(map(float, keys)))
                    else:
                        key_values = sorted(list(map(int, keys)))

                    min = key_values[0]
                    max = key_values[len(key_values) - 1]

            feature = {}
            feature["attribute"] = fairness_attribute
            if is_numeric:
                feature["min"] = min
                feature["max"] = max
            else:
                feature["distinct_values"] = keys

            class_label_values = []
            if not is_numeric:
                for key1, value1 in sorted(data[fairness_attribute].items()):
                    value_array = {}
                    value_array["label"] = key1
                    # value_array["total_rows"] = total_rows

                    a = []
                    for key2, value2 in sorted(value1.items()):
                        b = {}
                        b["class_value"] = key2
                        b["count"] = value2
                        a.append(b)
                    value_array["counts"] = a
                    class_label_values.append(value_array)
            else:
                bucket_data = None
                if fairness_attribute in bucket_summation_data and len(keys) > bucket_size:
                    bucket_data = bucket_summation_data[fairness_attribute]
                else:
                    bucket_data = data[fairness_attribute]

                for key, value in bucket_data.items():
                    value_array = {}
                    # value_array["label"] = key
                    value_array["label"] = key
                    a = []
                    for key2, value2 in sorted(value.items()):
                        b = {}
                        b["class_value"] = key2
                        b["count"] = value2
                        a.append(b)
                    value_array["counts"] = a
                    class_label_values.append(value_array)

            feature["class_labels"] = class_label_values
            distribution_data.append(feature)

        return distribution_data

    # GET the fairness configution
    def __get_fairness_configuration(self):
        fairness_config_json = {}
        parameters_json = {}
        parameters_json["features"] = self.fairness_inputs["fairness_attributes"]

        parameters_json["favourable_class"] = self.fairness_inputs["favourable_class"]
        parameters_json["unfavourable_class"] = self.fairness_inputs["unfavourable_class"]
        parameters_json["min_records"] = self.fairness_inputs["min_records"]

        fairness_config_json["parameters"] = parameters_json
        fairness_config_json["distributions"] = self.__computeTrainingDataDistribution()

        return fairness_config_json


    # GET the explainability configution
    def __get_explanability_configuration(self):
        from sklearn.preprocessing import LabelEncoder
        from lime.discretize import QuartileDiscretizer
        
        try:
            data_df = self.training_data_frame
            if self.categorical_columns is None:
                self.categorical_columns = []
                
            numeric_columns = list(set(self.feature_columns) ^ set(self.categorical_columns))

            # Convert columns to numeric incase data frame read them as non-numeric
            data_df[numeric_columns] = data_df[numeric_columns].apply(
                pd.to_numeric, errors="coerce")

            # Drop rows with invalid values
            data_df.dropna(axis="index", subset=self.feature_columns, inplace=True)

            random_state = 10
            training_data_schema = list(data_df.columns.values)

            # Feature column index
            feature_column_index = [training_data_schema.index(x) for x in self.feature_columns]

            # Categorical columns index as per feature colums
            categorical_column_index = []
            categorical_column_index = [self.feature_columns.index(x) for x in self.categorical_columns]

            # numeric columns
            numeric_column_index = []
            for f_col_index in feature_column_index:
                index = feature_column_index.index(f_col_index)
                if index not in categorical_column_index:
                    numeric_column_index.append(index)

            # class labels
            class_labels = []
            if self.problem_type != "regression":
                if (self.label_column != None):
                    class_labels = data_df[self.label_column].unique()
                    class_labels = class_labels.tolist()

            # Filter feature columns from training data frames
            data_frame = data_df.values
            data_frame_features = data_frame[:, feature_column_index]

            # Compute stats on complete training data
            data_frame_num_features = data_frame_features[:, numeric_column_index]
            num_base_values = np.median(data_frame_num_features, axis=0)
            stds = np.std(data_frame_num_features, axis=0, dtype="float64")
            mins = np.min(data_frame_num_features, axis=0)
            maxs = np.max(data_frame_num_features, axis=0)

            main_base_values = {}
            main_cat_counts = {}
            if (len(categorical_column_index) > 0):
                for cat_col in categorical_column_index:
                    cat_col_value_counts = Counter(data_frame_features[:, cat_col])
                    values, frequencies = map(
                        list, zip(*(cat_col_value_counts.items())))
                    max_freq_index = frequencies.index(np.max(frequencies))
                    cat_base_value = values[max_freq_index]
                    main_base_values[cat_col] = cat_base_value
                    main_cat_counts[cat_col] = cat_col_value_counts

            num_feature_range = np.arange(len(numeric_column_index))
            main_stds = {}
            main_mins = {}
            main_maxs = {}
            for x in num_feature_range:
                index = numeric_column_index[x]
                main_base_values[index] = num_base_values[x]
                main_stds[index] = stds[x]
                main_mins[index] = mins[x]
                main_maxs[index] = maxs[x]

            # Encode categorical columns
            categorical_columns_encoding_mapping = {}
            for column_index_to_encode in categorical_column_index:
                le = LabelEncoder()
                le.fit(data_frame_features[:, column_index_to_encode])
                data_frame_features[:, column_index_to_encode] = le.transform(
                    data_frame_features[:, column_index_to_encode])
                categorical_columns_encoding_mapping[column_index_to_encode] = le.classes_

            # Compute training stats on descritized data
            descritizer = QuartileDiscretizer(
                data_frame_features, categorical_features=categorical_column_index, feature_names=self.feature_columns,
                labels=class_labels, random_state=random_state)

            d_means = descritizer.means
            d_stds = descritizer.stds
            d_mins = descritizer.mins
            d_maxs = descritizer.maxs
            d_bins = descritizer.bins(data_frame_features, labels=class_labels)

            # Compute feature values and frequencies of all columns
            cat_features = np.arange(data_frame_features.shape[1])
            discretized_training_data = descritizer.discretize(data_frame_features)

            feature_values = {}
            feature_frequencies = {}
            for feature in cat_features:
                column = discretized_training_data[:, feature]
                feature_count = collections.Counter(column)
                values, frequencies = map(list, zip(*(feature_count.items())))
                feature_values[feature] = values
                feature_frequencies[feature] = frequencies

            index = 0
            d_bins_revised = {}
            for bin in d_bins:
                d_bins_revised[numeric_column_index[index]] = bin.tolist()
                index = index + 1

            # Encode categorical columns
            cat_col_mapping = {}
            for column_index_to_encode in categorical_column_index:
                cat_col_encoding_mapping_value = categorical_columns_encoding_mapping[
                    column_index_to_encode]
                cat_col_mapping[column_index_to_encode] = cat_col_encoding_mapping_value.tolist(
                )
        except Exception as ex:
            print(ex.with_traceback)
            raise Exception("Error while generating explanability configuration.Reason:%s" % ex)

        # Construct stats
        data_stats = {}
        data_stats["feature_columns"] = self.feature_columns
        data_stats["categorical_columns"] = self.categorical_columns

        # Common
        data_stats["feature_values"] = feature_values
        data_stats["feature_frequencies"] = feature_frequencies
        data_stats["class_labels"] = class_labels
        data_stats["categorical_columns_encoding_mapping"] = cat_col_mapping

        # Descritizer
        data_stats["d_means"] = d_means
        data_stats["d_stds"] = d_stds
        data_stats["d_maxs"] = d_maxs
        data_stats["d_mins"] = d_mins
        data_stats["d_bins"] = d_bins_revised

        # Full data
        data_stats["base_values"] = main_base_values
        data_stats["stds"] = main_stds
        data_stats["mins"] = main_mins
        data_stats["maxs"] = main_maxs
        data_stats["categorical_counts"] = main_cat_counts

        # Convert to json
        explainability_configuration = {}
        for k in data_stats:
            key_details = data_stats.get(k)
            if (key_details is not None) and (not isinstance(key_details, list)):
                new_details = {}
                for key_in_details in key_details:
                    counter_details = key_details[key_in_details]
                    if isinstance(key_details[key_in_details],Counter):
                        counter_details = {}
                        for key,value in key_details[key_in_details].items():
                            counter_details[str(key)] = value
                    new_details[str(key_in_details)] = counter_details
            else:
                new_details = key_details
            explainability_configuration[k] = new_details

        exp_config_converted = self.__convert_numpy_int64(explainability_configuration)
        return exp_config_converted

    def __convert_numpy_int64(self,exp_config):
        try:
            for config in exp_config:
                config_details = exp_config.get(config)
                if isinstance(config_details,list):
                    for x in range(len(config_details)):
                        if isinstance(config_details[x],numpy.int64):
                            config_details[x] = int(config_details[x])
                elif isinstance(config_details,dict):
                    for key in config_details:
                        key_details = config_details.get(key)
                        if isinstance(key_details,list):
                            for x in range(len(key_details)):
                                if isinstance(key_details[x],numpy.int64):
                                    key_details[x] = np.asscalar(key_details[x])
                            config_details[key] = key_details
                        elif isinstance(key_details,numpy.int64):
                            config_details[key] = int(key_details)
                exp_config[config] = config_details
        except Exception as ex:
            raise Exception("Error while coverting numpy int64.Reason:%s" % ex)
        return exp_config

    def get_training_statistics(self):
        """
            Method to generate training data distribution
        """
        stats_configuration = {}
        
        common_config = self.__get_common_configuration()
        stats_configuration["common_configuration"] = common_config
        
        if self.compute_explain:
            explain_config = self.__get_explanability_configuration()
            stats_configuration["explainability_configuration"] = explain_config
            
        if self.compute_fairness:    
            fairness_config = self.__get_fairness_configuration()
            stats_configuration["fairness_configuration"] = fairness_config
        
        return stats_configuration

    def get_buckets_for_training(self, payload_df,data,feature_attributs,fairness_attributes_list,feature_data_types):
        sorted_data={}
        bucket_size = 45 
        fairness_params = {"class_label": self.label_column,
                           "fairness_attributes": fairness_attributes_list}
        # Will nnd up creating max of 50 buckets or based on the adjustment we do to handle majority/minority ranges in the bucket.

        #Setting the precision value for binning and truncating
        round_value = 2
        for fairness_attribute in fairness_attributes_list:
            for element in payload_df[fairness_attribute]:
                if type(element) == float:
                    if round_value < len(str(element).split('.')[1]):
                        round_value = len(str(element).split('.')[1])

        #Setting maximum precision to 5
        if round_value > 5:
            round_value = 5

        for feature in feature_attributs[:]:
            values = {}
            feature_name = feature["feature"]
            majority = feature["majority"]
            minority = feature["minority"]
            data_type = None

            if payload_df[feature_name].dtype == np.float64 or payload_df[feature_name].dtype == np.float32 or \
                            payload_df[feature_name].dtype == np.double or payload_df[
                feature_name].dtype == np.longdouble:
                data_type = "float"
            elif (payload_df[feature_name].dtype == np.int64 or payload_df[feature_name].dtype == np.int32):
                data_type = "int"

            if data_type is not None:

                for major in majority[:]:
                    for maj in major[:]:
                        values[maj] = maj
                for minor in minority[:]:
                    for min in minor[:]:
                        values[min] = min

                keys = sorted(data[feature_name].keys())

                is_numeric, is_float, is_int = self.__get_data_types(keys[0])

                if (feature_data_types[feature_name] == "categorical"):
                    is_float = is_int = is_numeric = False

                key_values = []
                if len(keys) > 0:
                    if is_numeric:
                        if is_float:
                            key_values = sorted(list(map(float, keys)))
                        else:
                            key_values = sorted(list(map(int, keys)))
                            # Don't create boundaries if distinct values are less than bucket_size
                if is_numeric and len(key_values) < bucket_size:
                    boundaries = []
                else:
                    feature_min = payload_df[feature_name].min()
                    feature_max = payload_df[feature_name].max()
                    boundaries = self.__get_boundaries(majority, minority, data_type, bucket_size, feature_min, feature_max, round_value)
                    

                sorted_values = sorted(values.values())

                feature_data = {}
                feature_data["sorted_values"] = sorted_values
                feature_data["boundaries"] = boundaries
                sorted_data[feature_name] = feature_data

        distribution_data = []
        distinct_data = {}
        bucket_data = {}

        # Combine all the count data under bucket as list for each fairness attributes if type is numeric ie int or float
        for fairness_attribute in fairness_params["fairness_attributes"]:
            keys = sorted(data[fairness_attribute].keys())

            is_numeric, is_float, is_int = self.__get_data_types(keys[0])

            if (feature_data_types[fairness_attribute] == "categorical"):
                is_float = is_int = is_numeric = False

            # No need to count data for non numeric type since buckets are for int and float datatype
            if not is_numeric:
                continue

            bucket_dict = {}
            boundaries = []
            if fairness_attribute in sorted_data:
                boundaries = sorted_data[fairness_attribute]["boundaries"]
                if len(boundaries) == 0:
                    continue
                least_min = boundaries[0][0]
                highest_max = boundaries[-1][1]
                for key1, value1 in sorted(data[fairness_attribute].items()):
                    idx = -1
                    val = ast.literal_eval(str(key1))
                    val = self.__truncate(val, round_value)
                    bucket = None
                    a = []

                    # Values less than the least minority value given as input
                    if (val < boundaries[0][0]):
                        if (least_min != boundaries[0][0]):
                            bucket = str(boundaries[0])
                            for key2, value2 in sorted(value1.items()):
                                b = {}
                                b["class_value"] = fkey2
                                b["count"] = value2
                                a.append(b)

                            existing_values = None
                            if bucket in bucket_dict:
                                existing_values = bucket_dict[bucket]
                                existing_values.extend(a)
                                del bucket_dict[bucket]
                                boundaries[0][0] = val
                                bucket = str(boundaries[0])
                                bucket_dict[bucket] = existing_values

                        else:
                            left_most_boundary_bucket = [val, least_min]
                            boundaries.insert(0, left_most_boundary_bucket)

                            bucket = str(boundaries[0])
                            for key2, value2 in sorted(value1.items()):
                                b = {}
                                b["class_value"] = key2
                                b["count"] = value2
                                a.append(b)

                            existing_values = None
                            if bucket in bucket_dict:
                                existing_values = bucket_dict[bucket]
                                existing_values.extend(a)
                                bucket_dict[bucket] = existing_values
                            else:
                                bucket_dict[bucket] = a
                                # Value found and corresponding buket has been inserted/modified so go to the next value
                        continue;

                    # Values greater than the highest majority value given as input
                    if (val > boundaries[-1][1]):
                        if (highest_max != boundaries[-1][1]):
                            bucket = str(boundaries[-1])
                            for key2, value2 in sorted(value1.items()):
                                b = {}
                                b["class_value"] = key2
                                b["count"] = value2
                                a.append(b)

                            existing_values = None
                            if bucket in bucket_dict:
                                existing_values = bucket_dict[bucket]
                                existing_values.extend(a)
                                del bucket_dict[bucket]
                                boundaries[-1][1] = val;
                                bucket = str(boundaries[-1])
                                bucket_dict[bucket] = existing_values

                        else:
                            right_most_boundary_bucket = [highest_max, val]
                            boundaries.append(right_most_boundary_bucket)

                            bucket = str(boundaries[-1])
                            for key2, value2 in sorted(value1.items()):
                                b = {}
                                b["class_value"] = key2
                                b["count"] = value2
                                a.append(b)

                            existing_values = None
                            if bucket in bucket_dict:
                                existing_values = bucket_dict[bucket]
                                existing_values.extend(a)
                                bucket_dict[bucket] = existing_values
                            else:
                                bucket_dict[bucket] = a
                        # Value found and corresponding buket has been inserted/modified so go to the next value
                        continue;

                    for boundary_bucket in boundaries[:]:
                        idx += 1
                        boundary_start = boundary_bucket[0]
                        boundary_end = boundary_bucket[1]
                        # fit the value in right boundary
                        if (val >= boundary_start and val <= boundary_end):
                            bucket = str(boundary_bucket)
                            for key2, value2 in sorted(value1.items()):
                                b = {}
                                b["class_value"] = key2
                                b["count"] = value2
                                a.append(b)

                            existing_values = None
                            if bucket in bucket_dict:
                                existing_values = bucket_dict[bucket]
                                existing_values.extend(a)
                                bucket_dict[bucket] = existing_values
                            else:
                                bucket_dict[bucket] = a
                            # Value fits in the bucket so break, no need to further loop through remaining buckets
                            break

                bucket_data[fairness_attribute] = bucket_dict

                # Sum up each of the bucket
        bucket_summation_data = {}
        for key, value in bucket_data.items():
            summation_array = {}
            for key1, value1 in value.items():
                bucket_data_count = {}
                for val in value1[:]:
                    class_value = val["class_value"]
                    count = val["count"]
                    if not class_value in bucket_data_count:
                        bucket_data_count[class_value] = count
                    else:
                        bucket_data_count[class_value] = bucket_data_count[class_value] + count
                summation_array[key1] = bucket_data_count
            bucket_summation_data[key] = summation_array
        return bucket_summation_data