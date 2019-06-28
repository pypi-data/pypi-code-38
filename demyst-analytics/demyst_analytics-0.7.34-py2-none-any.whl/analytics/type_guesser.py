import os
import csv
import sys
import pandas as pd
import pickle
import json
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.layers import Flatten
from keras.layers.embeddings import Embedding
from collections import Counter
from demyst.analytics.eprint import debug
import usaddress


def first_name_from_full_name(str):
    if str:
        split_name = str.split()
        if len(split_name) > 1:
            return split_name[0]
        else:
            return split_name
    else:
        return None

def last_name_from_full_name(str):
    if str:
        split_name = str.split()
        if len(split_name) > 1:
            return split_name[-1]
        else:
            return split_name
    else:
        return None


def parse_address(str):
    # can't use postal cause it's too hard to install :/
    parsed_addr = usaddress.parse(str)
    addr_dict = dict([ x[::-1] for x in parsed_addr])
    street = addr_dict.get('AddressNumber', "") + addr_dict.get('StreetName', "") + addr_dict.get('StreetNamePostType', "")
    city = addr_dict.get('PlaceName', None)
    state = addr_dict.get('StateName', None)
    postcode = addr_dict.get('ZipCode', None)
    return street, city, state, postcode

#def street_city_state_postcode(str):
#    # can't use postal cause it's too hard to install :/
#    from postal import parse_address
#    parsed_addr = parse_address(str)
#    addr_dict = dict([ x[::-1] for x in parsed_addr])
#    retval = [
#        addr_dict.get('house_number', "") + " " + addr_dict.get('road', ""),
#        addr_dict.get('city', ""),
#        addr_dict.get('state', ""),
#        addr_dict.get('postcode', "")
#    ]
#    return addr_dict.get('house_number', "") + " " + addr_dict.get('road', ""), addr_dict.get('city', ""), addr_dict.get('state', ""), addr_dict.get('postcode', "")




