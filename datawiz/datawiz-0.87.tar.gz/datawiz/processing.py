# Authors: Koye Sodipo <koye.sodipo@gmail.com>
# License: BSD 3 clause

import csv
import gc
from sklearn import preprocessing
from random import randint
from scipy import stats
from dateutil.parser import parse
import numpy
import pandas

# Two fundamental problems with determining whether 1st row is header:
# 1.) If all  elements (including the header) are numbers, code will think header is just any other data point
# 2.) If all elements (including the header) are strings, code will think
# header is just any othe data point. This can be solved if we assume the
# header title is unique to the entire column (i.e. occurs only once as
# header).


           
def is_datetime(arr):
        total = len(arr)
        accum = []
        for item in arr:
            item = str(item)
            if len(item) >= 6:  # parse() mistakes strings like '13', '3' etc for dates
                # print(item)
                try:
                    parse(item)
                    accum.append(1)
                except:
                    accum.append(0)

        if sum(accum) == total:
            return True
        else:
            return False
        
def prescribe(train_path=None,
            test_path=None,

            
            exclude_cols=[],
            data_has_ws = 0,
            
            
            pds_chunksize=0):
    
        file_path = train_path
        test_file_path = test_path
        
        use_numpy = False
        use_pandas = False
        use_list = False
        
        exclude_columns = exclude_cols
        data_has_whitespaces = data_has_ws
        pd_chunksize = pds_chunksize
        to_use = 'pandas'


        array = []
        array_test = []
        ans = -1
        accum = []
        header_or_not = []
        col_is_categorical = []
        col_is_numeric = []
        col_is_datetime = []
        col_low_info = []
        col_good_info = []
        header = []

        dt_array = []
        dt_array_test = []
        

        use_numpy = True if (
            to_use == 0 or to_use == 'numpy') else False
        use_pandas = True if (
            to_use == 1 or to_use == 'pandas') else False
        use_list = True if (
            to_use == 2 or to_use == 'list') else False

        if use_numpy:
            csv_iter = csv.reader(open(file_path, 'r'))
            data = [row for row in csv_iter]
            array = numpy.array(data)
            del data
            gc.collect()
            

        elif use_pandas:
            if pd_chunksize > 0:
                array = None
                for i, chunk in enumerate(pandas.read_csv(
                        file_path, chunksize=pd_chunksize, low_memory=False)):
                    if array is None:
                        array = chunk.copy()  # not simply a reference to it
                    else:
                        array = pandas.concat([array, chunk])
                    del chunk
                    gc.collect()

            else:
                try:
                    array = pandas.read_excel(file_path)
                except:
                    array = pandas.read_csv(file_path)
                    
        elif use_list:
            csv_iter = csv.reader(open(file_path, 'rb'))
            array = [row for row in csv_iter]
            

        ##########################################################################
        if isinstance(array, pandas.core.frame.DataFrame):

            try:
                rng = xrange(0, len(array.columns))
            except NameError:
                rng = range(0, len(array.columns))

            for column in rng:  # Test each column
                # initialize an array of 40 valid indexes to randomly sample in
                # a given column. We reset the first value of the array to 0 to
                # test the potential header row

                try:
                    test_value_types = [randint(1, len(array) - 1) for i in xrange(0, 41)]
                except NameError:
                    test_value_types = [randint(1, len(array) - 1) for i in range(0, 41)]

                test_value_types[0] = 0
                accum = []  # assumes labels are not integers
                for index in test_value_types:
                    try:
                        float(array.loc[index][column])
                        accum.append(1)
                    except ValueError:
                        accum.append(0)
                        

                # if first item in row is a string and the rest are numbers
                # (i.e. sum of accum falls short of 40), assume that's a
                # header.
                if isinstance(array.loc[0][column],str) and sum(accum) < 41 and sum(accum) > 0:
                    # This logic fails though, if the entire dataset is made of
                    # categorical strings and has NO headers. It will still
                    # assume 1st item is header regardless.
                    header_or_not.append(True)
                else:
                    header_or_not.append(False)

                # if the sum of 1s (instances where we found a number) is less
                # than 35, it's probably a categorical column
                if sum(accum) < 35:
                    col_is_categorical.append(True)

                else:
                    col_is_categorical.append(False)

                test_value_types.pop(0)
                col_name = array.columns[column]
                # if .loc[x][y], where x is not a single int index, y MUST be
                # the name of the column, not simply an index
                col_is_datetime.append(is_datetime(
                    array.loc[test_value_types][col_name]))

            # Here we decide whether or not the data has headers
            is_header = True if True in header_or_not else False

            if is_header:
                # convert the pandas columns that were incorrectly assumed to be strings (and are numbers) to numbers...
                #  Actually, this isn't necessary as the sklearn DT converts all strings to floats
                # if header, split header from data. Then detect categorical
                # columns. create label encoder for that
                ndata = array
            else:
                ndata = array
            
            # Handle missing values

            for index, column in enumerate(array.columns):
                if col_is_categorical[index] and col_is_datetime[index] is False:
                    # Remove whitespaces if option specified
                    if data_has_whitespaces == 1:
                        array[column] = array[column].str.strip()
                    no_of_unique = len(array[column].unique())
                    # if we have so many unique labels relative to the number
                    # of rows, it's probably a useless feature or an identifier
                    # (both usually) e.g. a name, ticket number, phone number,
                    # staff ID. More feature engineering usually required.
                    # Unsuprvised PCA perhaps.
                    if float(no_of_unique) / \
                            float(len(array[column])) > 0.25:
                        # ... also, even if we accidentally rule out a legitimate feature, the metric being > 0.25
                        #  would probably be a feature that'll cause overfitting
                        col_low_info.append(column)
                    else:
                        col_good_info.append(column)
                    
                    
        
        category_cols = list(array.columns[col_is_categorical])
        numeric_cols = list(array.columns[~array.columns.isin(category_cols)])
        datetime_cols = list(array.columns[col_is_datetime])
        print('Numerical   Cols:',numeric_cols,'\n',
              'Categorical Cols:',col_good_info,'\n',
              ' Date-Time  Cols:',datetime_cols,'\n',
              'Uninformative Cols:',col_low_info)
        
        return array, col_is_categorical, col_is_datetime, col_low_info, col_good_info

                    
