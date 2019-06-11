#!/usr/bin/env python3
import pandas as pd
import numpy as np
import logging


def find_all_columns(csv_file, columns_to_exclude, range_fraction=0.1, separator=','):
    """
    Sometimes, csv files have way too many columns to make you want to list them all. This method will create
    a list of column objects for you, excluding whatever columns are in the columns_to_exclude_list.
    If columns are numeric/ranges acceptable range is set to 10 percent (range_fraction, modify if you want) of the
    average of the field. If you need more fine-grained control over this,
    :param csv_file: Full path to csv file.
    :param columns_to_exclude: List of column headers you DO NOT want Column objects created for.
    :param range_fraction: How much numeric columns can vary by, as a fraction of the mean of the column
    :param separator: Delimiter used by pandas when reading the report. Allows for parsing of .tsv ('\t' delimiter) as
    well as .csv (',' delimiter) files. Default is ','
    :return: List of column objects to be used by a Validator
    """
    column_list = list()
    df = pd.read_csv(csv_file, sep=separator)
    column_headers = list(df.columns)
    for column in column_headers:
        if column not in columns_to_exclude:
            # Check if column appears to be numeric
            if np.issubdtype(df[column].dtype, np.number):
                # Find average.
                average_column_value = df[column].mean()
                # Create column with acceptable range of plus/minus of range_fraction
                acceptable_range = average_column_value * range_fraction
                # Now finally create the column.
                column_list.append(Column(name=column,
                                          column_type='Range',
                                          acceptable_range=acceptable_range))
            else:
                column_list.append(Column(name=column))
    return column_list


def percent_depth_columns(csv_file, columns_to_exclude, percent_range, depth_range, separator=','):
    column_list = list()
    df = pd.read_csv(csv_file, sep=separator)
    column_headers = list(df.columns)
    for column in column_headers:
        if column not in columns_to_exclude:
            column_list.append(Column(name=column,
                                      column_type='Percent_Depth',
                                      percent_range=percent_range,
                                      depth_range=depth_range))
    return column_list


class Column(object):

    def __init__(self, name, column_type='Categorical', acceptable_range=None, percent_range=None, depth_range=None):
        self.name = name
        self.column_type = column_type
        self.acceptable_range = acceptable_range
        self.percent_range = percent_range
        self.depth_range = depth_range