class TypeGuesser(object):

    def __init__(self, file_to_analyze=None):
        self.file_to_analyze = None
        self.found_delimiter = None

        if file_to_analyze is None:
            # do nothing ?
            pass
        elif isinstance(file_to_analyze, pd.DataFrame):
            # skip the delimiter finding etc.
            self.data = file_to_analyze
            pass
        else:
            debug("About to analyze", file_to_analyze)
            self.file_to_analyze = file_to_analyze
            self.find_delimiter()
            rows_to_read = 10
            # read in the rows with pandas, using the delimiter we discovered, skipping the first row since it might be a header row, and just read in the first 10 or so rows instead of the whole file
            self.data = pd.read_csv(self.file_to_analyze, delimiter=self.found_delimiter, nrows=rows_to_read, skiprows=1)


        ### Load up the model etc
        self.tokenizer = None
        self.model = None
        self.dummy_df = None
        self.max_length = None
        dirname = os.path.dirname(__file__)

        print("dirname:", dirname)

        tokenizer_path = os.path.join(dirname, 'tokenizer.pickle')
        print(tokenizer_path)
        with open(tokenizer_path, 'rb') as handle:
            self.tokenizer = pickle.load(handle)
        dummy_df_path = os.path.join(dirname, 'dummies.pickle')
        print(dummy_df_path)
        with open(dummy_df_path, 'rb') as handle:
            self.dummy_df = pickle.load(handle)
        max_length_path = os.path.join(dirname, 'max_length.pickle')
        print(max_length_path)
        with open(max_length_path, 'rb') as handle:
            self.max_length = pickle.load(handle)
        model_path = os.path.join(dirname, 'model.pickle')
        print(model_path)
        with open(model_path, 'rb') as handle:
            self.model = pickle.load(handle)

        debug("Found max_length of ", self.max_length)

        self.categories = self.dummy_df.columns.values
        debug("Categories are ", self.categories)
        self.columns_to_types = {}
        self.guessed_headers = []


    def find_delimiter(self):
        ### Load with pandas
        self.found_delimiter = None

        with open(self.file_to_analyze, 'r') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.readline(), delimiters=',|\t')
            self.found_delimiter = dialect.delimiter
            debug("File is delimited by", self.found_delimiter)
            return self.found_delimiter

    def guess_type(self, str):
        column_values = [ str ]
        encoded_texts = self.tokenizer.texts_to_matrix(column_values, mode='count')
        padded_texts = pad_sequences(encoded_texts, maxlen=self.max_length, padding='post', truncating='post')
        ynew = self.model.predict(padded_texts)
        idx = 0
        list_of_dicts = []
        for boogie in ynew:
            woogie = list(map(lambda x: round(x, 2), boogie))
            dict_of_categories_and_probabilities = dict(zip(self.categories, woogie))
            dict_with_only_high_probas = {k: v for k, v in dict_of_categories_and_probabilities.items() if v >= 0.01}
            list_of_dicts.append(dict_with_only_high_probas)
            debug("{:>50s}".format(column_values[idx]), dict_with_only_high_probas)
            idx += 1
        total = sum(map(Counter, list_of_dicts), Counter())
        N = float(len(list_of_dicts))
        average_of_categories = { k: v/N for k, v in total.items() }
        debug("Average of categories", average_of_categories)
        max_proba_key = max(average_of_categories, key=average_of_categories.get)
        debug(max_proba_key)
        return max_proba_key


    def sum_probabilities(self):
        ### Sum the probabilities for each column
        for ind, column_name in enumerate(self.data.columns):
            debug(" ****** Analyzing column", ind, "with column name", column_name, "******")
            column_values = self.data[column_name].astype(str).values
            encoded_texts = self.tokenizer.texts_to_matrix(column_values, mode='count')
            padded_texts = pad_sequences(encoded_texts, maxlen=self.max_length, padding='post', truncating='post')
            ynew = self.model.predict(padded_texts)
            idx = 0
            list_of_dicts = []
            for boogie in ynew:
                woogie = list(map(lambda x: round(x, 2), boogie))
                dict_of_categories_and_probabilities = dict(zip(self.categories, woogie))
                dict_with_only_high_probas = {k: v for k, v in dict_of_categories_and_probabilities.items() if v >= 0.01}
                list_of_dicts.append(dict_with_only_high_probas)
                debug("{:>50s}".format(column_values[idx]), dict_with_only_high_probas)
                idx += 1
            total = sum(map(Counter, list_of_dicts), Counter())
            N = float(len(list_of_dicts))
            average_of_categories = { k: v/N for k, v in total.items() }
            max_proba_key = max(average_of_categories, key=average_of_categories.get)
            self.columns_to_types[ind] = max_proba_key
            self.guessed_headers.append(max_proba_key)

            debug(" ****** With a probability of", round(average_of_categories[max_proba_key], 3), "we believe", max_proba_key, "is the type of column index", ind, 'name', column_name)
            debug(" ****** Average Probability of Categories", average_of_categories)
            debug("\n\n")


    def analyze(self):
        ### print out the results on stdout in a way other programs can consume
        self.sum_probabilities()
        self.previous_headers = self.data.columns
        self.data.columns = self.guessed_headers
        output = {
            "filename": self.file_to_analyze,
            "delimiter": self.found_delimiter,
            "columns_to_types": self.columns_to_types,
            "guessed_headers": self.guessed_headers,
            "previous_headers": self.previous_headers
        }
        return output


    def expand_columns(self):
        #        data = pd.read_csv(self.file_to_analyze, delimiter=self.found_delimiter, names=self.guessed_headers, header=None)
        data = self.data
        splittable_headers = set(['full_name', 'full_address'])
        columns_to_split = splittable_headers.intersection(set(self.guessed_headers))
        empty_df = pd.DataFrame()

        for header in columns_to_split:
            if header == 'full_name':
                empty_df['first_name'] = self.data['full_name'].apply(lambda x: first_name_from_full_name(x))
                empty_df['last_name'] = self.data['full_name'].apply(lambda x: last_name_from_full_name(x))
            if header == 'full_address':
                empty_df['street'], empty_df['city'], empty_df['state'], empty_df['postcode'] = zip(*data['full_address'].apply(parse_address))
        debug("empty df before dropna \n", empty_df.to_string())
        empty_df.dropna(inplace=True, axis='columns', how='all')
        debug("empty df after dropna \n", empty_df.to_string())
        all_together = pd.concat([data, empty_df], axis=1)
        cols = all_together.columns.to_list()
        cols.sort() # i can't believe this is in place and returns None what a trash language
        all_together = all_together[ cols ]
        # TODO: Make idempotent, de-duplicate
        self.data = all_together