def process(train_path=None,
            test_path=None,

            target_col=-99,
            exclude_cols=[],
            missing_values='fill',
            pds_chunksize=0,
            data_has_ws = True,
            advanced_ops=True,
            encode_categories=True,
            dt_convert=True,
            drop_low_info_cols=True   
            ):
    
        file_path = train_path
        test_file_path = test_path
        
        
        target_column = target_col
        exclude_columns = exclude_cols
        test_split = 0.2
        missing_vals = missing_values
        pd_chunksize = pds_chunksize

        to_use = 'pandas'
        dt_array = []
        encoders = []
        encoded_cols = []
        

        # Advanced Defult settings (not editable through arguments)

        # should the date parser consider the first number group ('09') in '09/12/2010' as the day?
        dayfirst = True

      

        array, col_is_categorical, col_is_datetime, col_low_info, col_good_info = prescribe(file_path)
        
            
        # Handle missing values
        if missing_vals == 'fill':
            for index, column in enumerate(array.columns):
                if col_is_categorical[index]:
                    mode = stats.mode(array.loc[:][column])[0][0]
                    array[column] = array[column].fillna(mode)
                else:                
                    try:
                        mean = numpy.mean(
                            array[column][
                                pandas.notnull(
                                    array[column])])
                        array[column] = array[column].fillna(mean)
                    except:
                        raise TypeError

        elif missing_vals == 'drop':
            array = array.dropna('rows')

        for index, column in enumerate(array.columns):
            if column in col_good_info and encode_categories == True:
                # convert to number labels using LabelEncode
                encoder = preprocessing.LabelEncoder()
                if data_has_ws == True:
                    array[column] = array[column].str.strip()
                encoder.fit(array[column])
                no_of_unique = len(encoder.classes_)
                # if we have so many unique labels relative to the number
                # of rows, it's probably a useless feature or an identifier
                # (both usually) e.g. a name, ticket number, phone number,
                # staff ID. More feature engineering usually required.
                # Unsuprvised PCA perhaps.
                if float(no_of_unique) / \
                        float(len(array[column])) > 0.25:
                    # ... also, even if we accidentally rule out a legitimate feature, the metric being > 0.25
                    #  would probably be a feature that'll cause overfitting
                    encoder = 'Category Not Relevant'
                    
                else:
                    # this back references and actually modifies array
                    array[column] = encoder.transform(array[column])
                # output of encoder.transform is a numpy.ndarray, FYI
                encoders.append(encoder)
                encoded_cols.append(column)
                # In test test, be sure to only transform where
                # col_is_categorical AND encoder != None i.e. 1st instance
                # of True in col_is_categorical checks ast index of
                # encoders array. 2nd checkeck 2nd etc..
 

            # Attach a datetime object for each column.
            if dt_convert == True:
                if col_is_datetime[index]:
                    # creates a list of pandas series containing class
                    # 'pandas.tslib.Timestamp' objects
                    dt_array.append(pandas.Series(
                        [parse(i, dayfirst=dayfirst) for i in array[column]]))

        # Get the pandas names of columns before removing target col. 1. to preserve index. 2. Pandas doesn't like
        # dealing with indexes. Prefers names
        col_names_excl = []

        if exclude_columns is not None:
            for ind in exclude_columns:
                col_names_excl.append(array.columns[ind])
            array = array.drop(columns=col_names_excl)
            
        if drop_low_info_cols:
            for col in col_low_info:
                col_names_excl.append(col)
            array = array.drop(columns=col_low_info)
            
            

        if target_column == -1:
            # .pop sometimes can't deal with -1 as an index
            target_column = len(array.columns) - 1
        Y = []
        if target_column != -99 and target_column is not None:
            Y = array.pop(array.columns[target_column])

      
        gc.collect()
        X = array

        is_processed = True
        return X, Y  # This is great because X is only a reference to the array object created outside of the function
        # Our previous setting of ndata to an index of array persists as a
        # global rule. If global array modified out of func, ndata, X changes
        # too.