class Validator(object):
    def __init__(self, reference_csv, test_csv, column_list, identifying_column, separator=','):
        self.identifying_column = identifying_column
        self.separator = separator
        self.reference_csv_df = pd.read_csv(reference_csv, sep=self.separator)
        self.test_csv_df = pd.read_csv(test_csv, sep=self.separator)
        self.column_list = column_list
        self.reference_headers = list(self.reference_csv_df.columns)
        self.test_headers = list(self.test_csv_df.columns)

    def remove_duplicate_header_rows(self):
        """
        Some genesippr reports (specifically mlst and rMLST) have multiple header-ish rows, which messes everything up.
        This will remove those rows from the df so that other methods can actually work.
        :return:
        """
        self.reference_csv_df = self.reference_csv_df[~self.reference_csv_df[
            self.identifying_column].isin([self.identifying_column])]
        self.test_csv_df = self.test_csv_df[~self.test_csv_df[self.identifying_column].isin([self.identifying_column])]

    def same_columns_in_ref_and_test(self):
        if set(self.reference_headers) != set(self.test_headers):
            return False
        else:
            return True

    def all_test_columns_in_ref_and_test(self):
        all_columns_present = True
        for column in self.column_list:
            if column.name not in self.reference_headers:
                logging.warning('{} was not found in Reference CSV.'.format(column.name))
                all_columns_present = False
            if column.name not in self.test_headers:
                logging.warning('{} was not found in Test CSV.'.format(column.name))
                all_columns_present = False
        return all_columns_present

    def check_samples_present(self):
        samples_in_ref = set(self.reference_csv_df[self.identifying_column])
        samples_in_test = set(self.test_csv_df[self.identifying_column])
        if samples_in_ref != samples_in_test:
            logging.warning('Not all samples in Test set are found in Reference set.')
            logging.warning('Samples in Test but not Reference: {}'.format(samples_in_test.difference(samples_in_ref)))
            logging.warning('Samples in Reference but not Test: {}'.format(samples_in_ref.difference(samples_in_test)))
            return False
        else:
            return True

    def check_columns_match(self):
        columns_match = True
        for testindex, testrow in self.test_csv_df.iterrows():
            for refindex, refrow in self.reference_csv_df.iterrows():
                if testrow[self.identifying_column] == refrow[self.identifying_column]:
                    for column in self.column_list:
                        if pd.isna(testrow[column.name]) and pd.isna(refrow[column.name]):
                            pass  # Equality doesn't work for na values in pandas, so have to check this first.
                        # Ensure that the value for the test and reference is not 'ND' before proceeding
                        elif testrow[column.name] == 'ND' and refrow[column.name] == 'ND':
                            pass
                        elif column.column_type == 'Categorical':
                            if testrow[column.name] != refrow[column.name]:
                                logging.warning('Attribute {} does not match for sample {}'
                                                .format(column.name,
                                                        testrow[self.identifying_column]))
                                columns_match = False
                        elif column.column_type == 'Range':
                            lower_bound = float(refrow[column.name]) - column.acceptable_range
                            upper_bound = float(refrow[column.name]) + column.acceptable_range
                            if not lower_bound <= float(testrow[column.name]) <= upper_bound:
                                logging.warning('Attribute {} is out of range for sample {}'
                                                .format(column.name,
                                                        testrow[self.identifying_column]))
                                columns_match = False

                        elif column.column_type == 'Percent_Depth':
                            test_percent = float(testrow[column.name].split()[0].replace('%', ''))
                            test_depth = float(testrow[column.name].split()[1].replace('(', ''))
                            ref_percent = float(refrow[column.name].split()[0].replace('%', ''))
                            ref_depth = float(refrow[column.name].split()[1].replace('(', ''))
                            upper_percent_bound = ref_percent + column.percent_range
                            lower_percent_bound = ref_percent - column.percent_range
                            upper_depth_bound = ref_depth + column.depth_range
                            lower_depth_bound = ref_depth - column.depth_range
                            if not lower_depth_bound <= test_depth <= upper_depth_bound:
                                logging.warning('Depth is out of range for column {} for sample {}'
                                                .format(column.name,
                                                        testrow[self.identifying_column]))
                                columns_match = False
                            if not lower_percent_bound <= test_percent <= upper_percent_bound:
                                logging.warning('Percent is out of range for column {} for sample {}'
                                                .format(column.name,
                                                        testrow[self.identifying_column]))
                                columns_match = False
        return columns_match

    def get_resfinderesque_dictionaries(self):
        current_id = '-999999999'
        # Test row dictionary is a dict, where key is an ID. Value for each ID is a list, with each index in the list as
        # a dictionary with column name as key and column value as value
        test_row_dict = dict()
        for testindex, testrow in self.test_csv_df.iterrows():
            # Check if current ID is none or equal to previous ID. If so, continue using that ID.
            # Otherwise, update the current ID to whatever it is.
            if testrow[self.identifying_column] == current_id:
                if testrow[self.identifying_column] not in test_row_dict:
                    test_row_dict[testrow[self.identifying_column]] = list()
            elif pd.isna(testrow[self.identifying_column]):
                testrow[self.identifying_column] = current_id
                if testrow[self.identifying_column] not in test_row_dict:
                    test_row_dict[testrow[self.identifying_column]] = list()
            else:
                current_id = testrow[self.identifying_column]
                if testrow[self.identifying_column] not in test_row_dict:
                    test_row_dict[testrow[self.identifying_column]] = list()
            # Now iterate through columns to create necessary dictionary.
            dict_to_append = dict()
            for column in self.column_list:
                dict_to_append[column.name] = testrow[column.name]
            test_row_dict[testrow[self.identifying_column]].append(dict_to_append)

        # Repeat process with reference info
        current_id = '-999999999'
        ref_row_dict = dict()
        for refindex, refrow in self.reference_csv_df.iterrows():
            # Check if current ID is none or equal to previous ID. If so, continue using that ID.
            # Otherwise, update the current ID to whatever it is.
            if refrow[self.identifying_column] == current_id:
                if refrow[self.identifying_column] not in test_row_dict:
                    test_row_dict[refrow[self.identifying_column]] = list()
            elif pd.isna(refrow[self.identifying_column]):
                refrow[self.identifying_column] = current_id
                if refrow[self.identifying_column] not in test_row_dict:
                    test_row_dict[refrow[self.identifying_column]] = list()
            else:
                current_id = refrow[self.identifying_column]
                if refrow[self.identifying_column] not in ref_row_dict:
                    ref_row_dict[refrow[self.identifying_column]] = list()
            # Now iterate through columns to create necessary dictionary.
            dict_to_append = dict()
            for column in self.column_list:
                dict_to_append[column.name] = refrow[column.name]
            ref_row_dict[refrow[self.identifying_column]].append(dict_to_append)
        return test_row_dict, ref_row_dict

    def get_one_to_one_resfinderesque_dictionaries(self):
        current_id = '-999999999'
        # Test row dictionary is a dict, where key is an ID. Value for each ID is a list, with each index in the list as
        # a dictionary with column name as key and column value as value
        test_row_dict = dict()
        for testindex, testrow in self.test_csv_df.iterrows():
            # Check if current ID is none or equal to previous ID. If so, continue using that ID.
            # Otherwise, update the current ID to whatever it is.
            if testrow[self.identifying_column] == current_id:
                if testrow[self.identifying_column] not in test_row_dict:
                    test_row_dict[testrow[self.identifying_column]] = list()
            elif pd.isna(testrow[self.identifying_column]):
                testrow[self.identifying_column] = current_id
                if testrow[self.identifying_column] not in test_row_dict:
                    test_row_dict[testrow[self.identifying_column]] = list()
            else:
                current_id = testrow[self.identifying_column]
                if testrow[self.identifying_column] not in test_row_dict:
                    test_row_dict[testrow[self.identifying_column]] = list()
            # Now iterate through columns to create necessary dictionary.
            dict_to_append = dict()
            for column in self.column_list:
                dict_to_append[column.name] = testrow[column.name]
            test_row_dict[testrow[self.identifying_column]].append(dict_to_append)

        # Repeat process with reference info
        current_id = '-999999999'
        ref_row_dict = dict()
        for refindex, refrow in self.reference_csv_df.iterrows():
            # Check if current ID is none or equal to previous ID. If so, continue using that ID.
            # Otherwise, update the current ID to whatever it is.
            if refrow[self.identifying_column] == current_id:
                if refrow[self.identifying_column] not in ref_row_dict:
                    ref_row_dict[refrow[self.identifying_column]] = list()
            elif pd.isna(refrow[self.identifying_column]):
                refrow[self.identifying_column] = current_id
                if refrow[self.identifying_column] not in ref_row_dict:
                    ref_row_dict[refrow[self.identifying_column]] = list()
            else:
                current_id = refrow[self.identifying_column]
                if refrow[self.identifying_column] not in ref_row_dict:
                    ref_row_dict[refrow[self.identifying_column]] = list()
            # Now iterate through columns to create necessary dictionary.
            dict_to_append = dict()
            for column in self.column_list:
                dict_to_append[column.name] = refrow[column.name]
            ref_row_dict[refrow[self.identifying_column]].append(dict_to_append)
        return test_row_dict, ref_row_dict

    def check_resfinderesque_output(self, one_to_one=False):
        """
        Genesippr's resfinder/virulence modules don't play nice with the standard column matching used in
        check_columns_match, which assumes that the identifying column only has one entry, whereas resfinder output
        has many genes per strain, and each gene gets its own row.
        To handle this, need to get all rows associated with each ID, and then 1) check that each ID has same number
        of entries in test and reference set and 2) sort the rows somehow in case they weren't already sorted, and then
        do row by row comparisons
        :return:
        """
        # First, get dictionaries. Each dict has identifying column names as keys, and then has a list as the value
        # for each. Each entry in each list is a dictionary where keys are column headers, and values are the column
        # values
        if one_to_one:
            test_row_dict, ref_row_dict = self.get_one_to_one_resfinderesque_dictionaries()
        else:
            test_row_dict, ref_row_dict = self.get_resfinderesque_dictionaries()
        checks_pass = True
        # Now check that all IDs are present in both test and reference.
        for identifier in test_row_dict:
            if identifier not in ref_row_dict:
                logging.warning('Identifier {} found in test but not reference.'.format(identifier))
                checks_pass = False
        for identifier in ref_row_dict:
            if identifier not in test_row_dict:
                logging.warning('Identifier {} found in reference but not test.'.format(identifier))
                checks_pass = False
        if checks_pass is False:
            return False

        # With that checked, check that each identifier has the same number of rows
        for identifier in test_row_dict:
            if len(test_row_dict[identifier]) != len(ref_row_dict[identifier]):
                logging.warning('Found {} entries in test set, but {} entries in reference set for {}'
                                .format(len(test_row_dict[identifier]),
                                        len(ref_row_dict[identifier]),
                                        identifier))
                checks_pass = False
        if checks_pass is False:
            return False

        # Now, if all identifiers have been found and the same number of identifiers are present for both ref and test,
        # check that the values actually work out.
        for identifier in test_row_dict:
            for i in range(len(test_row_dict[identifier])):
                for column in self.column_list:
                    if pd.isna(test_row_dict[identifier][i][column.name]) and \
                            pd.isna(ref_row_dict[identifier][i][column.name]):
                        pass  # Equality doesn't work for na values in pandas, so have to check this first.
                    elif column.column_type == 'Categorical':
                        if test_row_dict[identifier][i][column.name] != ref_row_dict[identifier][i][column.name]:
                            logging.warning('Attribute {} does not match for identifier {}'.format(column.name,
                                                                                                   identifier))
                            checks_pass = False
                    elif column.column_type == 'Range':
                        lower_bound = ref_row_dict[identifier][i][column.name] - column.acceptable_range
                        upper_bound = ref_row_dict[identifier][i][column.name] + column.acceptable_range
                        if not lower_bound <= test_row_dict[identifier][i][column.name] <= upper_bound:
                            logging.warning('Attribute {} is out of range for sample {}'
                                            .format(column.name,
                                                    identifier))
                            checks_pass = False

        return checks_pass