def read_test(self):
    
    while True:
        ans_t = 1
        try:
            if test_file_path is None:
                test_file_path = input(
                    'Enter file path (surround with quotes)   :')
            break
        except:
            raise NameError

    # User can reset these by manipulating the class objects directly
    # before calling read_test()
    if use_numpy:
        csv_iter = csv.reader(open(test_file_path, 'rb'))
        data = [row for row in csv_iter]
        array_test = numpy.array(data)
        del data
        gc.collect()

    elif use_pandas:
        if pd_chunksize > 0:
            array_test = None
            for i, chunk in enumerate(
                    pandas.read_csv(
                        array_testtest_file_path, chunksize=pd_chunksize)):
                if array_test is None:
                    array_test = chunk.copy()  # not simply a reference to it
                else:
                    array_test = pandas.concat(
                        [array_test, chunk])
                del chunk
                gc.collect()

        else:
            array_test = pandas.read_csv(test_file_path)

    elif use_list:
        csv_iter = csv.reader(open(test_file_path, 'rb'))
        array_test = [row for row in csv_iter]
        


def process_test(self):
    # array to be returned (as a reference to array_test)
    X_test = array_test
    encoders_local = encoders
    tc = target_column if target_column != - \
        1 else len(encoders) - 1
    # Now encoders local should match test columns after we've popped the
    # encoder for the target column
    encoders_local.pop(tc)
    is_header = True if True in header_or_not else False
    adjusted_exclude_columns = []

    is_dt_local = col_is_datetime
    is_dt_local.pop(tc)

    for i in exclude_columns:
        if i < tc:
            adjusted_exclude_columns.append(i)
        if i > tc:  # Because if the target column was in the middle of the train array, the values provided for
            # excl_cols greater than indexof target col
            # ... need to be reduced by 1 since test array would already lacks the target column
            adjusted_exclude_columns.append(i - 1)
    print(len(encoders_local), len(encoders))
    for x in adjusted_exclude_columns:
        encoders_local[x] = 'Dont need this'
        is_dt_local[x] = False

    if isinstance(array_test, numpy.ndarray):
        if is_header:
            X_test = array_test[1:]
        else:
            q = None  # Completely useless atm. Feel we might need another case here in future

        try:
            rng = xrange(0, len(X_test[0, 0:]))
        except NameError:
            rng = range(0, len(X_test[0, 0:]))

        for column in rng:
            if column in adjusted_exclude_columns:  # no point processing columns we will later exclude
                continue

            # If column is categorical but also a datetime, don't convert it
            if not isinstance(encoders_local[column], str) and is_dt_local[column] is False:
                # convert to number labels using LabelEncode
                # print(column)
                if advanced_ops:  # remove leading or trailing spaces
                    X_test[:, column] = numpy.char.strip(X_test[:, column])
                # output of encoder.transform is a numpy.ndarray, FYI
                X_test[:, column] = encoders_local[column].transform(X_test[:, column], True)
            if dt_convert == 1:
                if is_dt_local[column]:
                    dt_array_test.append(numpy.array(
                        [parse(i, dayfirst=dayfirst) for i in X_test[:, column]]))

        array_of_col_index = [n for n in range(0, len(X_test[0]))]
        # Pick only the columns not listed to be excluded
        X_test = X_test[:, [i for i in array_of_col_index if (
            i not in adjusted_exclude_columns)]]

    if isinstance(array_test, pandas.core.frame.DataFrame):
        if is_header:
            X_test = array_test[1:]
        else:
            q = None

        # Handle missing values
        if missing_vals == 'fill' or missing_vals == 'drop':
            # Missing values shouldn't be dropped in the test set
            for index, column in enumerate(array_test.columns):
                if col_is_categorical[index]:
                    mode = stats.mode(X_test.loc[:][column])[0][0]
                    X_test[column] = X_test[column].fillna(mode)
                else:
                    mean = numpy.mean(
                        X_test[column][
                            pandas.notnull(
                                X_test[column])])
                    X_test[column] = X_test[column].fillna(mean)

        for index, column in enumerate(X_test.columns):
            if index in adjusted_exclude_columns:  # no point processing columns we will later exclude
                continue

            if not isinstance(
                    encoders_local[index],
                    str) and is_dt_local[index] is False:
                if advanced_ops:
                    X_test[column] = X_test[column].str.strip()
                # this back references and actually modifies the ooriginal
                # test.csv in memory
                X_test.loc[:][column] = encoders_local[
                    index].transform(X_test[column], True)
            # Attach a datetime object for each column.
            if dt_convert == 1:
                if col_is_datetime[index]:
                    dt_array_test.append(pandas.Series(
                        [parse(i, dayfirst=dayfirst) for i in X_test[column]]))

        for i in adjusted_exclude_columns:
            no_use = X_test.pop(i)

    print('len of enc local and dt_local ', len(encoders_local), len(is_dt_local))
    return X_test

"""def drop(self,cols):                        #arg "cols" can be a single index or array in indexes
    if not hasattr(self, "is_processed"):
        raise ValueError("datawiz array must be processed before dropping columns.")
    drop_indexes = []
    if type(cols)== int:
        drop_indexes.append(cols)
    else:
        drop_indexes = cols """



